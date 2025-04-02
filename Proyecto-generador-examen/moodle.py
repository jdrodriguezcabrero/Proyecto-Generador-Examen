# -*- coding: utf-8 -*-
"""
Generador de Exámenes Avanzado - Versión para Moodle
Basado en el script original de Javier Fernández Panadero
Ampliado para soportar diferentes tipos de preguntas y corregido para manejar expresiones condicionales
"""

from google.colab import files  # Importación para Google Colab (simulada en la app web)
import random  # Para generar valores aleatorios
import re  # Para expresiones regulares
import math  # Para operaciones matemáticas
import json  # Para manipulación de datos JSON
import xml.sax.saxutils as saxutils  # Para escapar caracteres especiales en XML

# Definición de constantes para tipos de preguntas
TIPO_MULTIRESPUESTA = "multirespuesta"
TIPO_VERDADERO_FALSO = "verdadero_falso"

# Configuración por defecto del examen (será reemplazada por la configuración de la interfaz)
CONFIG_EXAMEN = {
    "questionTypes": {
        "multirespuesta": 5,  # Número de preguntas de opción múltiple
        "verdaderoFalso": 0,  # Número de preguntas de verdadero/falso
    },
    "config": {
        "multirespuesta": {
            "opciones": 4,  # Número de opciones por pregunta
            "penalizacion": True,  # Si las respuestas incorrectas penalizan
            "puntos": 1.0  # Puntuación de cada pregunta
        },
        "verdaderoFalso": {
            "penalizacion": True,  # Si las respuestas incorrectas penalizan
            "puntos": 1.0  # Puntuación de cada pregunta
        }
    }
}

# Cargar el archivo de entrada (simulado en la app web)
uploaded = files.upload()
file = uploaded.popitem()[0]

with open(file, 'r') as archivo:
    texto_completo = archivo.read()


def escape_xml(text):
    """
    Escapar caracteres especiales para XML
    
    Args:
        text: Texto a escapar
        
    Returns:
        Texto con caracteres especiales escapados
    """
    return saxutils.escape(str(text))


def evaluar_expresiones_condicionales(texto):
    """
    Evalúa expresiones entre @@ @@ que pueden contener operaciones matemáticas
    y expresiones condicionales
    
    Args:
        texto: Texto con expresiones a evaluar
        
    Returns:
        Texto con expresiones evaluadas
    """
    patron = r'@@ (.+?) @@'

    def reemplazo(match):
        expresion = match.group(1)

        try:
            # Detectar expresiones condicionales (condición and valor_verdadero or valor_falso)
            if ' and ' in expresion and ' or ' in expresion:
                partes = expresion.split(' and ')
                condicion = partes[0]
                resto = ' and '.join(partes[1:])

                partes_resto = resto.split(' or ')
                valor_verdadero = partes_resto[0].strip('"\'')
                valor_falso = ' or '.join(partes_resto[1:]).strip('"\'')

                resultado_condicion = eval(condicion)
                return valor_verdadero if resultado_condicion else valor_falso
            else:
                # Expresión normal a evaluar (operación matemática)
                resultado = eval(expresion)
                return str(resultado)
        except Exception as e:
            print(f"Error al evaluar expresión: {expresion}, {e}")
            return str(expresion)

    return re.sub(patron, reemplazo, texto)


