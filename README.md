# Campus UTN FRM — MCP

Servidor [MCP](https://modelcontextprotocol.io) para que Claude, ChatGPT, Gemini o cualquier IA entre al **Campus Virtual de la UTN FRM** con tu usuario. Con él podés preguntarle cosas como *"¿qué tengo que entregar esta semana?"* o *"resumime el último apunte de Física"* sin abrir el campus.

> ⚠️ Proyecto no oficial, hecho por estudiantes. No está afiliado a la UTN.

## Qué puede hacer

| Herramienta | Qué hace |
|---|---|
| `materias` | Lista las materias en las que estás inscripto, con su id |
| `contenido_materia` | Muestra las secciones de una materia y todos sus recursos (apuntes, tareas, foros, links) con su URL |
| `vencimientos` | Muestra las próximas entregas pendientes, de todas las materias o de una sola |
| `entregas` | Lista todas las tareas de una materia con fecha de entrega y estado (entregada / sin entregar / calificada) |
| `avisos` | Muestra los últimos avisos del foro de novedades de una materia, con el texto completo |
| `leer` | Abre cualquier URL del campus. Las páginas las devuelve como texto y los archivos (PDF, docx, ppt…) los descarga en tu compu |

No hace falta llamar a las herramientas a mano: le hablás a Claude normalmente y él decide cuáles usar.

## Ejemplos

**Qué tengo pendiente**
> ¿Qué entregas tengo en los próximos días?

```
03/11/2026 23:59 | AM2 | TP 3 - Integrales dobles vence
05/11/2026 18:00 | SyO | Cuestionario Unidad 4 cierra
10/11/2026 23:59 | Física II | Informe de laboratorio vence
```

**Avisos de una materia**
> ¿Hay avisos nuevos en Sistemas Operativos?

Claude busca el id de la materia con `materias` y después llama a `avisos`. Te devuelve los últimos avisos completos, con autor, fecha y texto (por ejemplo, cambios de horario o fechas de parcial).

**Estudiar con el material**
> Bajate el apunte de la unidad 2 de Análisis Matemático II y haceme un resumen.

Claude usa `contenido_materia` para encontrar el recurso y `leer` para descargar el PDF en `~/Downloads/campus/`. Después lo lee y te lo resume.

**Estado de las tareas**
> ¿Qué TPs me faltan entregar en Física II?

`entregas` trae la tabla de tareas de la materia con su estado.

**Más ideas**
- "¿Cuándo es el próximo parcial de cada materia?"
- "Armame un calendario de estudio con todos los vencimientos de noviembre."
- "Leé la consigna del TP 3 de AM2 y explicame qué piden."

## Instalación

Necesitás **Python 3.10+** y **git**.

```sh
git clone https://github.com/ignaw05/campus-utn-frm-mcp.git
cd campus-utn-frm-mcp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

En Windows usá `.venv\Scripts\pip` y `.venv\Scripts\python` en lugar de `.venv/bin/...`.

### Claude Code

Desde la carpeta del repo, reemplazá tu usuario y contraseña del campus:

```sh
claude mcp add campus --scope user \
  -e CAMPUS_USER=tu_usuario -e CAMPUS_PASS=tu_contraseña \
  -- "$(pwd)/.venv/bin/python" "$(pwd)/campus_mcp.py"
```

Reiniciá Claude Code y verificá con `/mcp` que `campus` aparezca conectado.

Si te equivocaste en algún dato:

```sh
claude mcp remove campus
```

y volvé a agregarlo.

### Claude Desktop

Editá el archivo de configuración:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "campus": {
      "command": "/ruta/completa/a/campus-utn-frm-mcp/.venv/bin/python",
      "args": ["/ruta/completa/a/campus-utn-frm-mcp/campus_mcp.py"],
      "env": {
        "CAMPUS_USER": "tu_usuario",
        "CAMPUS_PASS": "tu_contraseña"
      }
    }
  }
}
```

Reiniciá Claude Desktop.

### Configuración

| Variable | Obligatoria | Descripción |
|---|---|---|
| `CAMPUS_USER` | sí | Usuario del campus |
| `CAMPUS_PASS` | sí | Contraseña del campus |
| `CAMPUS_DESCARGAS` | no | Carpeta donde se guardan los archivos que baja `leer`. Por defecto es `~/Downloads/campus` |

## Privacidad y seguridad

- Tu usuario y contraseña quedan **solo en tu compu**, en la config de tu cliente MCP. El servidor corre localmente y solo se conecta a `campusvirtual.frm.utn.edu.ar`.
- No escribas tu contraseña en el chat con Claude. Ponela solo en la configuración.
- Es **solo lectura**: no entrega tareas, no publica en foros y no modifica nada.
- `leer` solo acepta URLs del campus.

## Problemas comunes

| Error | Solución |
|---|---|
| `Login falló` | Revisá `CAMPUS_USER` y `CAMPUS_PASS`. Probá entrar al campus desde el navegador con los mismos datos |
| `KeyError: 'CAMPUS_USER'` | Agregaste el MCP sin las variables. Borralo y volvé a agregarlo con `-e` |
| `campus` no aparece en `/mcp` | Revisá que las rutas a `.venv/bin/python` y a `campus_mcp.py` sean absolutas y existan |
| `avisos` muestra otro foro | Se asume que el primer foro de la materia es el de avisos. Usá `contenido_materia` y `leer` con la URL del foro correcto |

## Cómo funciona

El servidor hace login en el campus (Moodle) igual que el navegador y usa la API AJAX interna de Moodle (`/lib/ajax/service.php`) para las materias, el contenido y los vencimientos. Lo que no está en esa API (tareas, avisos y páginas en general) lo saca del HTML y lo convierte a texto. Todo el código está en un solo archivo: [`campus_mcp.py`](campus_mcp.py).

## Contribuir

Se aceptan issues y PRs. Si el campus cambia algo y se rompe una herramienta, abrí un issue con el mensaje de error.
