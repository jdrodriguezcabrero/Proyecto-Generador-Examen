# -*- coding: utf-8 -*-
"""
Generador de Exámenes Avanzado - Versión para Moodle
Basado en el script original de Javier Fernández Panadero
Ampliado para soportar diferentes tipos de preguntas y corregido para manejar expresiones condicionales
"""

from google.colab import files
import random
import re
import math
import json
import xml.sax.saxutils as saxutils

# Constantes para los tipos de preguntas
TIPO_MULTIRESPUESTA = "multirespuesta"
TIPO_VERDADERO_FALSO = "verdadero_falso"
TIPO_RESPUESTA_CORTA = "respuesta_corta"
TIPO_RELLENAR_ESPACIOS = "rellenar_espacios"

# Configuración global del examen (se reemplazará dinámicamente)
CONFIG_EXAMEN = {
    "questionTypes": {
        "multirespuesta": 5,
        "verdaderoFalso": 0,
        "respuestaCorta": 0,
        "rellenarEspacios": 0
    },
    "config": {
        "multirespuesta": {
            "opciones": 4,
            "penalizacion": True,
            "puntos": 1.0
        },
        "verdaderoFalso": {
            "penalizacion": True,
            "puntos": 1.0
        },
        "respuestaCorta": {
            "puntos": 1.0,
            "caseSensitive": False
        },
        "rellenarEspacios": {
            "puntos": 1.0
        }
    }
}

# Cargamos el archivo
uploaded = files.upload()
file = uploaded.popitem()[0]

with open(file, 'r') as archivo:
    texto_completo = archivo.read()

# Función para escapar texto para XML


def escape_xml(text):
    return saxutils.escape(str(text))

# Reemplaza la función evaluar_expresiones_condicionales en moodle.py con esta versión mejorada


def evaluar_expresiones_condicionales(texto):
    # Buscar todas las expresiones con el formato @@ expresión @@
    patron = r'@@ (.+?) @@'

    def reemplazo(match):
        expresion = match.group(1)

        try:
            # Intentar detectar si es una expresión condicional o un simple cálculo
            if ' and ' in expresion and ' or ' in expresion:
                # Es una expresión condicional del tipo "condición and valor_si_verdadero or valor_si_falso"
                partes = expresion.split(' and ')
                condicion = partes[0]
                resto = ' and '.join(partes[1:])

                partes_resto = resto.split(' or ')
                valor_verdadero = partes_resto[0].strip('"\'')
                valor_falso = ' or '.join(partes_resto[1:]).strip('"\'')

                # Evaluar la condición
                resultado_condicion = eval(condicion)
                return valor_verdadero if resultado_condicion else valor_falso
            else:
                # Es una expresión simple, solo evaluarla
                resultado = eval(expresion)
                return str(resultado)
        except Exception as e:
            print(f"Error al evaluar expresión: {expresion}, {e}")
            # En lugar de mostrar [ERROR], intentar devolver la expresión original
            return str(expresion)

    # Reemplazar todas las ocurrencias
    return re.sub(patron, reemplazo, texto)

# Función para procesar la cabecera con variables si existe


def procesar_cabecera(texto_completo):
    marca_def = '\n@@@@\n\n'

    if marca_def in texto_completo:
        rompe_cabecera = texto_completo.split(marca_def)
        cabecera = rompe_cabecera[0]
        texto = rompe_cabecera[1]

        # Procesar variables para el formato XML de Moodle
        lineas = cabecera.split('\n')
        variables = []
        data = []

        for linea in lineas:
            elementos = linea.split(',')
            variables.append(elementos)

        longitud_serie = 10  # Longitud máxima de los datasets

        for variable in variables:
            if variable[0] == 'entero':
                valor = [variable[1]]
                numericos = list(map(int, variable[2:4]))
                valor += numericos
                minimo = valor[1]
                maximo = valor[2]
                for i in range(longitud_serie):
                    valor.append(random.randint(minimo, maximo))
                data.append(valor)

            elif variable[0] == 'real':
                valor = [variable[1]]
                numericos = list(map(float, variable[2:4]))
                valor += numericos
                minimo = valor[1]
                maximo = valor[2]
                for i in range(longitud_serie):
                    x = random.uniform(minimo, maximo)
                    decimales_para_significativas = 2 + \
                        math.ceil(-(math.log10(x)))
                    x = round(x, decimales_para_significativas)
                    valor.append(x)
                data.append(valor)

            elif variable[0] == 'lista':
                elegibles = variable[2:]
                elegibles = list(map(float, elegibles))
                max_elegibles = max(elegibles)
                min_elegibles = min(elegibles)

                if len(elegibles) < longitud_serie:
                    k = longitud_serie // len(elegibles)
                    elegibles += elegibles * k

                valor = [variable[1], min_elegibles, max_elegibles] + elegibles
                data.append(valor)

        # Primero, evaluar cualquier expresión condicional en el texto
        texto = evaluar_expresiones_condicionales(texto)

        # Luego, procesar las variables normales
        ocurrencias = re.findall('@@ (.+?) @@', texto)

        for i in range(len(ocurrencias)):
            for variable in variables:
                ocurrencias[i] = ocurrencias[i].replace(
                    variable[1], '{' + variable[1] + '}')

        for i in range(len(ocurrencias)):
            ocurrencias[i] = '{=' + ocurrencias[i] + '}'

        for i in range(len(ocurrencias)):
            texto = re.sub('@@ (.+?) @@', ocurrencias[i], texto, 1)

        return texto, data
    else:
        # Evaluar expresiones condicionales incluso si no hay cabecera
        texto = evaluar_expresiones_condicionales(texto_completo)
        return texto, []

