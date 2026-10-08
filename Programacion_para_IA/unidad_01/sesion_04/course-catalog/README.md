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