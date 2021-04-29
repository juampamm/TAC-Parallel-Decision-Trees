# TAC-Parallel-Decision-Trees
Repositorio creado para exponer el trabajo de la asignatura de Teoría Avanzada de la Computación sobre árboles de decisión en paralelo y uso de nuevos procesadores.

La versión de Python usada durante todo el desarollo del proyecto es *Python 3.6*.

El archivo principal es Main.py, en el que se puede encontrar todo el código desarrollado. En las primeras líneas hay una serie de constantes que se pueden modificar:
  - PARALLEL2: si se establece a *True*, se ejecutará paralelización sobre los atributos.
  - PARALLEL2: si se establece a *True*, se hará una paralelización sobre cada *fold* para la validación cruzada.
  - NUM_ATRIBUTES: modifica el número de atributos.
  - SAMPLES: número de instancias usadas.
  - MAX_DEPTH: máxima profundidad del árbol.

No se usa ningún archivo real, por lo que se genera uno con valores aleatorios ya que el acierto del árbol de decisión no es objeto de estudio en este trabajo.

Para ejecutar el archivo: *python main.py*

El *notebook* arboles_decision_multigpu.ipynb está preparado con múltiples celdas para evaluar el rendimiento variando el número de hilos.