# Función para separar y clasificar las preguntas por tipo


def clasificar_preguntas(texto_completo):
    # Primero procesamos cualquier variable en el texto
    texto, data = procesar_cabecera(texto_completo)

    # Separamos el texto en preguntas
    texto_preguntas = texto.split(sep='\n\n')

    # Analizar cada pregunta para determinar su tipo y estructura
    preguntas = {
        TIPO_MULTIRESPUESTA: [],
        TIPO_VERDADERO_FALSO: [],
        TIPO_RESPUESTA_CORTA: [],
        TIPO_RELLENAR_ESPACIOS: []
    }

    for pregunta in texto_preguntas:
        # Ignorar líneas que parecen ser comentarios o separadores
        if not pregunta.strip() or pregunta.strip().startswith('//'):
            continue

        # Si la pregunta contiene la marca de pregunta multilínea
        if '+++p\n' in pregunta:
            partes = pregunta.split('+++p\n')
            enunciado = partes[0]
            respuestas = partes[1].split('\n')
        else:
            # Dividir por líneas y separar enunciado de respuestas
            lineas = pregunta.split('\n')
            enunciado = lineas[0]
            respuestas = lineas[1:] if len(lineas) > 1 else []

        # Si no hay respuestas, continuar al siguiente
        if not respuestas:
            continue

        # Identificar bloques de tipos específicos (indicados por comentarios)
        tipo_indicado = None
        if enunciado.strip().startswith('// PREGUNTAS DE OPCIÓN MÚLTIPLE'):
            tipo_indicado = TIPO_MULTIRESPUESTA
            continue  # Es un marcador, no una pregunta real
        elif enunciado.strip().startswith('// PREGUNTAS DE VERDADERO O FALSO'):
            tipo_indicado = TIPO_VERDADERO_FALSO
            continue  # Es un marcador, no una pregunta real
        elif enunciado.strip().startswith('// PREGUNTAS DE RESPUESTA CORTA'):
            tipo_indicado = TIPO_RESPUESTA_CORTA
            continue  # Es un marcador, no una pregunta real
        elif enunciado.strip().startswith('// PREGUNTAS DE RELLENAR ESPACIOS'):
            tipo_indicado = TIPO_RELLENAR_ESPACIOS
            continue  # Es un marcador, no una pregunta real

        # Clasificar según características específicas de cada tipo
        # Verificar primero si hay respuestas marcadas como correctas
        if any(resp.startswith('$$$') for resp in respuestas):
            # Respuesta corta: si el enunciado tiene "?" y hay solo una respuesta
            if len(respuestas) == 1 and '?' in enunciado:
                preguntas[TIPO_RESPUESTA_CORTA].append({
                    'enunciado': enunciado,
                    'respuestas': respuestas
                })
            # Rellenar espacios: si el enunciado contiene guiones bajos (espacios para rellenar)
            elif "____" in enunciado or "___" in enunciado:
                preguntas[TIPO_RELLENAR_ESPACIOS].append({
                    'enunciado': enunciado,
                    'respuestas': respuestas
                })
            # Verdadero/Falso: exactamente 2 opciones y una es "Verdadero" o "Falso"
            elif len(respuestas) == 2 and any(
                r.strip().lower() in ["verdadero", "true", "falso", "false"]
                for r in [r[3:] if r.startswith('$$$') else r for r in respuestas]
            ):
                preguntas[TIPO_VERDADERO_FALSO].append({
                    'enunciado': enunciado,
                    'respuestas': respuestas
                })
            # Por defecto, multirespuesta
            else:
                preguntas[TIPO_MULTIRESPUESTA].append({
                    'enunciado': enunciado,
                    'respuestas': respuestas
                })

    # Imprimir estadísticas para depuración
    print(
        f"Preguntas de opción múltiple: {len(preguntas[TIPO_MULTIRESPUESTA])}")
    print(
        f"Preguntas de verdadero/falso: {len(preguntas[TIPO_VERDADERO_FALSO])}")
    print(
        f"Preguntas de respuesta corta: {len(preguntas[TIPO_RESPUESTA_CORTA])}")
    print(
        f"Preguntas de rellenar espacios: {len(preguntas[TIPO_RELLENAR_ESPACIOS])}")

    return preguntas, data

