# Protocolo de comunicacion

Se establecio el siguiente protocolo de comunicacion para la realizacion del trabajo practico.


## Modulo Communicator

El modulo `Communicator` es el encargado de enviar mensajes entre cliente y servidor.
Se implementa tanto en el cliente (golang) como en el servidor (python)

Se rige bajo los siguientes principios.

1. Los mensajes de señales entre cliente y servidor tienen un tamaño fijo de 13 (trece).
    a. Codigo solicitud de respuesta = 0000000000000
    b. Codigo confirmacion de respuesta = 0000000000001
    c. Codigo de cierre de conexion = 9999999999999 

2. Cliente y servidor estableceran contratos para determinar el tamaño del mensaje que se envia, tanto en la solicitud como la respuesta.

3. El tamaño maximo permitido para enviar es de 12 (trece). Es decir, como maximo se puede enviar un mensaje de 999999999999 caracteres.

3. En cada Request que el cliente envie al servidor se seguiran estos pasos.

    a. Cliente envia el tamaño del mensaje, el servidor lo recibe y envia el mismo tamaño para confirmar que puede recibirlo

    b. El cliente evalua si el tamaño que envio es el mismo que el que recibio. Si es el mismo envia el mensaje, de lo contrario loguea y cierra la conexion.

    c. El servidor responde el mismo mensaje que recibio para confirmar su recepcion, asi el cliente sabra que el mensaje a llegado correcto al servidor.

    d. Luego el cliente envia un mensaje para solicitar la respuesta con el codigo 0000000000000. El servidor lo recibe y le envia la el tamaño del mensaje de respuesta. Al igual que la solicitud del cliente, el tamaño maximo de la respuesta tendra un maximo de 999999999999

    e. El cliente recibe el tamaño de la respuesta y envia el mensaje 0000000000001 para confirmar que puede recibir la informacion.

    f. El servidor recibe 0000000000001 y envia la data. Luego el servidor sabe que tiene que esperar un codigo de cierre de conexion 9999999999999 (trece 9s).

    g. El cliente al recibir la respuesta envia 9999999999999. El servidor recibe el codigo y cierra la conexion.

    h. El cliente cierra la conexion.

4. Dado los puntos anteriores, cada Request que envia el cliente se realiza en una unica conexion, al recibir la respuesta la cierra. Si se desea enviar mas request, el `Communicador` iniciaria una nueva conexion.

## Modulo Client - Controller

Desde el cliente y el servidor se utilizan los modulos Client y Controller, respectivamente, para interpretar cada request.

Controller espera un mensaje de la estructura

```
REQUEST_CLI[id_cliente]REQUEST_NAME[nombre_request]REQUEST_BODY[lo_que_sea]
```

Dado el tipo de REQUEST_NAME que reciba, se delegara a la correspondiente capa de negocio para resolverlo.

Cliente sabe que tiene que mandar la estructura anterior, pero no espera ninguna estructura, solamente la respuesta del servidor. El servidor se asegura de responder con lo que el cliente necesita.

Luego el negocio del cliente sabe como interpretar la respuesta del servidor, dependiendo de la request que se envio.

## Negocio

Se soportan 2 request en el servidor
1. GET_WINNERS
2. GET_AGENCIES