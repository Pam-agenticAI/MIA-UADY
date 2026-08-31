# Reporte — Mi Cueva 4x4

## Configuración

- Wumpus: (1,2)
- Pits: (3,2), (3,4), (4,3)
- Oro: (3,3)
- Agente inicia en (1,1), mirando este

## Diagrama

```
 4 | .  .  P  . 
 3 | .  .  G  P 
 2 | W  .  P  . 
 1 | >  .  .  . 
      1  2  3  4
```

## Resultados por agente

| Agente | ¿Salió con el oro? | Steps | Score |
|---|---|---|---|
| Reflejo simple | No | 200 | -200 |
| Basado en modelo | No | 200 | -200 |
| Basado en metas | No | 200 | -200 |
| Basado en utilidad | No (murió) | 9 | -1009 |
| Que aprende | Sí | 16 | +984 |

## Análisis

### ¿Qué agentes lograron salir con el oro en tu mapa y cuáles no?

El único agente que logró salir con el oro fue el agente que aprende. El resto de modelos (reflejo simple, basado en modelo y el basado en metas) ni siquiera lograron avanzar ya que al estar el wumpus cercano a la casilla y carecer de registro de una ruta segura no se arriesgaron a avanzar. En el caso del modelo basado en utilidad, si bien exploró y avanzó, no llegó a encontrar el oro y murió en el camino.

### ¿Por qué el agente de reflejo simple falla (o tiene suerte) en tu diseño?

Porque se sigue la instrucción de que al considerarse en riesgo por el hedor, es mejor que gire por lo que en estos agentes optan por girar antes que arriesgarse si no hay registro en la memoria de una ruta segura. La instrucción del agente es que mientras haya peligro (sin importar cuantos) gire en lugar de arriesgarse y avanzar.

### ¿Cómo cambia el resultado del agente basado en modelo si acercas o alejas un pit de la casilla inicial?

El acercar el pit a la casilla inicial (de (3,2) a (2,1)) no cambia nada mientras el wumpus se siga manteniendo cerca debido a que el evento de stench se sigue desencadenando. Al no haber registro de ruta segura conocida, y el agente detectando stench va a seguir la instrucción de girar antes que arriesgarse.