# Función para seleccionar preguntas según la configuración del examen


def seleccionar_preguntas(preguntas_clasificadas, config):
    seleccionadas = []

    # Seleccionar preguntas de cada tipo según la configuración
    tipos_cantidades = [
        (TIPO_MULTIRESPUESTA, config["questionTypes"]["multirespuesta"]),
        (TIPO_VERDADERO_FALSO, config["questionTypes"]["verdaderoFalso"]),
        (TIPO_RESPUESTA_CORTA, config["questionTypes"]["respuestaCorta"]),
        (TIPO_RELLENAR_ESPACIOS, config["questionTypes"]["rellenarEspacios"])
    ]

    # Primera pasada: seleccionar preguntas disponibles de cada tipo
    for tipo, cantidad in tipos_cantidades:
        if cantidad > 0:
            disponibles = preguntas_clasificadas[tipo].copy()
            random.shuffle(disponibles)

            # Verificar si hay suficientes preguntas
            preguntas_disponibles = len(disponibles)
            if preguntas_disponibles < cantidad:
                print(
                    f"Advertencia: Se solicitaron {cantidad} preguntas de tipo {tipo}, pero solo hay {preguntas_disponibles} disponibles.")

            # Tomar solo el número solicitado, o todas si hay menos
            preguntas_seleccionadas = disponibles[:min(
                cantidad, preguntas_disponibles)]
            # Añadir tipo a cada pregunta para identificarla después
            for p in preguntas_seleccionadas:
                p['tipo'] = tipo
            seleccionadas.extend(preguntas_seleccionadas)

    # Mezclar todas las preguntas seleccionadas
    random.shuffle(seleccionadas)

    # Imprimir estadísticas de selección
    tipos_seleccionados = {}
    for pregunta in seleccionadas:
        tipo = pregunta['tipo']
        tipos_seleccionados[tipo] = tipos_seleccionados.get(tipo, 0) + 1

    print("Preguntas seleccionadas por tipo:")
    for tipo, cantidad in tipos_cantidades:
        print(
            f"- {tipo}: {tipos_seleccionados.get(tipo, 0)} de {cantidad} solicitadas")

    return seleccionadas