def procesar_cabecera(texto_completo):
    """
    Procesa la cabecera del archivo que contiene definiciones de variables
    y prepara los conjuntos de datos para preguntas calculadas en Moodle
    
    Args:
        texto_completo: Contenido completo del archivo
        
    Returns:
        tuple: (texto procesado, datos para preguntas calculadas)
    """
    marca_def = '\n@@@@\n\n'  # Marca que separa la cabecera del contenido

    if marca_def in texto_completo:
        # Separar cabecera del resto del texto
        rompe_cabecera = texto_completo.split(marca_def)
        cabecera = rompe_cabecera[0]
        texto = rompe_cabecera[1]

        # Procesar las definiciones de variables
        lineas = cabecera.split('\n')
        variables = []
        data = []  # Almacenará los conjuntos de datos para Moodle

        for linea in lineas:
            elementos = linea.split(',')
            variables.append(elementos)

        # Generar 10 conjuntos de datos para cada variable
        longitud_serie = 10

        # Procesar cada variable según su tipo
        for variable in variables:
            if variable[0] == 'entero':
                valor = [variable[1]]  # Nombre de la variable
                numericos = list(map(int, variable[2:4]))  # Límites min y max
                valor += numericos
                minimo = valor[1]
                maximo = valor[2]
                # Generar valores aleatorios enteros
                for i in range(longitud_serie):
                    valor.append(random.randint(minimo, maximo))
                data.append(valor)

            elif variable[0] == 'real':
                valor = [variable[1]]  # Nombre de la variable
                numericos = list(map(float, variable[2:4]))  # Límites min y max
                valor += numericos
                minimo = valor[1]
                maximo = valor[2]
                # Generar valores aleatorios reales
                for i in range(longitud_serie):
                    x = random.uniform(minimo, maximo)
                    # Calcular precisión basada en la magnitud
                    decimales_para_significativas = 2 + \
                        math.ceil(-(math.log10(x)))
                    x = round(x, decimales_para_significativas)
                    valor.append(x)
                data.append(valor)

            elif variable[0] == 'lista':
                elegibles = variable[2:]  # Posibles valores para esta variable
                elegibles = list(map(float, elegibles))
                max_elegibles = max(elegibles)
                min_elegibles = min(elegibles)

                # Si no hay suficientes valores, repetir la lista
                if len(elegibles) < longitud_serie:
                    k = longitud_serie // len(elegibles)
                    elegibles += elegibles * k

                valor = [variable[1], min_elegibles, max_elegibles] + elegibles
                data.append(valor)

        # Evaluar expresiones matemáticas en el texto
        texto = evaluar_expresiones_condicionales(texto)

        # Preparar expresiones para formato Moodle
        ocurrencias = re.findall('@@ (.+?) @@', texto)

        # Convertir nombres de variables al formato de plantilla de Moodle
        for i in range(len(ocurrencias)):
            for variable in variables:
                ocurrencias[i] = ocurrencias[i].replace(
                    variable[1], '{' + variable[1] + '}')

        # Añadir prefijo de ecuación para Moodle
        for i in range(len(ocurrencias)):
            ocurrencias[i] = '{=' + ocurrencias[i] + '}'

        # Reemplazar en el texto original
        for i in range(len(ocurrencias)):
            texto = re.sub('@@ (.+?) @@', ocurrencias[i], texto, 1)

        return texto, data
    else:
        # Si no hay cabecera, sólo evaluar expresiones
        texto = evaluar_expresiones_condicionales(texto_completo)
        return texto, []


def clasificar_preguntas(texto_completo):
    """
    Clasifica las preguntas del texto en diferentes tipos
    utilizando técnicas robustas de detección
    
    Args:
        texto_completo: Contenido completo del archivo
        
    Returns:
        tuple: (diccionario de preguntas clasificadas, datos para preguntas calculadas)
    """
    texto, data = procesar_cabecera(texto_completo)

    # Normalizar saltos de línea para evitar problemas de plataforma
    texto = texto.replace('\r\n', '\n')
    
    # Método de detección de preguntas mejorado
    # Usamos el marcador $$$ como indicador principal de preguntas
    preguntas_raw = []
    lineas = texto.split('\n')
    pregunta_actual = []
    
    # Procesar línea por línea para reconstruir preguntas completas
    for i, linea in enumerate(lineas):
        pregunta_actual.append(linea)
        
        # Si encontramos una línea que empieza con $$$, es una respuesta correcta
        if linea.startswith('$$$'):
            # Buscamos el final de esta pregunta (próxima línea vacía o final del texto)
            j = i + 1
            while j < len(lineas) and lineas[j].strip():
                pregunta_actual.append(lineas[j])
                j += 1
            
            # Añadimos esta pregunta completa
            preguntas_raw.append('\n'.join(pregunta_actual))
            pregunta_actual = []
            
        # Si encontramos línea vacía y tenemos contenido acumulado, reiniciamos
        elif not linea.strip() and pregunta_actual:
            pregunta_actual = []
    
    # Si quedó alguna pregunta en proceso, la añadimos también
    if pregunta_actual:
        preguntas_raw.append('\n'.join(pregunta_actual))
    
    # Ahora clasificamos esas preguntas en categorías
    preguntas = {
        TIPO_MULTIRESPUESTA: [],
        TIPO_VERDADERO_FALSO: [],
    }

    # Procesar cada pregunta para clasificarla
    for pregunta_texto in preguntas_raw:
        if not pregunta_texto.strip() or pregunta_texto.strip().startswith('//'):
            continue  # Ignorar líneas vacías y comentarios

        # Manejar tanto enunciados multilínea (con +++p) como normales
        if '+++p\n' in pregunta_texto:
            partes = pregunta_texto.split('+++p\n')
            enunciado = partes[0]
            respuestas = partes[1].split('\n')
        else:
            lineas = pregunta_texto.split('\n')
            enunciado = lineas[0]
            respuestas = lineas[1:] if len(lineas) > 1 else []

        if not respuestas:
            continue  # Si no hay respuestas, ignorar

        # Ignorar líneas de comentarios que indican secciones
        if enunciado.strip().startswith('// PREGUNTAS DE OPCIÓN MÚLTIPLE'):
            continue
        elif enunciado.strip().startswith('// PREGUNTAS DE VERDADERO O FALSO'):
            continue

        # Clasificar según tipo de pregunta
        if any(resp.startswith('$$$') for resp in respuestas):
            if len(respuestas) == 2 and any(
                r.strip().lower() in ["verdadero", "true", "falso", "false"]
                for r in [r[3:] if r.startswith('$$$') else r for r in respuestas]
            ):
                # Es una pregunta de verdadero/falso
                preguntas[TIPO_VERDADERO_FALSO].append({
                    'enunciado': enunciado,
                    'respuestas': respuestas
                })
            else:
                # Es una pregunta de opción múltiple
                preguntas[TIPO_MULTIRESPUESTA].append({
                    'enunciado': enunciado,
                    'respuestas': respuestas
                })

    # Informar de la cantidad de preguntas encontradas
    print(f"Preguntas de opción múltiple: {len(preguntas[TIPO_MULTIRESPUESTA])}")
    print(f"Preguntas de verdadero/falso: {len(preguntas[TIPO_VERDADERO_FALSO])}")

    return preguntas, data


