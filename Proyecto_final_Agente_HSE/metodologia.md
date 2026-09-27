# Metodología — Agente HSE (MLP + búsqueda ponderada por riesgo)

Este proyecto se divide en tres notebooks de **análisis exploratorio**
(`distribucion_riesgo_y_palabras_por_categoria.ipynb`, `nube_palabras_riesgo.ipynb` y
`preparacion_vocabulario_tfidf.ipynb`) que preparan y caracterizan el dataset, y un
notebook de **modelo** (`entrenamiento_mlp_riesgo.ipynb`) que entrena el MLP, compara
umbrales de decisión, calcula el riesgo por contratista y ejecuta la búsqueda ponderada.
Cada sección documenta la observación en los datos que motivó la decisión, y qué
herramienta se usó para llegar a esa observación.

## Parte 1 — Preparación y exploración de datos
*(scripts: `distribucion_riesgo_y_palabras_por_categoria.ipynb`,
`nube_palabras_riesgo.ipynb`, `preparacion_vocabulario_tfidf.ipynb`)*

### A. Preparación del dataset

#### A.1 Fuente de datos

**Observación:** el registro de Safety Save (BOLT) del proyecto MID1 contiene 105
observaciones de seguridad, con una descripción de la omisión (seleccionada de una lista
predefinida), severidad potencial y contratista responsable,
pero incluye nombres de personas en algunas columnas (observador, responsable de acción).

**Decisión:** descartar las columnas con nombres de personas y anonimizar los 7
contratistas originales con 5 códigos genéricos (Contratista A–E), antes de cualquier
análisis. Tres de las empresas se agruparon en un mismo código porque operan como una
sola entidad en el proyecto.

**Herramienta:** `pandas` (`pd.read_excel`, selección de columnas, `.map()` para
anonimizar), ejecutado en un script de preparación de datos.

#### A.2 Reclasificación binaria del riesgo

**Observación:** la columna original de severidad tiene 5 categorías (Negligible, Minor,
Significant, Major, sin dato) con conteos muy desbalanceados — algunas con menos de 6
registros sobre 105 totales.

**Decisión:** colapsar las 5 categorías en 2 (alto/bajo) para tener clases con muestra
suficiente (50 vs. 55), conservando la severidad original como columna aparte para
trazabilidad. La agrupación aplicada fue:

| Severidad original | Categoría reclasificada |
|---|---|
| Major | alto |
| Significant | alto |
| Minor | bajo |
| Negligible | bajo |
| Sin dato | bajo |

El criterio: "Major" y "Significant" implican una consecuencia seria (lesión o
incumplimiento grave), mientras que "Minor" y "Negligible" corresponden a menor
consecuencia. Las filas sin dato de severidad se agruparon como "bajo" para no perderlas,
aunque esto es una decisión pragmática y no evidencia real de bajo riesgo.

**Herramienta:** `pandas` (`.map()` con diccionario de reclasificación, `.value_counts()`
para verificar el balance resultante).

### B. Nube de palabras

**Motivación:** antes de entrar a la estadística formal, se generó una nube de palabras
por categoría de riesgo (alto/bajo) como primer acercamiento visual al texto de las
observaciones.

**Herramienta:** `WordCloud`, generada por separado para observaciones de riesgo alto y
riesgo bajo, a partir del texto tokenizado (patrón de 3+ letras).

**Hallazgo visual:** "failing" y "not" destacan por tamaño en ambas nubes, lo cual
sugiere que no separan bien las dos categorías. En cambio, "waste", "dispose" y
"accumulating" resaltan más en la nube de riesgo bajo, y "hazard", "ppe", "barrier",
"training" en la de riesgo alto — una separación más por tema que por lenguaje de
incumplimiento genérico. Este hallazgo visual es el que se confirma con números en la
sección C.2.

### C. Análisis exploratorio estadístico

#### C.1 Distribución de riesgo por contratista

