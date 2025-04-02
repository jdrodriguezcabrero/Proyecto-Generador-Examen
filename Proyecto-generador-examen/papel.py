# -*- coding: utf-8 -*-
"""
Generador de Exámenes Avanzado - Versión para Papel
Basado en el script original de Javier Fernández Panadero
Ampliado para soportar diferentes tipos de preguntas
"""

from google.colab import files  # Importación para Google Colab (simulada en la app web)
import random
import re
import math
import json

# Definición de constantes para tipos de preguntas
TIPO_MULTIRESPUESTA = "multirespuesta"
TIPO_VERDADERO_FALSO = "verdadero_falso"

# Configuración por defecto del examen (será reemplazada por la configuración de la interfaz)
CONFIG_EXAMEN = {
    "questionTypes": {
        "multirespuesta": 5,
        "verdaderoFalso": 0,
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
        }
    }
}

# Cargar el archivo de entrada (simulado en la app web)
uploaded = files.upload()
file = uploaded.popitem()[0]

with open(file, 'r') as archivo:
    texto_completo = archivo.read()


def evaluar_expresiones_condicionales(texto):
    """
    Evalúa expresiones condicionales en el formato @@ condición and "valor_verdadero" or "valor_falso" @@
    """
    patron = r'@@ (.+?) and "(.+?)" or "(.+?)" @@'

    def reemplazo(match):
        expresion = match.group(1)
        valor_verdadero = match.group(2)
        valor_falso = match.group(3)

        try:
            resultado = eval(expresion)
            return valor_verdadero if resultado else valor_falso
        except Exception as e:
            print(f"Error al evaluar expresión: {expresion}, {e}")
            return f"[ERROR: {expresion}]"

    return re.sub(patron, reemplazo, texto)


def procesar_cabecera(texto_completo):
    """
    Procesa la cabecera del archivo que contiene definiciones de variables
    y evalúa las expresiones matemáticas en el contenido
    """
    marca_def = '\n@@@@\n\n'

    if marca_def in texto_completo:
        # Separar la cabecera del resto del texto
        rompe_cabecera = texto_completo.split(marca_def)
        cabecera = rompe_cabecera[0]
        texto = rompe_cabecera[1]

        # Procesar definiciones de variables
        lineas = cabecera.split('\n')
        variables = []
        for linea in lineas:
            elementos = linea.split(',')
            variables.append(elementos)

        # Evaluar variables según su tipo
        for variable in variables:
            if variable[0] == 'entero':
                min_val = int(variable[2])
                max_val = int(variable[3])
                valor = random.randint(min_val, max_val)
                exec("%s = %d" % (variable[1], valor))
            elif variable[0] == 'real':
                min_val = float(variable[2])
                max_val = float(variable[3])
                valor = random.uniform(min_val, max_val)
                exec("%s = %f" % (variable[1], valor))
            elif variable[0] == 'lista':
                elegibles = variable[2:]
                elegibles = [int(val) if val.isdigit() else float(val)
                             for val in elegibles]
                valor = random.choice(elegibles)
                if isinstance(valor, int):
                    exec("%s = %d" % (variable[1], valor))
                else:
                    exec("%s = %f" % (variable[1], valor))

        # Evaluar expresiones condicionales
        texto = evaluar_expresiones_condicionales(texto)

        # Identificar expresiones a evaluar
        ocurrencias = re.findall('@@ (.+?) @@', texto)
        reemplazador = {}

        # Evaluar las expresiones y guardarlas
        for ocurrencia in ocurrencias:
            reemplazador[ocurrencia] = eval(ocurrencia)

        # Redondear valores numéricos para mejor presentación
        for key, value in reemplazador.items():
            if isinstance(value, (int, float)) and value != 0:
                # Determinar el número de decimales para redondeo basándose en la magnitud
                m = math.ceil(math.log10(abs(value)))
                reemplazador[key] = round(value, 3 - m)

        # Reemplazar las expresiones en el texto
        for clave, valor in reemplazador.items():
            texto = texto.replace('@@ ' + clave + ' @@', str(valor))

        return texto
    else:
        return evaluar_expresiones_condicionales(texto_completo)


