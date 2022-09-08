# TP0: Ejercicio 4

Para la demostracion de este ejercicio se debera checkoutear al branch `feature/ejercicio_4` o al tag `ejercicio_4`

Se han modificado cliente y servidor para que el programa termine de forma gracefully al recibir la signal SIGTERM.

Para probarlo levantar el entorno con 

```
make docker-compose-up
```

Luego frenar el entorno con 
```
docker-compose stop o docker compose stop
```

Finalmente se puede revisar los logs para chequear el apagado correcto mediante

```
make docker-compose-logs
```

o bien

```
docker logs server >& server.txt
docker logs client1 >& client1.txt
...
```