**Observación:** Contratista A concentra 68 de 105 observaciones (65%), con una
proporción casi equilibrada entre riesgo alto y bajo; el resto de los contratistas tiene
muestra insuficiente para conclusiones individuales.

**Decisión:** solo Contratista A, B y C se usarán con score de riesgo calculado a partir
de datos propios; el resto se tratará con un valor por defecto o se excluirá de la
comparación cuantitativa, documentando esto como limitación.

**Herramienta:** `pandas` (`.groupby()` + `.unstack()`) y un gráfico de barras agrupado.

#### C.2 Palabras más frecuentes y preparación del vocabulario para TF-IDF

**Confirmación estadística de la nube:** para respaldar con números lo que mostró la
nube de palabras en la sección B, se contó la frecuencia exacta de palabras por categoría
de riesgo.

**Herramienta:** tokenización con `re` (patrón de 3+ letras) + `Counter` de
`collections` (`.most_common(8)`) para la frecuencia absoluta por categoría; estos
mismos conteos alimentan también los gráficos de barras.

**Punto de partida para el vocabulario completo:** además de la frecuencia por
categoría, se calcularon medidas descriptivas básicas sobre todo el texto:

| Medida | Valor |
|---|---|
| Número de observaciones | 105 |
| Longitud promedio del texto | ~7 palabras |
| Longitud mínima | 2 palabras |
| Longitud máxima | 14 palabras |
| Tamaño del vocabulario único | 109 palabras |

Estas medidas mostraron que tanto la muestra como el vocabulario eran pequeños y de
orden similar (109 palabras para 105 observaciones), lo cual planteó una alerta de
posible sobreajuste si se usaba el vocabulario completo sin filtrar.

**Justificación del conteo de frecuencia general:** a partir de esa alerta, el objetivo
fue distinguir qué palabras del vocabulario eran realmente informativas y cuáles eran
ruido, usando el conteo real de frecuencia en vez de suponerlo. El conteo reveló dos
tipos de ruido distintos: por un lado, 24 de las 109 palabras del vocabulario total
aparecían una sola vez en todo el corpus de 105 observaciones — es decir, demasiado
raras para que el modelo aprenda un patrón confiable a partir de ellas; por otro lado, un
grupo pequeño de palabras muy frecuentes resultó ser conectores sin significado.

**Herramienta para el conteo:** `Counter` de `collections` (`.most_common(20)`), aplicado
sobre las palabras extraídas con `re.findall` y el patrón `\b[a-zA-Z]+\b` (sin filtro de
longitud, para no descartar nada antes de ver los resultados).

**Resultado del conteo:** "to", "or", "of" resultaron ser las palabras más frecuentes de
todo el vocabulario, sin aportar señal para distinguir el riesgo:

| Palabra | Frecuencia |
|---|---|
| to | 64 |
| or | 43 |
| of | 41 |
| failing | 38 |
| waste | 26 |
| properly | 19 |
| not | 19 |
| training | 18 |
| ppe | 14 |
| hazard | 14 |

**Decisión de tokenización:** con este resultado en mano, se decidió tokenizar solo
palabras de 3+ letras — esto descarta "to", "or", "of" automáticamente — y evitar la
lista estándar de stopwords en inglés, porque esa lista elimina "not", una negación
relevante en este dominio.

**Herramienta para tokenizar:** patrón de expresión regular `\b[a-zA-Z]{3,}\b`, que se
aplicará como `token_pattern` dentro de `TfidfVectorizer` en el paso de vectorización.

## Parte 2 — Modelo de clasificación y búsqueda ponderada
*(script: `entrenamiento_mlp_riesgo.ipynb`)*

### 2.1 Vectorización TF-IDF

**Observación:** con base en la sección C.2, el vocabulario resultante es pequeño (79 palabras
tras `min_df=2`), similar en tamaño a la muestra disponible.

**Decisión:** usar `TfidfVectorizer` con `min_df=2` y sin lista de stopwords, tokenizando
palabras de 3+ letras.

**Herramienta:** `sklearn.feature_extraction.text.TfidfVectorizer`.