def clasificar_preguntas(texto_completo):
    """
    Clasifica las preguntas del texto en diferentes tipos
    """
    texto = procesar_cabecera(texto_completo)

    # Dividir el texto en preguntas individuales utilizando dobles saltos de línea
    # NOTA: Este es el origen del problema de detección de preguntas
    texto_preguntas = texto.split(sep='\n\n')

    # Diccionario para almacenar las preguntas clasificadas
    preguntas = {
        TIPO_MULTIRESPUESTA: [],
        TIPO_VERDADERO_FALSO: [],
    }

    # Procesar cada pregunta
    for pregunta in texto_preguntas:
        if not pregunta.strip() or pregunta.strip().startswith('//'):
            continue  # Ignorar líneas vacías y comentarios

        # Manejar tanto enunciados multilínea (con +++p) como normales
        if '+++p\n' in pregunta:
            partes = pregunta.split('+++p\n')
            enunciado = partes[0]
            respuestas = partes[1].split('\n')
        else:
            lineas = pregunta.split('\n')
            enunciado = lineas[0]
            respuestas = lineas[1:] if len(lineas) > 1 else []

        if not respuestas:
            continue  # Si no hay respuestas, ignorar

        # Clasificar la pregunta según las respuestas
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

    # Informar de la cantidad de preguntas encontradas de cada tipo
    print(
        f"Preguntas de opción múltiple: {len(preguntas[TIPO_MULTIRESPUESTA])}")
    print(
        f"Preguntas de verdadero/falso: {len(preguntas[TIPO_VERDADERO_FALSO])}")

    return preguntas


def seleccionar_preguntas(preguntas_clasificadas, config):
    """
    Selecciona aleatoriamente preguntas de cada tipo según la configuración
    """
    seleccionadas = []

    # Procesar cada tipo de pregunta
    tipos_cantidades = [
        (TIPO_MULTIRESPUESTA, config["questionTypes"]["multirespuesta"]),
        (TIPO_VERDADERO_FALSO, config["questionTypes"]["verdaderoFalso"]),
    ]

    for tipo, cantidad in tipos_cantidades:
        if cantidad > 0:
            disponibles = preguntas_clasificadas[tipo].copy()
            random.shuffle(disponibles)  # Aleatorizar el orden

            # Verificar si hay suficientes preguntas del tipo requerido
            preguntas_disponibles = len(disponibles)
            if preguntas_disponibles < cantidad:
                print(
                    f"Advertencia: Se solicitaron {cantidad} preguntas de tipo {tipo}, pero solo hay {preguntas_disponibles} disponibles.")

            # Seleccionar hasta la cantidad solicitada
            preguntas_seleccionadas = disponibles[:min(
                cantidad, preguntas_disponibles)]
            for p in preguntas_seleccionadas:
                p['tipo'] = tipo
            seleccionadas.extend(preguntas_seleccionadas)
    random.shuffle(seleccionadas)  # Mezclar las preguntas de distintos tipos

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


def formatear_pregunta_multirespuesta(pregunta, numero, config):
    """
    Formatea una pregunta de opción múltiple para el examen en papel
    """
    resultado = f"{numero}. {pregunta['enunciado']}\n"

    respuestas = pregunta['respuestas'].copy()
    respuesta_correcta = None

    # Identificar la respuesta correcta (marcada con $$$)
    for i, resp in enumerate(respuestas):
        if resp.startswith('$$$'):
            respuesta_correcta = resp[3:]
            respuestas[i] = respuesta_correcta
            break

    num_opciones_deseadas = config["config"]["multirespuesta"]["opciones"]

    # Ajustar el número de opciones si es necesario
    if num_opciones_deseadas > len(respuestas):
        # Intentar generar más opciones basadas en la respuesta correcta
        try:
            valor_correcto = float(respuesta_correcta)

            for _ in range(num_opciones_deseadas - len(respuestas)):
                factor = random.uniform(0.5, 1.5)
                if factor == 1.0:
                    factor = 1.5

                nuevo_valor = valor_correcto * factor

                # Formatear con decimales apropiados
                if '.' in respuesta_correcta:
                    decimales = len(respuesta_correcta.split('.')[1])
                    nuevo_valor = round(nuevo_valor, decimales)
                else:
                    nuevo_valor = int(nuevo_valor)

                respuestas.append(str(nuevo_valor))
        except (ValueError, TypeError):
            # Si no se puede convertir a número, añadir opciones genéricas
            for i in range(num_opciones_deseadas - len(respuestas)):
                respuestas.append(f"Opción adicional {i+1}")
    else:
        # Si hay demasiadas opciones, reducir manteniendo la correcta
        if num_opciones_deseadas < len(respuestas):
            incorrectas = [r for r in respuestas if r != respuesta_correcta]
            random.shuffle(incorrectas)
            incorrectas = incorrectas[:num_opciones_deseadas - 1]
            respuestas = [respuesta_correcta] + incorrectas

    # Mezclar las respuestas
    random.shuffle(respuestas)

    # Formatear las opciones con letras (a, b, c, etc.)
    abecedario = 'abcdefghijklmnopqrstuvwxyz'
    index_correcta = None

    for i, resp in enumerate(respuestas[:num_opciones_deseadas]):
        resultado += f"{abecedario[i]}) {resp}\n"
        if resp == respuesta_correcta:
            index_correcta = i

    return {
        'texto': resultado,
        'correcta': abecedario[index_correcta]
    }


