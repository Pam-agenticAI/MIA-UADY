# Catálogo de cursos reproducible con uv y MCP

Unidad 1, sesión 4 · Programación para Inteligencia Artificial · Pamela Benítez

Proyecto que busca cursos por palabras del título, de dos formas: desde la
terminal (`main.py`) y como herramienta MCP (`server.py` y `client.py`).

## Cómo ejecutarlo

```bash
uv sync --locked                 # crea el entorno con las versiones exactas
uv run python main.py python     # consulta directa
uv run python client.py python   # consulta por MCP
make check                       # estilo, formato, tipos y pruebas
```

## Ejercicio 1 · Punto de entrada

```bash
uv run python -c "import main"
```

Resultado: no imprime nada y termina con código 0.

**Explicación:** al importar `main.py` solo se definen las funciones. La
consulta está dentro de `if __name__ == "__main__":`, que solo se cumple
cuando el archivo se ejecuta directamente, no cuando se importa. `server.py`
usa la misma condición para `mcp.run(transport="stdio")`, por eso importarlo
no inicia el servidor. Registrar una herramienta (`@mcp.tool()`) solo la
agrega a la lista del servidor; iniciar el servidor (`mcp.run`) es lo que lo
pone a escuchar peticiones.

## Ejercicio 2 · Datos y argumentos

Copié `data/courses.json` a `data/extra_courses.json` y agregué el curso
PY03 "Python for safety inspections".

```bash
uv run python main.py python --catalog data/extra_courses.json
```

Resultado: 3 cursos (PY01, PY02 y PY03). Con el catálogo original salen solo 2.

```bash
uv run python main.py python --catalog data/no_existe.json
echo $?
```

Resultado: `FileNotFoundError` y código de salida 1.

**Explicación:** `--catalog` permite elegir qué archivo leer sin cambiar el
código. Cuando el archivo no existe, `main.py` atrapa el error, lo registra
y devuelve 1 para avisar que falló. El error se escribe en el registro y no
en stdout. La herramienta MCP sigue usando el catálogo predeterminado porque
`server.py` no recibe `--catalog`.

## Ejercicio 3 · Niveles y destinos

| Nivel | Lo que aparece en consola |
|---|---|
| DEBUG | `Reading catalog: .../data/courses.json` y `Search completed: 3 courses read, 2 matches` |
| INFO | solo `Search completed: 3 courses read, 2 matches` |
| ERROR | ningún mensaje, solo el resultado JSON |

```bash
uv run python main.py python --log-level ERROR --log-file logs/app.log
```

Resultado: la consola no muestra mensajes, pero `logs/app.log` contiene:

```text
DEBUG | catalog.search | Reading catalog: .../data/courses.json
INFO | catalog.search | Search completed: 3 courses read, 2 matches
```

**Explicación:** en `logging_config.py` hay dos destinos. La consola usa el
nivel que elijo con `--log-level`, pero el archivo siempre guarda desde
DEBUG. Por eso el archivo conserva mensajes que no aparecen en consola.
En `server.py`, stdout se reserva para el protocolo porque por ahí viajan los
mensajes MCP entre cliente y servidor. Si un mensaje de registro se escribiera
en stdout, el cliente recibiría texto que no entiende y la comunicación se
rompería. Por eso los registros van a stderr.

## Ejercicio 4 · Mejorar el diagnóstico

Cambié el mensaje INFO de `catalog/search.py` para que también muestre
cuántos cursos se leyeron, usando argumentos de logging:

```
logger.info("Search completed: %d courses read, %d matches", len(courses), len(matches))
```

Consulta directa: `Search completed: 3 courses read, 2 matches` → PY01 y PY02.
Llamada MCP: la herramienta `find_courses` devuelve los mismos cursos, PY01 y
PY02, con `is_error: false`.

**Explicación:** con argumentos de logging (`%d`) en lugar de f-strings, el
texto solo se arma si el nivel del mensaje está activo. Ahora se distingue un
catálogo vacío (0 cursos leídos) de una búsqueda sin coincidencias.

## Ejercicio 5 · Reproducción y llamada MCP

Desde una copia limpia del repositorio ejecuté `uv sync --locked` y luego:

| Consulta | Resultado | `is_error` |
|---|---|---|
| `python` | PY01 y PY02 | false |
| `astronomy` | lista vacía (`3 courses read, 0 matches`) | false |
| `"   "` (espacios) | `Cannot search the catalog...` | true |

La herramienta disponible es `find_courses`.

**Explicación:** una respuesta vacía no es un error: la búsqueda funcionó y
simplemente no hubo coincidencias. En cambio, una consulta con solo espacios
es inválida: `search_courses` lanza `ValueError` y el servidor la convierte
en un error de herramienta (`is_error: true`), sin dejar de funcionar.

- `pyproject.toml` declara el proyecto, sus dependencias y la configuración de
  las herramientas.
- `uv.lock` fija las versiones exactas de todas las dependencias, para que
  cualquier persona instale lo mismo.
- `.python-version` indica qué versión de Python usar.
- `.venv` no se entrega porque es pesado, depende de cada computadora y se
  puede reconstruir con `uv sync --locked`.

## Calidad de código

Agregué `pytest`, `ruff` y `mypy` como dependencias de desarrollo, su
configuración en `pyproject.toml`, las pruebas de `tests/` y el `Makefile`.

### Calidad 1 y 2 · Pruebas nuevas (`tests/test_quality.py`)

- `test_negative_hours`: un curso con horas negativas produce un error de
  validación, porque `Course` exige `hours` mayor que 0.
- `test_console_missing_file`: ejecuta `main.py` con `subprocess.run` y un
  archivo inexistente en un directorio temporal de pytest. Comprueba código
  de salida 1 y stdout vacío.

### Calidad 3 · Import sin usar

Agregué `import os` a `catalog/__init__.py` y Ruff falló con `F401 'os'
imported but unused`. Al quitar la línea volvió a `All checks passed!`.
Ruff encuentra estos problemas sin ejecutar el programa.

### Calidad 4 · Copia limpia

Cloné el repositorio en una carpeta nueva y ejecuté `uv sync --locked` y
`make check`: Ruff sin errores, 10 archivos ya formateados, mypy sin
problemas en 6 archivos y 8 pruebas aprobadas. `make client` devolvió PY01
y PY02 con `is_error: false`.
