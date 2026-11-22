# Software FJ: clientes, servicios y reservas

Proyecto académico para la Fase 4 de Programación (213023), ejercicio 1. Usa Python 3 y únicamente la biblioteca estándar; no necesita base de datos ni paquetes externos.

## Ejecución

Abra una terminal en esta carpeta y ejecute `python main.py` (o `py main.py` en Windows). La simulación ejecuta 20 operaciones y crea `eventos.log` en el directorio desde el que se ejecuta el comando. Si el archivo no se puede abrir, se avisa y el registro pasa a la consola.

`sistema.py` contiene las clases y validaciones; `main.py` contiene la simulación. Los datos existen solo mientras se ejecuta el programa. El registro contiene eventos y errores, no reconstruye los datos al reiniciar. La disponibilidad es un dato inicial del servicio: no se gestionan fechas, horarios ni conflictos entre reservas, pues el anexo no los define. Los valores y tarifas son ejemplos, no reglas reales de la empresa.

Las variantes de cálculo se implementan con argumentos opcionales, ya que Python no selecciona versiones de un método por número de argumentos. El descuento se aplica antes del impuesto. Una reserva puede pasar de pendiente a confirmada y procesada, o cancelarse mientras esté pendiente o confirmada. Una validación fallida no cambia el estado.

El trabajo colaborativo y el enlace del repositorio deben completarse con los datos reales del grupo. No se debe afirmar que otras personas participaron hasta que lo hayan hecho.
