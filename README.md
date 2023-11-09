# Malla de Validacion
**Código de la Estructura de Validación de la información caracterizada desde RIT para la DIP**

En este repositorio se encuentra la estructura utilizada para la validación de los datos recibidos a través del Aplicativo RIT.

El funcionamiento de este código consiste en definir la estructura de la encuesta que viene desde un archivo JSON, en un formato excel que le va a permitir al script de Python entender las distintas de validaciones que debe realizar.


Este Libro de Excel contiene dos hojas que definen los siguientes parámetros:

- En la primera hoja se deben almacenar las condiciones de respuesta de cada pregunta, es decir, cuáles son las condiciones que se deben cumplir para que el encuestado deba contestar la respectiva pregunta.
- En la segunda hoja se almacenan los distintos valores que puede tomar cada pregunta, ya sea desde una lista de valores hasta un condicional de tipo expresión regular.


Para realizar la validación de una encuesta nueva, debe añadir un nuevo libro de Excel en la carpeta ____, según la estructura que se encuentra en _____. Una vez la ha definido, ingrese al script de Python y añada la ruta completa de la ubicación del archivo. 