def seleccionar_preguntas(preguntas_clasificadas, config):
    """
    Selecciona aleatoriamente preguntas de cada tipo según la configuración
    
    Args:
        preguntas_clasificadas: Diccionario con preguntas por tipo
        config: Configuración del examen
        
    Returns:
        list: Preguntas seleccionadas para el examen
    """
    seleccionadas = []

    # Definir cuántas preguntas de cada tipo necesitamos
    tipos_cantidades = [
        (TIPO_MULTIRESPUESTA, config["questionTypes"]["multirespuesta"]),
        (TIPO_VERDADERO_FALSO, config["questionTypes"]["verdaderoFalso"]),
    ]

    # Procesar cada tipo de pregunta
    for tipo, cantidad in tipos_cantidades:
        if cantidad > 0:
            disponibles = preguntas_clasificadas[tipo].copy()
            random.shuffle(disponibles)  # Mezclar para selección aleatoria

            # Verificar si hay suficientes preguntas
            preguntas_disponibles = len(disponibles)
            if preguntas_disponibles < cantidad:
                print(
                    f"Advertencia: Se solicitaron {cantidad} preguntas de tipo {tipo}, pero solo hay {preguntas_disponibles} disponibles.")

            # Seleccionar hasta la cantidad solicitada
            preguntas_seleccionadas = disponibles[:min(
                cantidad, preguntas_disponibles)]
            for p in preguntas_seleccionadas:
                p['tipo'] = tipo  # Añadir tipo a cada pregunta
            seleccionadas.extend(preguntas_seleccionadas)

    # Mezclar todas las preguntas
    random.shuffle(seleccionadas)

    # Informar sobre las preguntas seleccionadas
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
    """
    Genera el XML para una pregunta de opción múltiple en formato Moodle
    
    Args:
        pregunta: Diccionario con datos de la pregunta
        idx: Índice de la pregunta
        data: Datos para preguntas calculadas
        config: Configuración del examen
        
    Returns:
        str: XML para la pregunta
    """
    # Determinar si la pregunta usa cálculos
    tiene_calculos = len(data) > 0

    # Elegir el tipo apropiado de pregunta para Moodle
    tipo_pregunta = "calculatedmulti" if tiene_calculos else "multichoice"

    # Generar encabezado XML de la pregunta
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

    # Procesar las respuestas
    respuestas = pregunta['respuestas'].copy()
    num_respuestas = len(respuestas)

    # Configurar penalización para respuestas incorrectas
    if config['config']['multirespuesta']['penalizacion']:
        valor_penalizacion = config['config']['multirespuesta']['valorPenalizacion']
        resta = round(-100 * valor_penalizacion, 5)
    else:
        resta = 0

    # Generar XML para cada respuesta
    for idx_resp, respuesta in enumerate(respuestas):
        if respuesta.startswith('$$$'):
            # Respuesta correcta (100% de puntuación)
            xml += f'''<answer fraction="100">
      <text>{escape_xml(respuesta[3:])}</text>
'''
        else:
            # Respuesta incorrecta (con penalización configurada)
            xml += f'''<answer fraction="{resta}">
      <text>{escape_xml(respuesta)}</text>
'''

        # Añadir atributos adicionales para preguntas calculadas
        if tiene_calculos:
            xml += '''    <tolerance>0.01</tolerance>
    <tolerancetype>1</tolerancetype>
    <correctanswerformat>2</correctanswerformat>
    <correctanswerlength>3</correctanswerlength>
'''

        # Cerrar la etiqueta de respuesta
        xml += '''    <feedback format="html">
<text></text>
    </feedback>
</answer>
'''

    # Configuración de unidades (aunque no se usen)
    xml += '''<unitgradingtype>0</unitgradingtype>
    <unitpenalty>0.1000000</unitpenalty>
    <showunits>3</showunits>
    <unitsleft>0</unitsleft>
'''

    # Añadir definiciones de datos para preguntas calculadas
    if tiene_calculos:
        xml += add_datasets_xml(data)

    # Cerrar la etiqueta de pregunta
    xml += '</question>\n'

    return xml


