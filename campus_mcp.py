"""MCP del Campus Virtual UTN FRM. Credenciales en env: CAMPUS_USER, CAMPUS_PASS."""
import json, os, re, time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, unquote

import httpx
from mcp.server.mcpserver import MCPServer

BASE = "https://campusvirtual.frm.utn.edu.ar"
DESCARGAS = Path(os.environ.get("CAMPUS_DESCARGAS", Path.home() / "Downloads" / "campus"))

mcp = MCPServer("campus")
c = httpx.Client(follow_redirects=True, timeout=30)
sesskey = None


def login():
    global sesskey
    r = c.get(f"{BASE}/login/index.php")
    token = re.search(r'name="logintoken" value="([^"]+)"', r.text).group(1)
    r = c.post(f"{BASE}/login/index.php", data={
        "username": os.environ["CAMPUS_USER"],
        "password": os.environ["CAMPUS_PASS"],
        "logintoken": token,
        "anchor": "",
    })
    if "/login/index.php" in str(r.url):
        raise RuntimeError("Login falló: revisá CAMPUS_USER/CAMPUS_PASS")
    sesskey = re.search(r'"sesskey":"([^"]+)"', r.text).group(1)


def ajax(method, args, retry=True):
    if not sesskey:
        login()
    r = c.post(f"{BASE}/lib/ajax/service.php",
               params={"sesskey": sesskey, "info": method},
               json=[{"index": 0, "methodname": method, "args": args}])
    res = r.json()
    res = res[0] if isinstance(res, list) else res
    if res.get("error"):
        exc = res.get("exception") or res
        if retry and ("login" in str(exc.get("errorcode", "")) or "sesskey" in str(exc)):
            login()  # sesión vencida
            return ajax(method, args, retry=False)
        raise RuntimeError(exc.get("message", str(exc)))
    return res["data"]


def get(url):
    if not sesskey:
        login()
    r = c.get(urljoin(BASE, url))
    if "/login/index.php" in str(r.url):
        login()
        r = c.get(urljoin(BASE, url))
    return r


class _Texto(HTMLParser):
    """HTML -> texto plano, links como 'texto <url>'. Ignora menús/scripts."""
    SKIP = {"script", "style", "nav", "header", "footer", "noscript", "svg"}

    def __init__(self):
        super().__init__()
        self.out, self.skip, self.href = [], 0, None

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "a":
            self.href = dict(attrs).get("href")
        elif tag in ("p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4"):
            self.out.append("\n")
        elif tag in ("td", "th"):
            self.out.append(" | ")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag == "a" and self.href and not self.skip and self.href.startswith(BASE):
            self.out.append(f" <{self.href}>")
            self.href = None

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def texto(html):
    # ponytail: corta a la región principal de Moodle por regex; si el tema cambia, cae al HTML entero
    m = re.search(r'<div[^>]+id="region-main".*', html, re.S)
    p = _Texto()
    p.feed(m.group(0) if m else html)
    t = re.sub(r"[ \t]+", " ", "".join(p.out))
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def estado_curso(course_id):
    return json.loads(ajax("core_courseformat_get_state", {"courseid": course_id}))


def fecha(ts):
    return time.strftime("%d/%m/%Y %H:%M", time.localtime(ts))


@mcp.tool()
def materias() -> str:
    """Lista las materias en las que está inscripto el alumno (id y nombre)."""
    cursos = ajax("core_course_get_enrolled_courses_by_timeline_classification",
                  {"classification": "all", "limit": 0, "offset": 0, "sort": "fullname"})
    return "\n".join(f'{x["id"]}: {x["fullname"]}' for x in cursos["courses"])


@mcp.tool()
def contenido_materia(course_id: int) -> str:
    """Secciones y recursos (material, tareas, foros, links) de una materia, con su URL.
    Usar leer(url) para abrir cualquiera."""
    st = estado_curso(course_id)
    cms = {cm["id"]: cm for cm in st["cm"]}
    out = []
    for sec in st["section"]:
        out.append(f'\n## {sec.get("title") or sec.get("name") or "Sección " + str(sec.get("number"))}')
        for cid in sec.get("cmlist", []):
            cm = cms.get(cid) or cms.get(str(cid))
            if cm and cm.get("visible", True):
                out.append(f'- [{cm.get("module")}] {cm["name"]} <{cm.get("url", "")}>')
    return "\n".join(out).strip()


@mcp.tool()
def vencimientos(course_id: int = 0, cantidad: int = 30) -> str:
    """Próximas entregas/vencimientos pendientes (de todas las materias, o de una si se pasa course_id)."""
    if course_id:
        ev = ajax("core_calendar_get_action_events_by_course",
                  {"courseid": course_id, "timesortfrom": int(time.time()), "limitnum": cantidad})
    else:
        ev = ajax("core_calendar_get_action_events_by_timesort",
                  {"timesortfrom": int(time.time()), "limitnum": cantidad})
    lineas = [f'{fecha(e["timesort"])} | {e["course"]["shortname"]} | {e["name"]} <{e.get("url", "")}>'
              for e in ev["events"]]
    return "\n".join(lineas) or "No hay vencimientos próximos."


@mcp.tool()
def entregas(course_id: int) -> str:
    """Todas las tareas de una materia con fecha de entrega y estado de la entrega."""
    return texto(get(f"/mod/assign/index.php?id={course_id}").text)


@mcp.tool()
def avisos(course_id: int, cantidad: int = 5) -> str:
    """Últimos avisos (foro de novedades) de una materia, con el texto completo."""
    st = estado_curso(course_id)
    foros = [cm for cm in st["cm"] if cm.get("module") == "forum"]
    if not foros:
        return "La materia no tiene foros."
    # ponytail: asume que el foro de avisos es el primero del curso (Moodle lo crea así)
    html = get(foros[0]["url"]).text
    ids = list(dict.fromkeys(re.findall(r"discuss\.php\?d=(\d+)", html)))[:cantidad]
    if not ids:
        return f'{foros[0]["name"]}: sin avisos.'
    return f'# {foros[0]["name"]}\n\n' + "\n\n---\n\n".join(
        texto(get(f"/mod/forum/discuss.php?d={d}").text) for d in ids)


@mcp.tool()
def leer(url: str) -> str:
    """Abre cualquier URL del campus. Páginas -> texto. Archivos (PDF, docx, etc.) -> se descargan
    y devuelve la ruta local (leerla después con la herramienta de archivos)."""
    if not url.startswith(BASE) and not url.startswith("/"):
        return "Solo URLs del campus."
    r = get(url)
    if "text/html" in r.headers.get("content-type", ""):
        return texto(r.text)
    DESCARGAS.mkdir(parents=True, exist_ok=True)
    nombre = Path(unquote(str(r.url).split("?")[0])).name or "archivo"
    destino = DESCARGAS / nombre
    destino.write_bytes(r.content)
    return f"Descargado: {destino}"


if __name__ == "__main__":
    mcp.run()
