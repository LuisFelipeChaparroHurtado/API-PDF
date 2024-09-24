from flask import Flask, request, jsonify
import pdfplumber
import os
import re
from models.Llamadas import Llamadas
from models.Mensajes import Mensajes


appLlamadas = Flask(__name__)

@appLlamadas.route('/extract_pdf', methods=['POST'])
def extract_pdf():
    try:
        data = request.get_json()
        pdf_path = data.get('pdf_path')

        if not pdf_path:
            return jsonify({'error': 'La ruta del archivo PDF es requerida'}), 400

        if not os.path.isfile(pdf_path):
            return jsonify({'error': 'El archivo PDF no se encuentra en la ruta especificada'}), 400

        extracted_data = extract_data_from_pdf(pdf_path)
        filtered_data = remove_headers(extracted_data)
        # Imprimir solo las primeras 100 líneas del resumen de llamadas y mensajes
        #print('\n'.join(filtered_data['resumen_llamadas'].split('\n')[:100]))
        #print('\n'.join(filtered_data['resumen_mensajes'].split('\n')[:100]))

        # Procesar llamadas
        filtered_data_llamadas = []
        resumen_llamadas = filtered_data.get('resumen_llamadas', '')

        if not resumen_llamadas:
            return jsonify({'error': 'No se encontró el resumen llamadas'}), 400

        lines_llamadas = resumen_llamadas.split('\n')

        for line in lines_llamadas:
            valores = [v.strip() for v in line.split('|')]
            
            if len(valores) < 7:  # Asegura que al menos haya una columna completa
                continue  # Omite líneas que no tienen suficientes valores

            # Procesar la primera columna (primer conjunto de datos)
            primer_grupo = valores[0:7]
            
            llamada_1 = Llamadas(
                fecha=primer_grupo[0],
                hora=primer_grupo[1],
                numero_marcado=str(primer_grupo[2]),
                operador=str(primer_grupo[3]),
                duracion=str(primer_grupo[4]),
                valr_unidad=str(primer_grupo[5]),
                total=str(primer_grupo[6])
            )
            
            # Agregar la primera llamada al arreglo de datos filtrados
            filtered_data_llamadas.append(llamada_1)

            # Si hay una segunda columna (segundo conjunto de datos)
            if len(valores) >= 14:
                segundo_grupo = valores[7:14]
                
                llamada_2 = Llamadas(
                    fecha=segundo_grupo[0],
                    hora=segundo_grupo[1],
                    numero_marcado=str(segundo_grupo[2]),
                    operador=str(segundo_grupo[3]),
                    duracion=str(segundo_grupo[4]),
                    valr_unidad=str(segundo_grupo[5]),
                    total=str(segundo_grupo[6])
                )
                
                # Agregar la segunda llamada al arreglo de datos filtrados
                filtered_data_llamadas.append(llamada_2)


        # Procesar mensajes
        filtered_data_mensajes = []
        resumen_mensajes = filtered_data.get('resumen_mensajes', '')

        if not resumen_mensajes:
            return jsonify({'error': 'No se encontró el resumen de mensajes'}), 400

        lines_mensajes = resumen_mensajes.split('\n')

        for line in lines_mensajes:
            valores = [v.strip() for v in line.split('|')]
            
            if len(valores) < 18:
                continue  # Omite líneas que no tienen suficientes valores
            
            # Dividir los valores en tres grupos de 5 elementos (fecha, hora, vlr_unidad, consumo, valor_total)
            primer_grupo = valores[0:6]  # Primer conjunto de columnas
            segundo_grupo = valores[6:12]  # Segundo conjunto de columnas
            tercer_grupo = valores[12:18]  # Tercer conjunto de columnas

            # Crear instancias de 'Mensajes' para cada grupo
            mensaje_1 = Mensajes(
                fecha=primer_grupo[0],
                hora=primer_grupo[1],
                vlr_unidad=str(primer_grupo[2]),
                consumo=str(primer_grupo[3]),
                unidad_consumo=str(primer_grupo[4]),
                valor_total=str(primer_grupo[5])
            )
            
            mensaje_2 = Mensajes(
                fecha=segundo_grupo[0],
                hora=segundo_grupo[1],
                vlr_unidad=str(segundo_grupo[2]),
                consumo=str(segundo_grupo[3]),
                unidad_consumo=str(segundo_grupo[4]),
                valor_total=str(segundo_grupo[5])
            )
            
            mensaje_3 = Mensajes(
                fecha=tercer_grupo[0],
                hora=tercer_grupo[1],
                vlr_unidad=str(tercer_grupo[2]),
                consumo=str(tercer_grupo[3]),
                unidad_consumo=str(tercer_grupo[4]),
                valor_total=str(tercer_grupo[5])
            )

            # Agregar los tres mensajes al arreglo de datos filtrados
            filtered_data_mensajes.append(mensaje_1)
            filtered_data_mensajes.append(mensaje_2)
            filtered_data_mensajes.append(mensaje_3)

        # Respuesta con llamadas y mensajes
        facturaGeneral = {
            "Llamadas": [llamada.to_dict() for llamada in filtered_data_llamadas],
            "Mensajes": [mensaje.to_dict() for mensaje in filtered_data_mensajes]
        }

        return jsonify(facturaGeneral)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_data_from_pdf(pdf_path):
    data = {}
    resumen_llamadas_found = False
    resumen_mensajes_found = False
    resumen_llamadas_text = ""
    resumen_mensajes_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            # Buscar el texto específico para llamadas
            if "Minutos/Segundos del Plan" in text:
                resumen_llamadas_found = True
                resumen_llamadas_text += text[text.index("Minutos/Segundos del Plan"):]

            # Buscar el texto específico para mensajes
            if "INTERNET 4G LTE" in text:
                resumen_mensajes_found = True
                resumen_mensajes_text += text[text.index("INTERNET 4G LTE"):]

    resumen_llamadas_text = resumen_llamadas_text.replace('$', '').replace('  ', ' ').replace(' ', ' | ')
    resumen_mensajes_text = resumen_mensajes_text.replace('$', '').replace('  ', ' ').replace(' ', ' | ')

    if resumen_llamadas_found:
        data['resumen_llamadas'] = resumen_llamadas_text.strip()
    else:
        data['resumen_llamadas'] = "No encontrado"

    if resumen_mensajes_found:
        data['resumen_mensajes'] = resumen_mensajes_text.strip()
    else:
        data['resumen_mensajes'] = "No encontrado"

    return data


