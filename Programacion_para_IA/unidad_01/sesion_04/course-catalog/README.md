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

## Ejercicio 4 · Mejorar el diagnóstico

Cambié el mensaje INFO de `catalog/search.py` para que también muestre
cuántos cursos se leyeron:

```python
logger.info("Search completed: %d courses read, %d matches", len(courses), len(matches))
```

Consulta directa (`uv run python main.py python`):
`Search completed: 3 courses read, 2 matches` → PY01 y PY02.

Llamada MCP (`uv run python client.py python`): la herramienta `find_courses`
devuelve los mismos cursos, PY01 y PY02, con `is_error: false`.

**Explicación:** usé argumentos de logging (`%d`) en lugar de f-strings. Así
el texto solo se arma si el nivel del mensaje está activo. Ahora se distingue
un catálogo vacío (0 cursos leídos) de una búsqueda sin coincidencias.