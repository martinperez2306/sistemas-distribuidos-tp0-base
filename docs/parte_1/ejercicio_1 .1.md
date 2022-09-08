# TP0: Ejercicio 1.1

Para la demostracion de este ejercicio se debera checkoutear al branch `feature/ejercicio_1.1` o al tag `ejercicio_1.1`

Se ofrece el script `create_compose.sh` para crear el archivo **docker-compose-dev.yaml** un numero especifico de clientes.
Para hacerlo ejecutar el comando reemplazando la variable **CLIENTES** por la cantidad de clientes deseados

```
./create_compose.sh ${CLIENTES}
```

El mismo utiliza `templates` tanto de cliente como servidor para la generacion **docker-compose-dev.yaml** final.
Los templates se encuentran dentro del directorio `create_compose`
- **base_template.yaml**
- **clients_template.yaml**