def generar_xml_multirespuesta(pregunta, idx, data, config):
    # Determinar si hay variables calculadas
    tiene_calculos = len(data) > 0

    # Tipo de pregunta (calculatedmulti si hay variables, multichoice si no)
    tipo_pregunta = "calculatedmulti" if tiene_calculos else "multichoice"

    # Crear el XML base para la pregunta
    ordinal = str(idx + 1) if idx >= 9 else '0' + str(idx + 1)
    xml = f'''<!-- Pregunta {ordinal} -->
  <question type="{tipo_pregunta}">
    <name>
      <text>Pregunta {ordinal}</text>
    </name>
    <questiontext format="html">
      <text><![CDATA[<p>{escape_xml(pregunta['enunciado'])}</p>]]></text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>{config['config']['multirespuesta']['puntos']}</defaultgrade>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <synchronize>0</synchronize>
    <single>1</single>
    <answernumbering>abc</answernumbering>
    <shuffleanswers>1</shuffleanswers>
    <correctfeedback>
      <text></text>
    </correctfeedback>
    <partiallycorrectfeedback>
      <text></text>
    </partiallycorrectfeedback>
    <incorrectfeedback>
      <text></text>
    </incorrectfeedback>
'''

    # Añadir las respuestas
    respuestas = pregunta['respuestas'].copy()
    num_respuestas = len(respuestas)

    # Calcular la penalización por respuesta incorrecta
    if config['config']['multirespuesta']['penalizacion']:
        # Usar el valor de penalización configurado
        valor_penalizacion = config['config']['multirespuesta']['valorPenalizacion']
        # Convertir a porcentaje negativo
        resta = round(-100 * valor_penalizacion, 5)
    else:
        resta = 0

    for idx_resp, respuesta in enumerate(respuestas):
        if respuesta.startswith('$$$'):
            # Respuesta correcta
            xml += f'''<answer fraction="100">
    <text>{escape_xml(respuesta[3:])}</text>
'''
        else:
            # Respuesta incorrecta
            xml += f'''<answer fraction="{resta}">
    <text>{escape_xml(respuesta)}</text>
'''

        # Si hay cálculos, añadir la información de tolerancia
        if tiene_calculos:
            xml += '''    <tolerance>0.01</tolerance>
    <tolerancetype>1</tolerancetype>
    <correctanswerformat>2</correctanswerformat>
    <correctanswerlength>3</correctanswerlength>
'''

        xml += '''    <feedback format="html">
<text></text>
    </feedback>
</answer>
'''

    # Añadir configuración de unidades
    xml += '''<unitgradingtype>0</unitgradingtype>
    <unitpenalty>0.1000000</unitpenalty>
    <showunits>3</showunits>
    <unitsleft>0</unitsleft>
'''

    # Si hay variables calculadas, añadir los datasets
    if tiene_calculos:
        xml += add_datasets_xml(data)

    # Cerrar la etiqueta de pregunta
    xml += '</question>\n'

    return xml


def generar_xml_verdadero_falso(pregunta, idx, data, config):
    # Crear el XML base para la pregunta
    ordinal = str(idx + 1) if idx >= 9 else '0' + str(idx + 1)
    xml = f'''<!-- Pregunta {ordinal} -->
  <question type="truefalse">
    <name>
      <text>Pregunta {ordinal}</text>
    </name>
    <questiontext format="html">
      <text><![CDATA[<p>{escape_xml(pregunta['enunciado'])}</p>]]></text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>{config['config']['verdaderoFalso']['puntos']}</defaultgrade>
    <penalty>{config['config']['verdaderoFalso']['valorPenalizacion'] if config['config']['verdaderoFalso']['penalizacion'] else 0}</penalty>
    <hidden>0</hidden>
'''

    # Encontrar la respuesta correcta
    respuestas = pregunta['respuestas'].copy()
    respuesta_correcta = None

    for resp in respuestas:
        if resp.startswith('$$$'):
            respuesta_correcta = resp[3:].strip().lower()
            break

    # Determinar si la respuesta correcta es "Verdadero"
    es_verdadero = respuesta_correcta in ["verdadero", "true"]

    # Añadir las respuestas
    xml += f'''    <answer fraction="{100 if es_verdadero else 0}">
      <text>true</text>
      <feedback format="html">
        <text></text>
      </feedback>
    </answer>
    <answer fraction="{0 if es_verdadero else 100}">
      <text>false</text>
      <feedback format="html">
        <text></text>
      </feedback>
    </answer>
  </question>
'''

    return xml

# Función para generar el XML para una pregunta de respuesta corta


def generar_xml_respuesta_corta(pregunta, idx, data, config):
    # Crear el XML base para la pregunta
    ordinal = str(idx + 1) if idx >= 9 else '0' + str(idx + 1)
    xml = f'''<!-- Pregunta {ordinal} -->
  <question type="shortanswer">
    <name>
      <text>Pregunta {ordinal}</text>
    </name>
    <questiontext format="html">
      <text><![CDATA[<p>{escape_xml(pregunta['enunciado'])}</p>]]></text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>{config['config']['respuestaCorta']['puntos']}</defaultgrade>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <usecase>{1 if config['config']['respuestaCorta']['caseSensitive'] else 0}</usecase>
'''

    # Encontrar la respuesta correcta
    respuestas = pregunta['respuestas'].copy()
    respuesta_correcta = None

    for resp in respuestas:
        if resp.startswith('$$$'):
            respuesta_correcta = resp[3:]
            break

    # Añadir la respuesta correcta
    xml += f'''    <answer fraction="100">
      <text>{escape_xml(respuesta_correcta)}</text>
      <feedback format="html">
        <text></text>
      </feedback>
    </answer>
  </question>
'''

    return xml

# Función para generar el XML para una pregunta de rellenar espacios


