# TP0: Ejercicio 3

Para la demostracion de este ejercicio se debera checkoutear al branch `feature/ejercicio_3` o al tag `ejercicio_3`

Se ofrece el script  `tester.sh` y eldirectorio `tester` con todos los archivos necesarios para ejecutar un test que determinara el correcto funcionamiento del servidor. Tester y servidor se ejecutan dentro de la misma red.

Se debe ejecutar el siguiente comando

```
./tester.sh
```

Lo cual imprimira la salida del test.

**Si el servidor funciona**
```
"Server is working correctly"
```

**Si el servidor NO funciona**
```
"Server is NOT working correctly"
```

**IMPORTANTE**
Se espera haber ejecutado `make docker-compose-up` para haber inicializado el ambiente de desarrollo antes de ejecutar el tester.
Para probar los distintos casos se puede frenar el contenedor del servidor con `docker-compose stop` o  `docker compose stop`