### 2.2 Entrenamiento del MLP

#### 2.2.1 Arquitectura y validación

**Observación:** con 105 observaciones y un vocabulario de 79 palabras tras la
vectorización TF-IDF, la cantidad de datos es reducida frente a la cantidad de parámetros
que podría tener un modelo. Un split fijo de entrenamiento/prueba dejaría un conjunto de
evaluación de apenas ~21 observaciones, insuficiente para una métrica confiable.

**Decisión:** usar una arquitectura conservadora (una sola capa oculta de 8 neuronas,
activación ReLU, salida sigmoide) para minimizar el riesgo de sobreajuste, y evaluar con
validación cruzada estratificada de 5 particiones en lugar de un split único, para que
cada observación participe exactamente una vez en evaluación y la proporción de riesgo
alto/bajo se mantenga consistente en cada partición.

**Herramienta:** `keras.Sequential` para la arquitectura, `StratifiedKFold` de
scikit-learn (`n_splits=5, shuffle=True, random_state=42`) para la validación cruzada,
`confusion_matrix` y `accuracy_score` de scikit-learn para las métricas.

#### 2.2.2 Reproducibilidad

**Observación:** una primera corrida sin semilla fija para los pesos de la red dio 70.5%
de exactitud promedio; al volver a ejecutar el mismo código, el resultado cambió (71.4%),
porque la red inicia con pesos aleatorios distintos en cada ejecución.

**Decisión:** fijar la semilla aleatoria de la red para que cualquier ejecución del
notebook produzca exactamente los mismos resultados. Se verificó volviendo a ejecutar y
obteniendo resultados idénticos.

**Herramienta:** `keras.utils.set_random_seed(42)`.

#### 2.2.3 Resultados oficiales (semilla 42)

| Ronda | Exactitud |
|---|---|
| 1 | 0.619 |
| 2 | 0.810 |
| 3 | 0.905 |
| 4 | 0.667 |
| 5 | 0.571 |
| **Promedio** | **0.714** |
| Desviación estándar | 0.124 |

Matriz de confusión acumulada (umbral 0.5): 36 bajos correctos, 19 falsas alarmas,
11 altos no detectados, 39 altos detectados (sensibilidad para riesgo alto: 78%).

#### 2.2.4 Umbral de decisión

**Observación:** con el umbral estándar de 0.5, 11 de 50 observaciones de riesgo alto
se clasificaron como riesgo bajo, el error más costoso en un contexto de seguridad.

**Decisión:** comparar cuatro umbrales repitiendo la misma validación cruzada con la
misma semilla, y guardando la probabilidad de cada observación:

| Umbral | Exactitud | Altos detectados | Altos no detectados | Falsas alarmas |
|---|---|---|---|---|
| 0.3 | 64.8% | 44 de 50 | 6 | 31 |
| 0.4 | 74.3% | 44 de 50 | 6 | 21 |
| 0.5 | 71.4% | 39 de 50 | 11 | 19 |
| 0.6 | 63.8% | 25 de 50 | 25 | 13 |

Se eligió el umbral 0.4. El umbral de 0.4, si bien genera un número significativo de
falsas alarmas (21 de 55 observaciones de riesgo bajo), se justifica en un contexto de
seguridad industrial, porque es preferible una alerta de más a que condiciones de alto
riesgo se clasifiquen como de bajo riesgo. La diferencia entre el umbral de 0.5 y el de
0.4 reduce los riesgos no detectados de 11 a 6, a cambio de solo 2 falsas alarmas más.

Estos resultados deben interpretarse con cautela por dos razones: la muestra es limitada
(105 observaciones) y el umbral se eligió con los mismos datos con los que se evalúa el
modelo, lo que puede hacer que su desempeño se vea más favorable de lo que sería con
observaciones nuevas.

**Herramienta:** `keras.utils.set_random_seed(42)` + el mismo `StratifiedKFold`,
`confusion_matrix(...).ravel()` para contar aciertos y errores por umbral.

