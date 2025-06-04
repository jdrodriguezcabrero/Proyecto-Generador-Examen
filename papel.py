# -*- coding: utf-8 -*-
"""
Generador de Exámenes Avanzado - Versión para Papel
Basado en el script original de Javier Fernández Panadero
Ampliado para soportar diferentes tipos de preguntas
"""

from google.colab import files
import random
import re
import math
import json

# Constantes para los tipos de preguntas
TIPO_MULTIRESPUESTA = "multirespuesta"
TIPO_VERDADERO_FALSO = "verdadero_falso"
TIPO_RESPUESTA_CORTA = "respuesta_corta"
TIPO_RELLENAR_ESPACIOS = "rellenar_espacios"

# Configuración global del examen (se reemplazará dinámicamente con la configuración de la interfaz)
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

# Función para evaluar expresiones condicionales en el texto


def evaluar_expresiones_condicionales(texto):
    # Patrón para encontrar expresiones Python condicionales
    patron = r'@@ (.+?) and "(.+?)" or "(.+?)" @@'

    def reemplazo(match):
        expresion = match.group(1)
        valor_verdadero = match.group(2)
        valor_falso = match.group(3)

        try:
            # Evaluar la expresión Python
            resultado = eval(expresion)
            # Devolver el valor adecuado según el resultado
            return valor_verdadero if resultado else valor_falso
        except Exception as e:
            print(f"Error al evaluar expresión: {expresion}, {e}")
            return f"[ERROR: {expresion}]"

    # Reemplazar todas las ocurrencias
    return re.sub(patron, reemplazo, texto)

# Función para procesar la cabecera con variables si existe


def procesar_cabecera(texto_completo):
    marca_def = '\n@@@@\n\n'

    if marca_def in texto_completo:
        rompe_cabecera = texto_completo.split(marca_def)
        cabecera = rompe_cabecera[0]
        texto = rompe_cabecera[1]

        lineas = cabecera.split('\n')
        variables = []
        for linea in lineas:
            elementos = linea.split(',')
            variables.append(elementos)

        # Procesar variables
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

        # Primero, evaluar expresiones condicionales
        texto = evaluar_expresiones_condicionales(texto)

        # Luego, reemplazar variables en el texto
        ocurrencias = re.findall('@@ (.+?) @@', texto)
        reemplazador = {}

        for ocurrencia in ocurrencias:
            reemplazador[ocurrencia] = eval(ocurrencia)

        # Ajustar por cifras significativas
        for key, value in reemplazador.items():
            if isinstance(value, (int, float)) and value != 0:
                # Ajuste para 3 cifras significativas
                m = math.ceil(math.log10(abs(value)))
                reemplazador[key] = round(value, 3 - m)

        # Reemplazar en el texto
        for clave, valor in reemplazador.items():
            texto = texto.replace('@@ ' + clave + ' @@', str(valor))

        return texto
    else:
        # Evaluar expresiones condicionales incluso si no hay cabecera
        return evaluar_expresiones_condicionales(texto_completo)

# Función para separar y clasificar las preguntas por tipo


def clasificar_preguntas(texto_completo):
    # Primero procesamos cualquier variable en el texto
    texto = procesar_cabecera(texto_completo)

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

        # Identificar el tipo de pregunta basado en características específicas
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

    return preguntas

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


def formatear_pregunta_multirespuesta(pregunta, numero, config):
    resultado = f"{numero}. {pregunta['enunciado']}\n"

    # Identificar la respuesta correcta
    respuestas = pregunta['respuestas'].copy()
    respuesta_correcta = None

    for i, resp in enumerate(respuestas):
        if resp.startswith('$$$'):
            respuesta_correcta = resp[3:]  # Quitar el marcador $$$
            respuestas[i] = respuesta_correcta
            break

    # Obtener el número deseado de opciones de la configuración
    num_opciones_deseadas = config["config"]["multirespuesta"]["opciones"]

    # Si necesitamos más opciones de las disponibles, generamos algunas aleatorias
    if num_opciones_deseadas > len(respuestas):
        # Generar opciones adicionales basadas en la respuesta correcta si es numérica
        try:
            # Intentar convertir la respuesta correcta a un número
            valor_correcto = float(respuesta_correcta)

            # Generar valores aleatorios cercanos al valor correcto
            for _ in range(num_opciones_deseadas - len(respuestas)):
                # Generar un valor aleatorio entre 0.5 y 1.5 veces el valor correcto
                factor = random.uniform(0.5, 1.5)
                if factor == 1.0:  # Evitar duplicar la respuesta correcta
                    factor = 1.5

                nuevo_valor = valor_correcto * factor

                # Redondear para mantener el mismo número de decimales
                if '.' in respuesta_correcta:
                    decimales = len(respuesta_correcta.split('.')[1])
                    nuevo_valor = round(nuevo_valor, decimales)
                else:
                    nuevo_valor = int(nuevo_valor)

                respuestas.append(str(nuevo_valor))
        except (ValueError, TypeError):
            # Si no es numérica, generar opciones con texto aleatorio
            for i in range(num_opciones_deseadas - len(respuestas)):
                respuestas.append(f"Opción adicional {i+1}")
    else:
        # Si hay más respuestas que opciones deseadas, reducir las incorrectas
        if num_opciones_deseadas < len(respuestas):
            incorrectas = [r for r in respuestas if r != respuesta_correcta]
            random.shuffle(incorrectas)
            # Dejar espacio para la correcta
            incorrectas = incorrectas[:num_opciones_deseadas - 1]
            respuestas = [respuesta_correcta] + incorrectas

    # Mezclar las respuestas
    random.shuffle(respuestas)

    # Añadir las respuestas al resultado con letras (a, b, c, etc.)
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

