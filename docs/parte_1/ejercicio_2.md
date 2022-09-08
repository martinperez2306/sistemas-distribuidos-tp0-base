# TP0: Ejercicio 2

Para la demostracion de este ejercicio se debera checkoutear al branch `feature/ejercicio_2` o al tag `ejercicio_2`

Se ofrece el directorio `config` para almacenar las configuraciones tanto del `client` como el `server`.
Se modificaron los templtes para soportar volumenes

**En el servidor**
```
volumes:
      - "./config/server:/config"
```

**En el cliente**
```
volumes:
      - "./config/client:/config"
```