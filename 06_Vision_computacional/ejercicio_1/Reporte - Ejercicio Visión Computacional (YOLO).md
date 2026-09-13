# Reporte — Ejercicio 1, Visión Computacional (YOLO ultralytics)

## Qué se hizo

Se corrió la notebook `13 YOLO ultralytics.ipynb` en Google Colab (entorno GPU T4) tal como está, con las predicciones originales sobre `zidane.jpg` y `bus.jpg`. Después se hizo el único cambio pedido: se sustituyeron ambas fuentes de predicción (celda CLI y celda `model(...)`) por la misma imagen propia — una foto de un salón de clases con estudiantes, laptops, un pizarrón y una pantalla — sin modificar el modelo (`yolov8n.pt`), las épocas de entrenamiento (`epochs=3`) ni el dataset (`coco128.yaml`).

## Resultados

| Imagen | Método | Detecciones |
|---|---|---|
| Zidane (original) | CLI | 2 personas, 1 corbata |
| Bus (original) | `model()` | 4 personas, 1 bus, 1 señal de alto |
| Mi foto (salón de clases) | CLI | 7 personas, 2 sillas, 1 tv, 5 laptops |
| Mi foto (salón de clases) | `model()` | 7 personas, 1 silla, 1 tv, 6 laptops |

## Preguntas

**¿Qué clases detectó YOLO en las fotos de Ultralytics y cuáles en la tuya?**

En las fotos de muestra, YOLO detectó clases sencillas y pocas por imagen: *person* y *tie* en Zidane; *person*, *bus* y *stop sign* en el bus. En mi foto detectó una mezcla más rica de clases de interior/oficina — *person*, *laptop*, *tv* y *chair* — reflejando que es una escena con más objetos y más variedad de categorías COCO presentes a la vez.

**¿Algún objeto evidente de tu foto no salió etiquetado? ¿Por qué podría pasar?**

Sí: en la foto se ven claramente entre 5 y 6 sillas/pupitres, pero YOLO solo marcó 1 (con `model()`) o 2 (con CLI). La mayoría de las sillas quedó sin caja. Esto probablemente pasa porque los estudiantes sentados ocultan buena parte de cada silla (solo se ve una porción pequeña, muchas veces solo una pata o el respaldo), lo que baja la confianza del modelo por debajo del umbral de detección — y porque YOLOv8n (la versión "nano", la más ligera de la familia) tiene menor capacidad de detección que versiones más grandes como `yolov8s` o `yolov8m`.

**¿La predicción de la celda CLI y la de `model(...)` coinciden sobre tu misma imagen?**

No coinciden exactamente. El CLI detectó 2 sillas y 5 laptops, mientras que `model(...)` detectó solo 1 silla y 6 laptops sobre la misma foto. Ambas corridas usan el mismo modelo base (`yolov8n.pt`), así que la diferencia probablemente viene de que el modelo fue reentrenado (fine-tuned 3 épocas sobre coco128) entre una corrida y otra, lo que cambia ligeramente los pesos y por tanto el umbral de confianza con el que cada objeto queda o no por encima del corte de detección — un ejemplo concreto de cómo hasta un fine-tune corto puede mover las predicciones cerca del límite de confianza.

## Evidencia

- Notebook en Colab: https://colab.research.google.com/drive/1e9dS5-0NwQMBmn_hLgj_bs1MFvX0Qmmg
- Entorno: GPU T4 confirmado (`Setup complete ✅`, indicador "T4 (Python 3)")
- Capturas: predicción original sobre Zidane, predicción original sobre el bus, predicción CLI sobre mi foto (`predict-8`), predicción `model()` sobre mi foto (`predict-9`)
