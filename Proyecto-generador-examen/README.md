# Generador de Exámenes

**Generador de Exámenes** es una herramienta que facilita la creación de exámenes de respuesta múltiple y verdadero/falso con diferentes valores. Los exámenes se pueden descargar en formato texto para imprimir en papel o en formato XML para las aulas virtuales de [Moodle](https://moodle.org/).

## Funcionalidades

* Mezcla preguntas y respuestas
* Soporta preguntas de opción múltiple y verdadero/falso
* Permite configurar número de opciones por pregunta
* Admite penalización configurable por respuestas incorrectas
* Soporta preguntas con enunciados multilínea
* Permite valores aleatorios y cálculos en enunciados y respuestas
* Genera clave de corrección para exámenes en papel

## Licencia

Este proyecto se ofrece bajo licencia [CC BY,NC,SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es), quedando expresamente prohibido su uso comercial.

## Autores y Contribuciones

* **Javier F. Panadero**: Desarrollo del programa original, publicado en su blog [La Ciencia para todos](https://lacienciaparatodos.wordpress.com/).
* **Jorge Barata**: Desarrollo de la interfaz web para facilitar el uso sin Google Colab.
* **Juan Diego Rodríguez Cabrero**: Mejoras significativas en el programa básico, incluyendo:
  - Soporte para preguntas de verdadero/falso
  - Configuración del número de opciones por pregunta
  - Sistema de penalización configurable para respuestas incorrectas
  - Mejoras en la detección de preguntas
  - Optimizaciones en el procesamiento de archivos

## Instrucciones de uso

1. **Selección de tipos de preguntas**: Elige cuántas preguntas de cada tipo deseas incluir.
2. **Caracterización del examen**: Configura las opciones específicas para cada tipo de pregunta.
3. **Carga del archivo**: Sube tu archivo de texto con las preguntas en el formato adecuado.
4. **Generación y descarga**: El sistema genera y permite descargar el examen en el formato elegido.

Para más detalles, consulta el [Videotutorial](https://www.youtube.com/watch?v=FjHS49ZIDxs&list=PLzqyAKVt4MgM5T61zLBGef_QO_fVDhKHM).

## Formato del archivo de preguntas

### Estructura básica

```
entero,x1,20,25
real,x2,0.3,0.4
lista,x3,2,4,6,8
@@@@

¿Cuál es el cociente entre estos dos números @@ x1 @@, @@ x3 @@ ?
$$$Dividirlos y da como resultado: @@ x1/x3 @@
Restarlos y da como resultado: @@ x1-x3 @@
Ninguna de las anteriores

¿Estás de acuerdo con estas afirmaciones?
- El doble de @@ x2 @@ es @@ x2*2 @@
- El triple de @@ x2 @@ es @@ x2*3 @@ 
+++p
$$$Con las dos
Con ninguna
Con la primera sí, con la segunda no, sería @@ x2*4 @@
Ninguna de las anteriores

La suma de @@ x1 @@ más @@ x3 @@ es mayor que 30.
$$$Verdadero
Falso
```

### Explicación del formato

1. **Archivo**
   - Formato texto (`.txt`) con codificación UTF-8
   - Sin líneas en blanco al principio o final

2. **Cabecera de variables (opcional)**
   - Define variables para preguntas calculadas
   - Tipos: `entero`, `real`, `lista`
   - Termina con `@@@@` seguido de una línea en blanco

3. **Preguntas de opción múltiple**
   - Enunciado en la primera línea
   - Respuesta correcta marcada con `$$$` al inicio
   - Respuestas incorrectas en líneas siguientes
   - Separa preguntas con una línea en blanco

4. **Preguntas de verdadero/falso**
   - Enunciado en la primera línea
   - Respuesta correcta (`$$$Verdadero` o `$$$Falso`)
   - Respuesta incorrecta (sin `$$$`)
   - Separa preguntas con una línea en blanco

5. **Enunciados multilínea**
   - Escribe el enunciado completo
   - Añade `+++p` en una línea aparte al final del enunciado
   - Después coloca las respuestas normalmente

6. **Variables y expresiones**
   - Valor de variable: `@@ x1 @@`
   - Operaciones: `@@ x1/x3 @@`, `@@ x2*2 @@`
   - Expresiones condicionales: `@@ condición and "valor_verdadero" or "valor_falso" @@`
   - Utiliza sintaxis de Python para operaciones

7. **Elementos HTML e imágenes**
   - Puedes incluir código HTML en enunciados y respuestas
   - Ejemplo para imágenes: `<img src="URL_de_la_imagen" alt="Descripción" width="400" />`

## Formatos de salida

### Papel (.txt)
- Documento de texto con preguntas numeradas
- Variables constantes en todo el examen
- Incluye clave de corrección al final
- Respuestas con letras (a, b, c, d)

### Moodle (.xml)
- Archivo XML importable en Moodle
- Variables dinámicas para cada intento
- Penalización según configuración
- Soporte para preguntas calculadas con datasets

## Solución de problemas

- **Detección de preguntas**: Separa cada pregunta con exactamente una línea en blanco.
- **Variables**: Verifica que todas las variables usadas estén definidas en la cabecera.
- **Respuestas**: Asegúrate de que cada pregunta tenga una sola respuesta con `$$$`.
- **Codificación**: Guarda el archivo en UTF-8 para evitar problemas con caracteres especiales.

## Recursos adicionales

Para información técnica sobre el código, consulta los artículos:

- [Creación de exámenes respuesta múltiple con diferentes valores](https://lacienciaparatodos.wordpress.com/2021/12/12/creacion-de-examenes-respuesta-multiple-con-diferentes-valores/)
- [Programa para subir a Moodle preguntas de respuesta múltiple con valores variables](https://lacienciaparatodos.wordpress.com/2021/12/15/programa-para-subir-a-moodle-preguntas-de-respuesta-multiple-con-valores-variables/)