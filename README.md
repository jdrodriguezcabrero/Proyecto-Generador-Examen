## Generador de Exámenes


**Generador de Exámenes** es un herramienta que facilita la **creación de exámenes respuesta múltiple con diferentes valores**.

Los exámenes se pueden descargar en formato texto para imprimir en papel o en formato XML para las aulas virtuales de [Moodle](https://moodle.org/).

Ofrece las siguientes funcionalidades:

* Mezcla preguntas (número arbitrario)
* Mezcla respuestas (número arbitrario)
* Admite preguntas multilínea (OPCIONAL)
* Admite valores aleatorios y cálculos con ellos en enunciados y respuestas. (OPCIONAL)
* Da la clave de corrección

La idea es que podáis escribir el examen de manera **cómoda e intuitiva**.

📝 INSTRUCCIONES DE USO - GENERADOR DE EXÁMENES

Este proyecto necesita un servidor local para funcionar correctamente. Si abres el archivo index.html directamente (doble clic), algunos navegadores bloquearán la carga de módulos esenciales como Pyodide.

📦 CONTENIDO NECESARIO:
Asegúrate de que todos estos archivos estén en la misma carpeta:
- index.html
- pyodide.js
- pyodide.asm.js
- pyodide.asm.wasm
- pyodide.asm.data
- pyodide_py.tar
- distutils.tar
- packages.json
- pdf.min.js
- pico.min.css
- app.js
- papel.py
- moodle.py
- examen.txt (y cualquier archivo de preguntas)

🚀 PASOS PARA USAR LA APLICACIÓN

⚠️ NOTA IMPORTANTE SOBRE PERMISOS

Al hacer doble clic sobre el archivo `Iniciar_Servidor_Examenes.bat`, es posible que Windows muestre advertencias de seguridad como:

- "¿Deseas permitir que esta aplicación realice cambios en el dispositivo?"
- O bien, el antivirus puede preguntar si deseas ejecutar un archivo de comandos.

Esto es normal porque el archivo `.bat` intenta ejecutar un servidor local en tu propio equipo.

✅ Qué debes hacer:
- Asegúrate de que el archivo proviene de una fuente confiable (este proyecto).
- Haz clic en “Sí” o “Permitir” para continuar.
- Si ves advertencias de tu antivirus, puedes marcar el archivo como seguro o confiar temporalmente.

El script **no instala nada** ni accede a internet, simplemente ejecuta `python -m http.server` en la carpeta actual y abre el navegador.



1. **Requisitos previos**
   - Tener Python instalado en el equipo (https://www.python.org)

2. **Iniciar el servidor local**
   - Haz doble clic en el archivo: `Iniciar_Servidor_Examenes.bat`

3. **Abrir en el navegador**
   - El navegador se abrirá automáticamente en: http://localhost:8000
   - Allí podrás usar el Generador de Exámenes sin errores.

❗IMPORTANTE:
- No abras `index.html` directamente desde el explorador de archivos (file:///...), ya que los navegadores bloquean módulos ES6 desde rutas locales.
- Si ves errores relacionados con `pyodide` o `import`, asegúrate de estar usando el servidor local.

📧 Contacto:
Para dudas, contactar con el desarrollador del proyecto.


---

## 🔧 Requisitos técnicos para ejecutar correctamente

Algunos navegadores (especialmente Chrome) **bloquean la ejecución de módulos locales desde archivos `file:///`**, lo que puede impedir que el proyecto funcione correctamente si se abre con doble clic.

Para garantizar el funcionamiento completo:

### ✅ Opción recomendada: Usar un servidor local

1. Asegúrate de tener Python instalado.
2. Usa el archivo `Iniciar_Servidor_Examenes.bat` incluido en el proyecto.
   - Al ejecutarlo, abrirá automáticamente el navegador en la dirección correcta.
   - Esto elimina errores como: `pyodide is null`, `La URI de origen del módulo no está permitida`, etc.

Si lo prefieres, puedes iniciar el servidor manualmente con:

```bash
python -m http.server 8000
```

y luego ir a: http://localhost:8000

---

#### Licencia

**Generador de Exámenes** se ofrece bajo licencia [CC BY,NC,SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es), quedando expresamente prohibido su uso comercial.

#### Autores

El programa fue desarrollado por [Javier F. Panadero](https://twitter.com/javierfpanadero) y publicado en su blog [La Ciencia
para todos](https://lacienciaparatodos.wordpress.com/).

Posteriormente, esta web fue desarrollada por [Jorge Barata](https://twitter.com/neuralhacker), facilitando el uso del programa sin necesidad de usar Google Colab.

Además, [Juan Diego Rodríguez Cabrero] ha añadido diversas funcionalidades al programa, entre ellas:

- Preguntas de verdadero o falso

- Preguntas de respuesta corta

- Preguntas de rellenar espacios

Selección del número y tipo de preguntas

Caracterización de las preguntas, incluyendo:

- Número de respuestas en preguntas de opción múltiple

- Penalización o no de respuesta incorrecta

- Puntuación de la respuesta correcta

Generación de prompts para IA, permitiendo:

- Seleccionar tema y nivel de dificultad

- Subir tus propios apuntes como base de generación

## Instrucciones de uso

1.  Prepara el examen de entrada (<a href="examen2.txt" download="examen.txt">ejemplo</a>)
2.  Elige un formato (`Papel` o `Moodle`) y sube el examen de entrada.
3.  Descarga el examen de salida.

Para aprender a usar esta herramienta recomendamos consultar el [Videotutorial](
https://www.youtube.com/watch?v=FjHS49ZIDxs&list=PLzqyAKVt4MgM5T61zLBGef_QO_fVDhKHM).


#### Ejemplo de exámen de entrada

```
entero,x1,20,25
real,x2,0.3,0.4
lista,x3,2,4,6,8
@@@@

¿Cuál es el cociente entre estos dos números @@ x1 @@, @@ x3 @@ ?
Dividirlos y da como resultado: @@ x1/x3 @@
Restarlos y da como resultado: @@ x1-x3 @@
Ninguna de las anteriores

¿Estás de acuerdo con estas afirmaciones?
- El doble de @@ x2 @@ es @@ x2*2 @@
- El triple de @@ x2 @@ es @@ x2*3 @@ 
+++p
Con las dos
Con ninguna
Con la primera sí, con la segunda no, sería @@ x2*4 @@
Ninguna de las anteriores
```

#### Explicación rápida

- El archivo de entrada debe estar en formato texto (`.txt`).
- No se dejan líneas en blanco ni al principio ni al final del archivo.
- Sin cabecera, examen tipo test habitual.
- Cabecera para definir variables, su tipo y su rango. Termina la cabecera con cuatro arrobas.
- Preguntas: Primera línea, enunciado. Segunda, respuesta correcta. Después, respuestas incorrectas.
- Si el enunciado tiene más de una línea. Al final del enunciado se añade `+++p`
- Si se quiere usar el valor de una variable se pone entre pareja de arrobas: `@@ x1 @@`
- Si se quiere usar un cálculo con una variable, también entre pareja de arrobas: `@@ x2*3 @@`
- En el examen en papel las variables tendrán el mismo valor en todo el examen. En Moodle, cambian de valor en cada pregunta.
- **Guárdese en un archivo txt con codificación UTF-8**
- Si quieres usar imágenes, sólo tienes que incluir en el enunciado esta etiqueta hmtl
![image](https://user-images.githubusercontent.com/91572665/206852862-8564c491-6f3d-4e7d-8c3f-9644d3eb9926.png)

#### Explicación detallada

1. Debe estar en formato texto (`.txt`)
2. Debe guardarse con codificación UTF-8
3. Si quieres usar preguntas calculadas debes empezar el archivo con una cabecera declarándolas. Sin cabecera, será un examen test normal.
    - Sin líneas en blanco antes de la cabecera
    - Tipo: `entero`, `real` (decimal), `lista` (lista de valores)
    - Nombre de la variable. Puede hacerse con palabras, pero usar `x1`, `x2`, `x3`... es posible que te ahorre confusiones
    - Valores mínimo y máximo (si son enteros o reales), lista de valores si es una lista.
    - En cada examen los valores de las variables serán diferentes, dentro de los rangos establecidos.
    - Termina la cabecera con cuatro arrobas y una línea en blanco.
4. Preguntas:
    - La primera línea es el enunciado
    - La segunda línea es la respuesta correcta.
    - Las siguientes líneas son respuestas incorrectas. Puedes poner tantas como quieras. En Moodle restará al contestarlas lo correspondiente al número de opciones)
    - Cuando acaba la pregunta y sus respuestas se pone una línea en blanco.
5. Preguntas con enunciados de más de una línea.
    - Pones todas las líneas del enunciado y después de la última pones `+++p` (indicando que ahí acaba el párrafo del enunciado).
    - A partir de ahí pones las respuestas como en una pregunta normal.
6. Uso de las variables
    - Si pones `x1`, en el examen aparecerá "x1"
    - Si quieres que salga su valor, debes poner `@@ x1 @@`
    - También puedes hacer operaciones con ellas y que se muestre su valor, por ejemplo dividir la variable `x1` entre `x3` sería así: `@@ x1/x3 @@` (para las operaciones, usaremos la sintaxis de Python, que en operaciones sencillas sería la habitual. Para otras consultas, por ejemplo `x2` al cuadrado sería `x**2`) 
7. El programa va a mezclar tanto preguntas como respuestas.
8. Corrección
    - En el examen en papel te sale al final la clave de corrección
    - En el examen de moodle se marca como correcta la primera respuesta que pusiste y se resta `1/(n-1)` por respuesta incorrecta, siendo `n` el número de respuestas. Digamos 1/3 en cuatro opciones, 1/4 en cinco opciones, etc.
9. Si necesitas incluir imágenes, tendrás que hacerlo a mano. Puedes poner en el enunciado Fig 1., Fig 2., etc. y luego añadir un conjunto de figuras o ir incluyéndolas a mano y borrando la referencia. 
10. Si vas a hacer un examen sobre HTML u otro lenguaje de marcado, puede que tengas problemas y el programa confunda tus etiquetas con las suyas.
11. Si quieres usar imágenes, sólo tienes que incluir en el enunciado esta etiqueta hmtl
![image](https://user-images.githubusercontent.com/91572665/206852862-8564c491-6f3d-4e7d-8c3f-9644d3eb9926.png) Si conoces html puedes añadir texto alternativo, tamaño y el resto de atributos. También puedes intentar añadir más características html a los enunciados o respuestas, creo que funcionarán bien.



#### Código

Para más información sobre el código, consulte los artículos publicados en el blog "La Ciencia para todos":

-   [Creación de exámenes respuesta múltiple con diferentes valores
](https://lacienciaparatodos.wordpress.com/2021/12/12/creacion-de-examenes-respuesta-multiple-con-diferentes-valores/)
-   [Programa para subir a Moodle preguntas de respuesta múltiple con valores variables](https://lacienciaparatodos.wordpress.com/2021/12/15/programa-para-subir-a-moodle-preguntas-de-respuesta-multiple-con-valores-variables/)