def generar_xml_verdadero_falso(pregunta, idx, data, config):
    """
    Genera el XML para una pregunta de verdadero/falso en formato Moodle
    
    Args:
        pregunta: Diccionario con datos de la pregunta
        idx: Índice de la pregunta
        data: Datos para preguntas calculadas
        config: Configuración del examen
        
    Returns:
        str: XML para la pregunta
    """
    # Generar encabezado XML de la pregunta
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

    # Procesar las respuestas
    respuestas = pregunta['respuestas'].copy()
    respuesta_correcta = None

    # Identificar la respuesta correcta (marcada con $$$)
    for resp in respuestas:
        if resp.startswith('$$$'):
            respuesta_correcta = resp[3:].strip().lower()
            break

    # Determinar si la respuesta correcta es Verdadero o Falso
    es_verdadero = respuesta_correcta in ["verdadero", "true"]

    # Generar XML para las opciones de respuesta
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


def add_datasets_xml(data):
    """
    Genera XML para definir los conjuntos de datos de variables en preguntas calculadas
    
    Args:
        data: Lista de definiciones de variables y sus valores
        
    Returns:
        str: XML para los conjuntos de datos
    """
    xml = '''<dataset_definitions>
'''

    # Generar XML para cada variable
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

        # Calcular el número de decimales para las variables
        if variable[1] != 0:
            decimales = max(0, 2 + math.ceil(-(math.log10(abs(variable[1])))))
        else:
            decimales = 2

        xml += f'''    <decimals><text>{decimales}</text>
</decimals>
'''

        # Definir los elementos del conjunto de datos
        long_serie = len(variable) - 3
        xml += f'''    <itemcount>{long_serie}</itemcount>
    <dataset_items>
'''

        # Añadir cada valor específico
        for i, valor in enumerate(variable[3:]):
            xml += f'''        <dataset_item>
           <number>{i+1}</number>
           <value>{valor}</value>
        </dataset_item>
'''

        # Cerrar las etiquetas de elementos
        xml += f'''    </dataset_items>
    <number_of_items>{long_serie}</number_of_items>
</dataset_definition>
'''

    # Cerrar la etiqueta principal
    xml += '</dataset_definitions>\n'
    return xml


def generar_examen_xml(preguntas_seleccionadas, data, config):
    """
    Genera el examen completo en formato XML para Moodle
    
    Args:
        preguntas_seleccionadas: Lista de preguntas a incluir
        data: Datos para preguntas calculadas
        config: Configuración del examen
        
    Returns:
        str: XML completo del examen
    """
    # Encabezado del documento XML
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<quiz>
'''

    # Generar XML para cada pregunta según su tipo
    for idx, pregunta in enumerate(preguntas_seleccionadas):
        tipo = pregunta.get('tipo', TIPO_MULTIRESPUESTA)

        if tipo == TIPO_MULTIRESPUESTA:
            xml += generar_xml_multirespuesta(pregunta, idx, data, config)
        elif tipo == TIPO_VERDADERO_FALSO:
            xml += generar_xml_verdadero_falso(pregunta, idx, data, config)

    # Cerrar la etiqueta principal
    xml += '</quiz>\n'

    return xml


def main():
    """
    Función principal que coordina el proceso de generación del examen
    """
    # Clasificar las preguntas del texto
    preguntas_clasificadas, data = clasificar_preguntas(texto_completo)

    # Seleccionar preguntas según la configuración
    preguntas_seleccionadas = seleccionar_preguntas(
        preguntas_clasificadas, CONFIG_EXAMEN)

    # Generar el examen en formato XML para Moodle
    examen_xml = generar_examen_xml(
        preguntas_seleccionadas, data, CONFIG_EXAMEN)

    # Guardar el resultado en un archivo
    with open("salida.xml", "w", encoding="utf-8") as archivo:
        archivo.write(examen_xml)

    # Ofrecer el archivo para descarga (simulado en la app web)
    files.download("salida.xml")

    return "Examen generado correctamente en formato XML para Moodle"


# Ejecutar la función principal y mostrar el resultado
result = main()
print(result)