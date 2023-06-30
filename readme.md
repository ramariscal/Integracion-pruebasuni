## Instalación
*pre requesito: Docker https://www.docker.com/*
1. Dirígete a la carpeta raíz del proyecto /entrega

2. Ejetuta el comando: ```docker compose up -d```



## API tbk 
- URL Local http://localhost:8888/docs


### Metodo */execute_sale_fake*
Usado para hacer pruebas, todas las peticiones darán una transacción exitosa, ejemplo:
```
{
  "status": true,
  "id_transaction": 1684726454
}
```
Los datos o montos ingresados no son validados y no afectan a la tabla de tarjetas.

Ejemplo del Request se encuentra dentro de la documentación de swagger.

### Metodo */execute_sale*
Usado para produccion, las transacciones exitosas daran:
```
{
  "status": true,
  "id_transaction": 1684726454
}
```
Los datos o montos ingresados son validados y afectan a la tabla de tarjetas.

Ejemplo del Request se encuentra dentro de la documentación de swagger.
****

### Metodo */view_all_card*

Usado para entregar la lista de tarjetas con sus saldos 


# Errores controlados

El formato del *fecha_v* (ej: 05/23) incorrecto. 
```
{
    'status': False, 
    'msg': 'fecha_v con formato incorrecto'
}
```

El valor de *nro_tarjeta* no fue encorntrado en la tabla de tarjetas
```
{
    'status': False, 
    'msg': 'Tarjeta no encontrada'
}
```
Algun valor de tarjeta ingresada no coincide con la que esta almacenada en la base de datos (*nro_tarjeta*, *fecha_v*, *cvv*) 
```
{
    'status': False, 
    'msg': 'Los valores de la tarjeta no coinciden'
}
```

El monto a cobrar es mayor al que tiene de saldo la tarjeta ingresada
```
{
    'status': False, 
    'msg': 'Saldo insuficiente'
}
```

Error al prosesar el cobro, la operacion fue interrumpida por algun procedo interno del api
```
{
    'status': False, 
    'msg': 'Error en el cobro'
}
```

