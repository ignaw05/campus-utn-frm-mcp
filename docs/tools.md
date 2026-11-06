# Herramientas del MCP

Referencia de las 6 herramientas que expone el servidor `campus`. Todas son **solo lectura** y devuelven texto plano (o markdown simple) para que la IA lo procese.

No hace falta llamarlas a mano: le hablás a tu cliente (Claude, Codex, Gemini…) y él elige cuáles usar. Esta página sirve para saber qué puede hacer cada una, qué parámetros recibe y qué devuelve.

| Herramienta | Parámetros | Para qué sirve |
|---|---|---|
| [`materias`](#materias) | — | Listar tus materias y sus ids |
| [`contenido_materia`](#contenido_materia) | `course_id` | Ver secciones y recursos de una materia |
| [`vencimientos`](#vencimientos) | `course_id?`, `cantidad?` | Próximas entregas pendientes |
| [`entregas`](#entregas) | `course_id` | Todas las tareas de una materia con su estado |
| [`avisos`](#avisos) | `course_id`, `cantidad?` | Últimos avisos del foro de novedades |
| [`leer`](#leer) | `url` | Abrir una página o descargar un archivo del campus |

`?` = opcional.

## Flujo típico

```
materias ──► course_id ──► contenido_materia ──► url ──► leer
                     ├───► vencimientos / entregas
                     └───► avisos
```

Casi todo arranca con `materias` para obtener el `course_id`. Las URLs que devuelven `contenido_materia` y `vencimientos` se pueden abrir con `leer`.

---

## `materias`

Lista las materias en las que estás inscripto.

**Parámetros:** ninguno.

**Devuelve:** una línea por materia con `id: nombre`, ordenadas por nombre.

```
1234: Ciencia de Datos
1240: Física II
1255: Informática Industrial
```

**Moodle:** `core_course_get_enrolled_courses_by_timeline_classification` (API AJAX).

---

## `contenido_materia`

Muestra las secciones (unidades, semanas, etc.) de una materia y todos sus recursos visibles: apuntes, tareas, foros, links, carpetas.

**Parámetros:**

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `course_id` | int | sí | Id de la materia (sale de `materias`) |

**Devuelve:** un título `##` por sección y un ítem por recurso con `[tipo] nombre <url>`. El tipo es el módulo de Moodle (`resource`, `assign`, `forum`, `url`, `folder`, `page`, …).

```
## Unidad 4: Planificación y Programación de la Producción
- [resource] Apuntes de clase <https://campusvirtual.frm.utn.edu.ar/mod/resource/view.php?id=5678>
- [resource] Presentación <https://campusvirtual.frm.utn.edu.ar/mod/resource/view.php?id=5679>
- [assign] TP 4 <https://campusvirtual.frm.utn.edu.ar/mod/assign/view.php?id=5680>
```

**Moodle:** `core_courseformat_get_state` (API AJAX). Los recursos ocultos no se muestran.

---

## `vencimientos`

Próximas entregas y eventos pendientes del calendario, desde ahora en adelante.

**Parámetros:**

| Nombre | Tipo | Obligatorio | Default | Descripción |
|---|---|---|---|---|
| `course_id` | int | no | `0` | Id de la materia. `0` = todas las materias |
| `cantidad` | int | no | `30` | Máximo de eventos a devolver |

**Devuelve:** una línea por evento con `fecha | materia | nombre <url>`, ordenadas por fecha. Si no hay nada: `No hay vencimientos próximos.`

```
06/11/2026 23:59 | CDATOS | TP 3 vence <https://campusvirtual.frm.utn.edu.ar/mod/assign/view.php?id=5680>
10/11/2026 23:59 | FIS2 | Informe de laboratorio vence <https://...>
```

Las fechas están en la zona horaria de tu compu.

**Moodle:** `core_calendar_get_action_events_by_timesort` (todas) o `core_calendar_get_action_events_by_course` (una materia).

---

## `entregas`

Todas las tareas de una materia, incluidas las ya vencidas, con fecha de entrega, estado y nota.

**Parámetros:**

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `course_id` | int | sí | Id de la materia |

**Devuelve:** la tabla de tareas de Moodle convertida a texto, con columnas separadas por `|` (sección, tarea, fecha de entrega, estado, calificación). Los nombres de las tareas incluyen su URL.

```
 | Tema | Tareas | Fecha de entrega | Entrega | Calificación
 | Unidad 1 | TP 1 <https://...> | 05/09/2026 | Enviado para calificar | 8,00
 | Unidad 2 | TP 2 <https://...> | 03/10/2026 | Sin entrega | -
```

A diferencia de `vencimientos`, muestra también lo pasado. Sirve para "¿qué me falta entregar?" o "¿qué nota me sacaron?".

**Moodle:** scraping de `/mod/assign/index.php?id=<course_id>`.

---

## `avisos`

Últimos avisos del foro de novedades de una materia, con el texto completo de cada uno.

**Parámetros:**

| Nombre | Tipo | Obligatorio | Default | Descripción |
|---|---|---|---|---|
| `course_id` | int | sí | — | Id de la materia |
| `cantidad` | int | no | `5` | Cuántos avisos traer (los más recientes) |

**Devuelve:** el nombre del foro como título y el texto de cada discusión separado por `---`. Si la materia no tiene foros: `La materia no tiene foros.`

```
# Avisos

Parcial 2 - Horarios
de Prof. Pérez - miércoles, 28 de octubre de 2026
El parcial se toma el miércoles 4/11 ...

---

Clase de consulta
...
```

**Limitación:** asume que el **primer foro** de la materia es el de avisos (Moodle lo crea así por defecto). Si una cátedra usa otro foro, buscá su URL con `contenido_materia` y abrilo con `leer`.

**Moodle:** `core_courseformat_get_state` para encontrar el foro + scraping de `/mod/forum/discuss.php?d=<id>`.

---

## `leer`

Abre cualquier URL del campus. Es la herramienta comodín: sirve para páginas, consignas, foros, carpetas y archivos.

**Parámetros:**

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `url` | str | sí | URL absoluta del campus (`https://campusvirtual.frm.utn.edu.ar/...`) o ruta relativa (`/mod/...`) |

**Devuelve:**

- **Página HTML:** el contenido principal convertido a texto, sin menús ni scripts. Los links del campus quedan como `texto <url>` para poder seguirlos con otro `leer`.
- **Archivo** (PDF, docx, pptx, xlsx, zip, imágenes…): lo descarga en `CAMPUS_DESCARGAS` (por defecto `~/Downloads/campus`) y devuelve `Descargado: <ruta>`. Después tu cliente lo lee con su propia herramienta de archivos. Si ya existe un archivo con el mismo nombre, se sobrescribe.
- **URL de otro sitio:** `Solo URLs del campus.`

```
Descargado: /Users/vos/Downloads/campus/Unidad_4_Produccion_Apunte.pdf
```

---

## Errores comunes

| Mensaje | Causa |
|---|---|
| `Login falló: revisá CAMPUS_USER/CAMPUS_PASS` | Usuario o contraseña incorrectos |
| `KeyError: 'CAMPUS_USER'` | Faltan las variables de entorno en la config del cliente |
| Mensaje de Moodle (ej. `Can't find data record in database`) | `course_id` inexistente o materia en la que no estás inscripto |

La sesión se renueva sola: si vence, el servidor vuelve a loguearse y reintenta.
