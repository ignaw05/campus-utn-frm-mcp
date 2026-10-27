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

Estas respuestas son conversaciones reales con Claude Code.

### Bajar el material de una unidad

> Podés pasarme los archivos de las unidades 4 y 5 de Informática Industrial?

Claude usa `materias` para encontrar la materia, `contenido_materia` para ubicar los recursos y `leer` para descargarlos:

```
Descargué los 4 PDFs en ~/Downloads/campus/ y abren bien:

Unidad 4: Planificación y Programación de la Producción
- Apuntes de clase: Unidad_4_Produccion_Apunte.pdf (16 págs)
- Presentación: U4_Planificacion_Produccion_Teoria.pdf (24 págs)

Unidad 5: Control de Gestión y Business Intelligence
- Apuntes de clase: Unidad_5_Control_de_Gestion_Apunte.pdf (16 págs)
- Presentación: Unidad_5_Control_de_Gestion_Teoria.pdf (16 págs)
```

Después podés seguir con *"resumime el apunte de la unidad 4"* o *"haceme preguntas de repaso de la unidad 5"*.

### Fechas de parciales

> Cuándo es el segundo parcial de Ciencia de Datos?

Claude lee la página "Calendario y entregas" de la materia y los avisos, y cruza la información:

```
El Parcial 2 de Ciencia de Datos es el miércoles 4/11 (clase 12), según la
página "Calendario y entregas" del campus.

- Temas: Unidad 3 (Machine Learning, supervisado y no supervisado) y
  Unidad 4 (Visualización con Altair).
- Horario: todavía no se publicó. Para el Parcial 1 avisaron la hora unos días
  antes y fue distinta en cada comisión: 5K09 de 14:30 a 16:00, 5K10 a las 21:30.
- Aprobación: el que tiene que llegar a 60 es el promedio de los dos parciales,
  no cada parcial por separado.
- Recuperatorio: miércoles 18/11, junto con el del Parcial 1. Lo puede rendir
  cualquiera, y se queda la nota más alta.
```

### Más ideas

- "¿Qué entregas tengo en los próximos días?"
- "¿Hay avisos nuevos en alguna materia?"
- "¿Qué TPs me faltan entregar?"
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

### Gemini (Gemini CLI)

Instalá [Gemini CLI](https://github.com/google-gemini/gemini-cli) y agregá esto a `~/.gemini/settings.json`. Si el archivo ya tiene contenido, sumá solo la entrada `campus` dentro de `mcpServers`:

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

Abrí `gemini` y verificá con `/mcp` que `campus` aparezca.

> La web y la app de Gemini (gemini.google.com) no permiten conectar servidores MCP locales. Funciona solo con Gemini CLI.

### ChatGPT (Codex CLI)

ChatGPT en la web o la app de escritorio solo se conecta a servidores MCP **remotos** (una URL pública por HTTPS). Este servidor corre en tu compu con tu sesión del campus. Publicarlo en internet le daría acceso a tu cuenta a cualquiera que tenga la URL, así que **no lo recomendamos**.

En su lugar usá [Codex CLI](https://github.com/openai/codex), el agente de terminal de OpenAI. Funciona con tu cuenta de ChatGPT y sí soporta MCP local. Desde la carpeta del repo:

```sh
codex mcp add campus \
  --env CAMPUS_USER=tu_usuario --env CAMPUS_PASS=tu_contraseña \
  -- "$(pwd)/.venv/bin/python" "$(pwd)/campus_mcp.py"
```

O agregalo a mano en `~/.codex/config.toml`:

```toml
[mcp_servers.campus]
command = "/ruta/completa/a/campus-utn-frm-mcp/.venv/bin/python"
args = ["/ruta/completa/a/campus-utn-frm-mcp/campus_mcp.py"]
env = { CAMPUS_USER = "tu_usuario", CAMPUS_PASS = "tu_contraseña" }
```

Abrí `codex` y verificá con `/mcp` que `campus` aparezca.

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