#### 2.2.5 Limitación de los datos de entrada

La columna `texto`, que es la única entrada del modelo, indica la omisión de seguridad
presentada, sin una relación con el riesgo de la actividad como tal. Puede presentarse
la misma descripción en texto con una severidad potencial diferente, debido a que la
severidad potencial es asignada por el usuario tomando en cuenta factores como si había
personal presente, la ubicación u otros riesgos derivados de operaciones simultáneas.
Como esos factores no quedan registrados en el texto, el modelo recibe exactamente la
misma entrada con etiquetas distintas y no puede distinguirlas, lo que limita la
exactitud que puede alcanzar.

### 2.3 Grafo de frentes de trabajo y búsqueda ponderada por riesgo

#### 2.3.1 Riesgo por contratista

**Observación:** el MLP produce una probabilidad de riesgo alto para cada observación,
pero el grafo necesita un solo valor de riesgo por nodo.

**Decisión:** calcular el riesgo de cada contratista como el promedio de las
probabilidades que el MLP asignó a sus observaciones (obtenidas en la validación cruzada
del paso 2.2.4). Siguiendo la decisión de la sección C.1, solo los contratistas A, B y C
usan su propio promedio; D y E, con una sola observación cada uno, reciben el promedio
general del dataset como valor por defecto.

| Contratista | Observaciones | Riesgo promedio | % sobre umbral 0.4 | Riesgo asignado |
|---|---|---|---|---|
| A | 68 | 0.500 | 60.3% | 0.500 |
| B | 24 | 0.524 | 66.7% | 0.524 |
| C | 11 | 0.406 | 54.5% | 0.406 |
| D | 1 | 0.929 | 100% | 0.502 (por defecto) |
| E | 1 | 0.769 | 100% | 0.502 (por defecto) |

El valor por defecto evitó que D y E, con probabilidades individuales muy altas (0.929 y
0.769) pero basadas en una sola observación, dominaran la ruta de inspección.

**Herramienta:** `pandas` (`.groupby('contratista').agg(...)`).

#### 2.3.2 Definición de los nodos

**Observación:** el campo de ubicación del registro BOLT no era obligatorio al momento
de capturar, y las observaciones se registran con categorías de una lista predefinida,
por lo que no fue posible reconstruir el área física de cada observación.

**Decisión:** definir los nodos del grafo como **frentes de trabajo por actividad**, cada
uno asociado al contratista que la ejecuta, con base en el conocimiento de campo de la
autora. El riesgo de cada nodo es el riesgo asignado a su contratista (sección 2.3.1).

| Nodo (frente de trabajo) | Contratista | Riesgo |
|---|---|---|
| Acceso (inicio) | — | — |
| High racking | A | 0.500 |
| Etiquetas y accesorios de seguridad | C | 0.406 |
| Sistema eléctrico (tubería y soportería) | B | 0.524 |
| Sistema contra incendio (tubería y soportería) | B | 0.524 |
| HVAC (tubería y soportería) | B | 0.524 |
| Oficina HSE (llegada) | — | — |

El diseño de ingeniería del contratista B se excluyó por ser trabajo de oficina, sin
frente de campo que inspeccionar. Los contratistas D y E no se incluyeron como nodos por
no tener una actividad de campo continua.

Se consideró también dividir el análisis por fase de construcción (fase 1: 15 de junio
a 24 de agosto; fase 2: 25 de agosto a 7 de septiembre; fase 3: 8 a 19 de septiembre),
pero se descartó porque el dataset limpio no conserva fechas y porque dividir 105
observaciones en tres fases dejaría muestras demasiado pequeñas por contratista.

**Herramienta:** diccionario de Python (`zona_contratista`).

#### 2.3.3 Tiempos de traslado

**Observación:** no se cuenta con un plano ni con mediciones de los recorridos entre
frentes de trabajo.

**Decisión:** usar tiempos de traslado aproximados en minutos, estimados a partir del
recorrido habitual de inspección en sitio, solo entre frentes vecinos (el algoritmo suma
los tramos para llegar a frentes más lejanos). Se documentan como supuesto de diseño.

