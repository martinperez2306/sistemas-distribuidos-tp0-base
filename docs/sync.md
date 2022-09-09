# Herramientas de sincronizacion

Se utilizaron **Semaforos Binarios (Mutex)** como herramientas de sincronizacion.

Los mismos se usaron en las entidades

1. WinnersRepository
2. WinnersTrack

Las mismas corresponden a entidades que contienen recursos compartidos los cuales distintos procesos podrian competir.

1. El archivo donde se persisten los datos.
2. El trackeo de las agencias.

### Winners Repository

Para este caso se usa el Mutex para controlar el acceso de lectura y escritura del archivo.

### Winners Track

Para este caso se usa el Mutex para controlar el acceso a lectura y escritura de una lista que indica si hay agencias que aun estan esperando el procesamiento de su respuesta.

Esto sirve para poder enviar una respuesta parcial a los clientes con la cantidad de agencias en espera de su informacion.