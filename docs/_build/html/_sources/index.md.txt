# Malla de Validación

Proyecto de Python con las clases y modulos requeridos para la validación de los datos adquiridos a través de los formularios de RIT

## Clase Validación

La clase validación se refiere al objeto que va almacenar la información relacionada a la validación de la información:
- Conjunto de Datos
- Malla de Validación (JSON)
- Resultados de la validación

```{eval-rst}  
.. autoclass:: MallaValidacionRuta.validacion
```

## Validación de la Información

Para realizar el proceso de validación del conjunto de datos, una vez se ha definido la clase validación con los parámetros definidos, se ejecuta el método validar_datos, este se va a encargar de descargar, normalizar y validar la información.

```{eval-rst}  
.. autofunction:: MallaValidacionRuta.validacion.validar_datos

```

## Funciones Adicionales

### Crear Malla de Validación en formato JSON
En el caso que la estructura de la malla de validación se encuentre en formato Excel, existe la función create_json_malla del modulo malla_functions que le va a permitir crear el archivo json con la malla de validación.
```{eval-rst}  
.. autofunction:: malla_functions.create_json_malla

```

### Malla de Validación
La siguiente función es la encargada de realizar la validación de los datos a partir de las condiciones de la Malla de Validación
```{eval-rst}  
.. autofunction:: malla_functions.malla_validacion

```