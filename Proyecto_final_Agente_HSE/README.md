# Agente HSE: clasificación de riesgo y rutas de inspección

Proyecto final de la materia **Introducción a la Inteligencia Artificial**, Maestría en Inteligencia Artificial, UADY.

## El problema

En una obra de construcción, el equipo de seguridad industrial tiene tiempo limitado para inspeccionar los frentes de trabajo. Este proyecto construye un agente que usa los registros de observaciones de seguridad (Safety Saves) para estimar el riesgo de cada contratista y planear una ruta de inspección que priorice los frentes más riesgosos sin aumentar el tiempo de recorrido.

## Cómo funciona el agente

1. **Clasifica el riesgo.** Un perceptrón multicapa lee la descripción de cada observación de seguridad y estima la probabilidad de que sea de riesgo alto.
2. **Calcula el riesgo por contratista.** Promedia las probabilidades de las observaciones de cada contratista.
3. **Planea la ruta.** Una búsqueda de costo uniforme recorre un grafo de frentes de trabajo, donde el costo de llegar a cada frente se reduce según su riesgo: `minutos × (1 − riesgo)`.

## Datos

- 105 observaciones de seguridad del registro BOLT del proyecto MID1 (junio a septiembre de 2026).
- Columnas: descripción de la omisión, severidad potencial original, riesgo reclasificado (alto/bajo) y contratista.
- Se eliminaron los nombres de personas y los contratistas se anonimizaron con códigos (Contratista A a E).

## Archivos

| Archivo | Contenido |
|---|---|
| `safety_save_limpio.csv` | Dataset limpio y anonimizado |
| `distribucion_riesgo_y_palabras_por_categoria.ipynb` | Distribución del riesgo por contratista y palabras frecuentes |
| `nube_palabras_riesgo.ipynb` / `.png` | Nube de palabras por categoría de riesgo |
| `preparacion_vocabulario_tfidf.ipynb` | Análisis del vocabulario para la vectorización |
| `entrenamiento_mlp_riesgo.ipynb` | Modelo, comparación de umbrales, riesgo por contratista y rutas |
| `metodologia.md` | Documentación completa de cada decisión (observación, decisión y herramienta) |

## Resultados principales

**Modelo** (validación cruzada estratificada de 5 particiones, semilla fija):
- Exactitud promedio: 71.4% (desviación estándar 0.124).
- Umbral de decisión elegido: 0.4. Detecta 44 de 50 observaciones de riesgo alto (6 no detectadas, contra 11 con el umbral estándar de 0.5), a cambio de 2 falsas alarmas más.

**Rutas de inspección:**

| Ruta | Recorrido | Tiempo | Riesgo acumulado |
|---|---|---|---|
| Solo tiempo | Acceso → High racking → Etiquetas y accesorios → Oficina HSE | 11 min | 0.906 |
| Ponderada por riesgo | Acceso → High racking → Sistema contra incendio → Oficina HSE | 11 min | 1.024 |

Con el mismo tiempo de recorrido, el agente dirige la inspección hacia el frente de mayor riesgo.

## Limitaciones

- La muestra es pequeña (105 observaciones) y el umbral se eligió con los mismos datos con los que se evalúa el modelo.
- Las descripciones son categorías de una lista predefinida: la misma categoría aparece con distinta severidad, porque la severidad depende del contexto que evalúa quien observa y que no queda registrado.
- El riesgo se calcula por contratista y no por frente de trabajo, y las diferencias entre contratistas son pequeñas (0.406 a 0.524).
- Los frentes de trabajo y los tiempos de traslado se definieron con conocimiento de campo, porque el campo de ubicación no era obligatorio en el registro.

## Recomendaciones

Hacer obligatorio el campo de ubicación y permitir descripciones en texto libre al registrar las observaciones. Con esos datos, el riesgo podría calcularse por frente de trabajo y usarse para asignar la frecuencia de inspección: a mayor riesgo registrado, más inspecciones.

## Cómo ejecutarlo

1. Abrir el notebook en Google Colab.
2. Subir `safety_save_limpio.csv` desde el panel de archivos (ícono de carpeta).
3. Ejecutar todas las celdas en orden (Entorno de ejecución → Ejecutar todas).

Los resultados son reproducibles gracias a la semilla fija (`keras.utils.set_random_seed(42)`).

## Autora

Pamela C. Benítez M.