def remove_headers(data):
    # Definir patrones generales para los encabezados de llamadas y mensajes
    patterns_to_remove = [
        r"^(?:\s*\|.*?)+$",  # Encabezados con muchas barras "|"
        r"Minutos/Segundos\s+\|\s+del\s+\|\s+Plan\s+\|.*?\|\s+Total\s+\|.*?\n",  # Patrones de llamadas
        r"Continúan\s+\|Minutos/Segundos\s+\|\s+del\s+\|\s+Plan\s+\|.*?\|\s+Total\s+\|.*?\n",  # Patrones de llamadas
        r"INTERNET\s+\|\s+4G\s+\|\s+LTE\s+\|.*?\|\s+Total\s+\|.*?\n",  # Patrones de internet
        r"Continúan\s+\|INTERNET\s+\|\s+4G\s+\|\s+LTE\s+\|.*?\|\s+Total\s+\|.*?\n",  # Patrones de internet
        r"Fecha\s+\|\s+Hora\s+\|\s+Número\s+\|\s+Marcado\s+\|\s+DuraciónVlr\.\s+\|\s+Unidad\s+\|\s+Total.*?\n",  # Fechas y valores de llamadas
        r"Fecha\s+\|\s+Hora\s+\|\s+Vlr\.\s+\|\s+Unidad\s+\|\s+Consumo\s+\|\s+Valor\s+\|\s+Total.*?\n"  # Fechas y valores de mensajes/datos
    ]

    # Eliminar encabezados en 'resumen_llamadas'
    if 'resumen_llamadas' in data:
        for pattern in patterns_to_remove:
            data['resumen_llamadas'] = re.sub(pattern, '', data['resumen_llamadas'], flags=re.DOTALL)

    # Eliminar encabezados en 'resumen_mensajes'
    if 'resumen_mensajes' in data:
        for pattern in patterns_to_remove:
            data['resumen_mensajes'] = re.sub(pattern, '', data['resumen_mensajes'], flags=re.DOTALL)

    return data

if __name__ == '__main__':
    appLlamadas.run(debug=True)