# Función para formatear una pregunta de verdadero/falso
def formatear_pregunta_verdadero_falso(pregunta, numero, config):
    resultado = f"{numero}. {pregunta['enunciado']}\n"

    # Identificar la respuesta correcta
    respuestas = pregunta['respuestas'].copy()
    respuesta_correcta = None

    for i, resp in enumerate(respuestas):
        if resp.startswith('$$$'):
            # Quitar el marcador $$$
            respuesta_correcta = resp[3:].strip().lower()
            respuestas[i] = resp[3:]
            break

    # Añadir las respuestas al resultado
    correcta = 'a' if respuesta_correcta in ["verdadero", "true"] else 'b'
    resultado += "a) Verdadero\n"
    resultado += "b) Falso\n"

    return {
        'texto': resultado,
        'correcta': correcta
    }

# Función para formatear una pregunta de respuesta corta


def formatear_pregunta_respuesta_corta(pregunta, numero, config):
    resultado = f"{numero}. {pregunta['enunciado']}\n"
    resultado += "Respuesta: ________________________________\n"

    # Identificar la respuesta correcta
    for resp in pregunta['respuestas']:
        if resp.startswith('$$$'):
            respuesta_correcta = resp[3:]  # Quitar el marcador $$$
            break

    return {
        'texto': resultado,
        'correcta': respuesta_correcta
    }

# Función para formatear una pregunta de rellenar espacios


def formatear_pregunta_rellenar_espacios(pregunta, numero, config):
    resultado = f"{numero}. {pregunta['enunciado']}\n"

    # Identificar la respuesta correcta
    for resp in pregunta['respuestas']:
        if resp.startswith('$$$'):
            respuesta_correcta = resp[3:]  # Quitar el marcador $$$
            break

    return {
        'texto': resultado,
        'correcta': respuesta_correcta
    }

# Función principal para generar el examen en formato texto


def generar_examen_texto(preguntas_seleccionadas, config):
    resultado = "EXAMEN\n\n"
    clave_correccion = []

    for i, pregunta in enumerate(preguntas_seleccionadas):
        # Formatear la pregunta según su tipo
        tipo = pregunta.get('tipo', TIPO_MULTIRESPUESTA)

        if tipo == TIPO_MULTIRESPUESTA:
            pregunta_formateada = formatear_pregunta_multirespuesta(
                pregunta, i+1, config)
        elif tipo == TIPO_VERDADERO_FALSO:
            pregunta_formateada = formatear_pregunta_verdadero_falso(
                pregunta, i+1, config)
        elif tipo == TIPO_RESPUESTA_CORTA:
            pregunta_formateada = formatear_pregunta_respuesta_corta(
                pregunta, i+1, config)
        elif tipo == TIPO_RELLENAR_ESPACIOS:
            pregunta_formateada = formatear_pregunta_rellenar_espacios(
                pregunta, i+1, config)
        else:
            # Por defecto, tratar como multirespuesta
            pregunta_formateada = formatear_pregunta_multirespuesta(
                pregunta, i+1, config)

        resultado += pregunta_formateada['texto'] + "\n"
        clave_correccion.append(f"{i+1}: {pregunta_formateada['correcta']}")

    # Añadir la clave de corrección al final
    resultado += "\n\n\nCLAVE DE CORRECCIÓN\n"
    resultado += "\n".join(clave_correccion)

    return resultado

# Función principal


def main():
    # Procesar el archivo de entrada
    preguntas_clasificadas = clasificar_preguntas(texto_completo)

    # Seleccionar preguntas según la configuración
    preguntas_seleccionadas = seleccionar_preguntas(
        preguntas_clasificadas, CONFIG_EXAMEN)

    # Generar el examen en formato texto
    examen_texto = generar_examen_texto(preguntas_seleccionadas, CONFIG_EXAMEN)

    # Guardar el examen en un archivo
    with open("output.txt", "w") as archivo:
        archivo.write(examen_texto)

    # Descargar el archivo
    files.download("output.txt")

    return "Examen generado correctamente"


# Ejecutar el programa
main()