| Desde | Hasta | Minutos |
|---|---|---|
| Acceso | High racking | 3 |
| Acceso | Sistema eléctrico | 4 |
| High racking | Etiquetas y accesorios | 2 |
| High racking | Sistema contra incendio | 3 |
| Etiquetas y accesorios | HVAC | 4 |
| Etiquetas y accesorios | Oficina HSE | 6 |
| Sistema eléctrico | HVAC | 5 |
| Sistema contra incendio | HVAC | 3 |
| Sistema contra incendio | Oficina HSE | 5 |
| HVAC | Oficina HSE | 4 |

**Herramienta:** lista de tuplas de Python (`traslados`), con conexiones en ambos
sentidos.

#### 2.3.4 Costo ponderado por riesgo

**Observación:** una búsqueda que solo minimiza el tiempo ignora dónde está el riesgo.

**Decisión:** construir dos grafos con los mismos nodos y conexiones. En el primero, el
costo de cada tramo es su tiempo real. En el segundo, el costo de llegar a un frente es
`minutos × (1 − riesgo del frente)`, de modo que un frente más riesgoso "cuesta" menos y
la búsqueda tiende a pasar por él. Las dos rutas se comparan después en minutos reales.

**Herramienta:** búsqueda de costo uniforme implementada con una cola de prioridad
(`heapq`), con la misma lógica usada en el laboratorio del mapa de Rumania: se expande
siempre primero el camino con menor costo acumulado.

#### 2.3.5 Resultados

| Ruta | Recorrido | Tiempo real | Riesgo acumulado |
|---|---|---|---|
| Ingenua (solo tiempo) | Acceso → High racking → Etiquetas y accesorios → Oficina HSE | 11 min | 0.906 |
| Ponderada por riesgo | Acceso → High racking → Sistema contra incendio → Oficina HSE | 11 min | 1.024 |

Ambas rutas tardan lo mismo. La ruta ponderada sustituye el frente de etiquetas
(contratista C, riesgo 0.406) por el de sistema contra incendio (contratista B, riesgo
0.524), lo que eleva el riesgo acumulado cubierto de 0.906 a 1.024 sin aumentar el
tiempo de recorrido.

**Limitaciones:**
- La diferencia de riesgo entre contratistas es pequeña (0.406 a 0.524), por lo que la
  ponderación solo cambia la ruta cuando hay empates o casi empates de tiempo.
- En la ruta ingenua, las dos opciones empatan en 11 minutos; la elección de etiquetas
  se debe a un desempate interno del algoritmo, no a un criterio de seguridad.
- Los tiempos de traslado son estimaciones, no mediciones.
- El riesgo se asigna por contratista y no por frente, así que los tres frentes del
  contratista B comparten el mismo valor.

#### 2.3.6 Interpretación

El resultado es consistente con mi criterio de campo, ya que las actividades
relacionadas con el sistema contra incendio tienen más riesgo asociado que la instalación
de etiquetas y accesorios de seguridad. Sin embargo, el riesgo se calcula por contratista
y no por actividad: los tres frentes del contratista B comparten el mismo valor, y el
agente eligió el sistema contra incendio porque era el frente de ese contratista que
quedaba en el camino.

Para que el agente pudiera calcular el riesgo por frente de trabajo, sería necesario que
el campo de ubicación fuera obligatorio desde la captura del Safety Save en la plataforma
BOLT. Además, contar con descripciones en texto libre, y no solo con categorías de una
lista predefinida, permitiría al modelo distinguir mejor el nivel de riesgo, ya que hoy
una misma categoría se registra con distinta severidad.

Con los datos de las condiciones de riesgo asociados a su ubicación, este enfoque podría
aplicarse a los proyectos para asignar inspecciones con una frecuencia proporcional al
riesgo del lugar donde se realizan las actividades: a mayor riesgo registrado, mayor
cantidad de inspecciones asignadas.