def formatear_pregunta_verdadero_falso(pregunta, numero, config):
    """
    Formatea una pregunta de verdadero/falso para el examen en papel
    """
    resultado = f"{numero}. {pregunta['enunciado']}\n"

    respuestas = pregunta['respuestas'].copy()
    respuesta_correcta = None

    # Identificar la respuesta correcta (marcada con $$$)
    for i, resp in enumerate(respuestas):
        if resp.startswith('$$$'):
            respuesta_correcta = resp[3:].strip().lower()
            respuestas[i] = resp[3:]
            break

    # Determinar si la respuesta correcta es Verdadero o Falso
    correcta = 'a' if respuesta_correcta in ["verdadero", "true"] else 'b'
    resultado += "a) Verdadero\n"
    resultado += "b) Falso\n"

    return {
        'texto': resultado,
        'correcta': correcta
    }


def generar_examen_texto(preguntas_seleccionadas, config):
    """
    Genera el examen en formato texto con las preguntas seleccionadas
    """
    resultado = "EXAMEN\n\n"
    clave_correccion = []

    # Procesar cada pregunta
    for i, pregunta in enumerate(preguntas_seleccionadas):
        tipo = pregunta.get('tipo', TIPO_MULTIRESPUESTA)

        # Formatear según el tipo de pregunta
        if tipo == TIPO_MULTIRESPUESTA:
            pregunta_formateada = formatear_pregunta_multirespuesta(
                pregunta, i+1, config)
        elif tipo == TIPO_VERDADERO_FALSO:
            pregunta_formateada = formatear_pregunta_verdadero_falso(
                pregunta, i+1, config)
        else:
            # Por defecto, tratar como multirespuesta
            pregunta_formateada = formatear_pregunta_multirespuesta(
                pregunta, i+1, config)

        # Añadir la pregunta formateada al resultado
        resultado += pregunta_formateada['texto'] + "\n"
        clave_correccion.append(f"{i+1}: {pregunta_formateada['correcta']}")

    # Añadir la clave de corrección al final
    resultado += "\n\n\nCLAVE DE CORRECCIÓN\n"
    resultado += "\n".join(clave_correccion)

    return resultado


def main():
    """
    Función principal que coordina el proceso de generación del examen
    """
    # Clasificar las preguntas del texto
    preguntas_clasificadas = clasificar_preguntas(texto_completo)

    # Seleccionar preguntas según la configuración
    preguntas_seleccionadas = seleccionar_preguntas(
        preguntas_clasificadas, CONFIG_EXAMEN)

    # Generar el examen en formato texto
    examen_texto = generar_examen_texto(preguntas_seleccionadas, CONFIG_EXAMEN)

    # Guardar el resultado en un archivo
    with open("output.txt", "w") as archivo:
        archivo.write(examen_texto)

    # Ofrecer el archivo para descarga (simulado en la app web)
    files.download("output.txt")

    return "Examen generado correctamente"

# Ejecutar la función principal
main()