def generar_xml_rellenar_espacios(pregunta, idx, data, config):
    # Crear el XML base para la pregunta
    ordinal = str(idx + 1) if idx >= 9 else '0' + str(idx + 1)

    # Preparar el enunciado sustituyendo los espacios en blanco por [...]
    enunciado = pregunta['enunciado'].replace("_____", "[...]")
    enunciado = enunciado.replace("____", "[...]")
    enunciado = enunciado.replace("___", "[...]")

    xml = f'''<!-- Pregunta {ordinal} -->
  <question type="cloze">
    <name>
      <text>Pregunta {ordinal}</text>
    </name>
    <questiontext format="html">
      <text><![CDATA[<p>
'''

    # Encontrar la respuesta correcta
    respuestas = pregunta['respuestas'].copy()
    respuesta_correcta = None

    for resp in respuestas:
        if resp.startswith('$$$'):
            respuesta_correcta = resp[3:]
            break

    # Crear la pregunta con el formato de cloze
    # Reemplazamos los [...] por la entrada de respuesta corta
    enunciado_cloze = enunciado.replace(
        "[...]", f"{{1:SHORTANSWER:{escape_xml(respuesta_correcta)}}}")

    xml += f'''{enunciado_cloze}
      </p>]]></text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <shuffleanswers>0</shuffleanswers>
  </question>
'''

    return xml

# Función para añadir la información de datasets para preguntas calculadas


def add_datasets_xml(data):
    xml = '''<dataset_definitions>
'''

    for variable in data:
        xml += f'''<dataset_definition>
    <status><text>private</text>
</status>
    <name><text>{variable[0]}</text>
</name>
    <type>calculatedmulti</type>
    <distribution><text>uniform</text>
</distribution>
    <minimum><text>{variable[1]}</text>
</minimum>
    <maximum><text>{variable[2]}</text>
</maximum>
'''

        # Calcular decimales para que muestre hasta la tercera cifra significativa
        if variable[1] != 0:
            decimales = max(0, 2 + math.ceil(-(math.log10(abs(variable[1])))))
        else:
            decimales = 2

        xml += f'''    <decimals><text>{decimales}</text>
</decimals>
'''

        # Añadir los valores de la variable
        long_serie = len(variable) - 3
        xml += f'''    <itemcount>{long_serie}</itemcount>
    <dataset_items>
'''

        for i, valor in enumerate(variable[3:]):
            xml += f'''        <dataset_item>
           <number>{i+1}</number>
           <value>{valor}</value>
        </dataset_item>
'''

        xml += f'''    </dataset_items>
    <number_of_items>{long_serie}</number_of_items>
</dataset_definition>
'''

    xml += '</dataset_definitions>\n'
    return xml

# Función para generar el examen completo en formato XML para Moodle


def generar_examen_xml(preguntas_seleccionadas, data, config):
    # Cabecera del XML
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<quiz>
'''

    # Añadir cada pregunta según su tipo
    for idx, pregunta in enumerate(preguntas_seleccionadas):
        tipo = pregunta.get('tipo', TIPO_MULTIRESPUESTA)

        if tipo == TIPO_MULTIRESPUESTA:
            xml += generar_xml_multirespuesta(pregunta, idx, data, config)
        elif tipo == TIPO_VERDADERO_FALSO:
            xml += generar_xml_verdadero_falso(pregunta, idx, data, config)
        elif tipo == TIPO_RESPUESTA_CORTA:
            xml += generar_xml_respuesta_corta(pregunta, idx, data, config)
        elif tipo == TIPO_RELLENAR_ESPACIOS:
            xml += generar_xml_rellenar_espacios(pregunta, idx, data, config)

    # Cerrar el documento XML
    xml += '</quiz>\n'

    return xml

# Función principal


def main():
    # Procesar el archivo de entrada
    preguntas_clasificadas, data = clasificar_preguntas(texto_completo)

    # Seleccionar preguntas según la configuración
    preguntas_seleccionadas = seleccionar_preguntas(
        preguntas_clasificadas, CONFIG_EXAMEN)

    # Generar el examen en formato XML para Moodle
    examen_xml = generar_examen_xml(
        preguntas_seleccionadas, data, CONFIG_EXAMEN)

    # Guardar el examen en un archivo
    with open("salida.xml", "w", encoding="utf-8") as archivo:
        archivo.write(examen_xml)

    # Descargar el archivo
    files.download("salida.xml")

    return "Examen generado correctamente en formato XML para Moodle"


# Ejecutar el programa
result = main()
print(result)
