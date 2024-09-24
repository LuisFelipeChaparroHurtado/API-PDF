from flask import Flask, request, jsonify
import pdfplumber
import os
import re
from models.FacturaMovil import FacturaMovil
from models.Total import Total
from models.TotalFactura import TotalFactura
from models.Llamadas import Llamadas
from models.Mensajes import Mensajes

app = Flask(__name__)

@app.route('/extract_pdf', methods=['POST'])
def extract_pdf():
    try:
        data = request.get_json()
        pdf_path = data.get('pdf_path')

        if not pdf_path:
            return jsonify({'error': 'La ruta del archivo PDF es requerida'}), 400

        if not os.path.isfile(pdf_path):
            return jsonify({'error': 'El archivo PDF no se encuentra en la ruta especificada'}), 400

        extracted_data = extract_data_from_pdf(pdf_path)
        print(extracted_data)

        if extracted_data is None:
            return jsonify({'error': 'No se encontró el resumen de abonados'}), 200

        filtered_data = remove_headers(extracted_data)
        filtered_data_new = []
        resumen_abonados = filtered_data.get('resumen_abonados', '')

        if not resumen_abonados:
            return jsonify({'error': 'No se encontró el resumen de abonados'}), 400

        lines = resumen_abonados.split('\n')
        
        if len(lines) < 2:
            return jsonify({'error': 'El resumen de abonados no contiene suficientes líneas'}), 400

        for line in lines[:-2]:
            valores = [v.strip() for v in line.split('|')]
            
            if len(valores) >= 14:
                negativo = str(valores[7]) if len(valores) > 7 else ""
                datos = str(valores[8]) if len(valores) > 8 else "0"

                # Si ambos son "0", dejar un solo "0"
                if negativo == "0" and datos == "0":
                    negativo_datos = "0"
                else:
                    negativo_datos = (negativo + "" + datos).strip()  # Concatenación si no son ambos "0"
                
                factura = FacturaMovil(
                    celular=valores[0],
                    plan=valores[1],
                    cargo_fijo_mensual=str(valores[2]),
                    consumo_adicional_voz=str(valores[3]),
                    mensajes=str(valores[4]),
                    larga_distancia_internacional=str(valores[5]),
                    roaming=str(valores[6]),
                    negativo=negativo,  # Asigna negativo directamente
                    datos=negativo_datos,  # Asigna la concatenación de negativo y datos
                    servicios_movistar=str(valores[9]),
                    servicios_especiales=str(valores[10]),
                    descuentos=str(valores[11]),
                    iva_19=str(valores[12]),
                    impto_consumo_gravamenes=str(valores[13]),
                    subtotal=str(valores[13]) if len(valores) > 13 else ""
                )
                filtered_data_new.append(factura)
            
            elif len(valores) >= 13:
                factura = FacturaMovil(
                    celular=valores[0],
                    plan=valores[1],
                    cargo_fijo_mensual=str(valores[2]),
                    consumo_adicional_voz=str(valores[3]),
                    mensajes=str(valores[4]),
                    larga_distancia_internacional=str(valores[5]),
                    roaming=str(valores[6]),
                    negativo="",  # Asigna negativo directamente
                    datos="0" if str(valores[7]) == "0" else str(valores[7]),  # Asigna "0" si es "0"
                    servicios_movistar=str(valores[8]),
                    servicios_especiales=str(valores[9]),
                    descuentos=str(valores[10]),
                    iva_19=str(valores[11]),
                    impto_consumo_gravamenes=str(valores[12]),
                    subtotal=str(valores[12]) if len(valores) > 12 else ""
                )
                filtered_data_new.append(factura)


        
        if len(lines) >= 2:
            penultima_linea = lines[-2]
            valores_penultima = [v.strip() for v in penultima_linea.split('|')]
            if len(valores_penultima) >= 13:
                total = Total(
                    cargo_fijo_mensual=str(valores_penultima[1]),
                    consumo_adicional_voz=str(valores_penultima[2]),
                    mensajes=str(valores_penultima[3]),
                    larga_distancia_internacional=str(valores_penultima[4]),
                    roaming=str(valores_penultima[5]),
                    datos=str(valores_penultima[6]),
                    servicios_movistar=str(valores_penultima[7]),
                    servicios_especiales=str(valores_penultima[8]),
                    descuentos=str(valores_penultima[9]),
                    iva_19=str(valores_penultima[10]),
                    impto_consumo_gravamenes=str(valores_penultima[11]),
                    subtotal=str(valores_penultima[12])
                )
            else:
                return jsonify({'error': 'La penúltima línea no tiene suficientes valores'}), 400

        if len(lines) >= 1:
            ultima_linea = lines[-1]
            valores_ultima = [v.strip() for v in ultima_linea.split('|')]
            if len(valores_ultima) >= 3:
                totalFactura = TotalFactura(
                    total=str(valores_ultima[2])
                )
            else:
                return jsonify({'error': 'La última línea no tiene suficientes valores'}), 400

        # Procesar llamadas
        filtered_data_llamadas = []
        resumen_llamadas = filtered_data.get('resumen_llamadas', '')
        hay_llamadas = bool(resumen_llamadas)

        # Procesar mensajes
        filtered_data_mensajes = []
        resumen_mensajes = filtered_data.get('resumen_mensajes', '')
        hay_mensajes = bool(resumen_mensajes)

        # Procesar llamadas si hay
        if hay_llamadas:
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

        # Procesar mensajes si hay
        if hay_mensajes:
            lines_mensajes = resumen_mensajes.split('\n')
            for line in lines_mensajes:
                valores = [v.strip() for v in line.split('|')]
                if len(valores) < 6:
                    continue  # Omite líneas que no tienen suficientes valores
                
                # Dividir los valores en tres grupos de 5 elementos (fecha, hora, vlr_unidad, consumo, valor_total)
                primer_grupo = valores[0:6]  # Primer conjunto de columnas

                # Crear instancias de 'Mensajes' para cada grupo
                mensaje_1 = Mensajes(
                    fecha=primer_grupo[0],
                    hora=primer_grupo[1],
                    vlr_unidad=str(primer_grupo[2]),
                    consumo=str(primer_grupo[3]),
                    unidad_consumo=str(primer_grupo[4]),
                    valor_total=str(primer_grupo[5])
                )

                # Agregar los tres mensajes al arreglo de datos filtrados
                filtered_data_mensajes.append(mensaje_1)

                if len(valores) >= 12:
                    segundo_grupo = valores[6:12]  # Segundo conjunto de columnas

                    mensaje_2 = Mensajes(
                        fecha=segundo_grupo[0],
                        hora=segundo_grupo[1],
                        vlr_unidad=str(segundo_grupo[2]),
                        consumo=str(segundo_grupo[3]),
                        unidad_consumo=str(segundo_grupo[4]),
                        valor_total=str(segundo_grupo[5])
                    )

                    # Agregar los tres mensajes al arreglo de datos filtrados
                    filtered_data_mensajes.append(mensaje_2)

                if len(valores) >= 18:
                    tercer_grupo = valores[12:18]  # Tercer conjunto de columnas

                    mensaje_3 = Mensajes(
                        fecha=tercer_grupo[0],
                        hora=tercer_grupo[1],
                        vlr_unidad=str(tercer_grupo[2]),
                        consumo=str(tercer_grupo[3]),
                        unidad_consumo=str(tercer_grupo[4]),
                        valor_total=str(tercer_grupo[5])
                    )

                    # Agregar los tres mensajes al arreglo de datos filtrados
                    filtered_data_mensajes.append(mensaje_3)

        facturaGeneral = {
            "FacturaMovil": [factura.to_dict() for factura in filtered_data_new],
            "Total": total.to_dict() if 'total' in locals() else {},
            "TotalFactura": totalFactura.to_dict() if 'totalFactura' in locals() else {},
            "Llamadas": [llamada.to_dict() for llamada in filtered_data_llamadas],
            "Mensajes": [mensaje.to_dict() for mensaje in filtered_data_mensajes]
        }

        # Si no hay mensajes y llamadas, agrega el mensaje correspondiente
        if not hay_llamadas and not hay_mensajes:
            facturaGeneral["Mensajes"] = "No hay mensajes ni llamadas."

        return jsonify(facturaGeneral)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def extract_data_from_pdf(pdf_path):
    data = {}
    resumen_abonados_found = False
    resumen_abonados_text = ""
    resumen_llamadas_found = False
    resumen_mensajes_found = False
    resumen_llamadas_text = ""
    resumen_mensajes_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        # Itera sobre las páginas, asegurándote de acceder correctamente a cada página
        for page in pdf.pages:
            text = page.extract_text()
            
            if "RESUMEN DE ABONADOS" in text:
                resumen_abonados_found = True
                resumen_abonados_text += text[text.index("RESUMEN DE ABONADOS"):]
                if "Detalle de Ajustes" in text or "Detalle de consumos incluidos" in text or "Otras facturas en el mes" in text:
                    # Detener la búsqueda si encontramos el texto
                    break
            
            # Buscar el texto específico para llamadas
            if "Minutos/Segundos del Plan" in text:
                resumen_llamadas_found = True
                llamadas_text = text[text.index("Minutos/Segundos del Plan"):]
                
                # Si también se encuentra la sección de Internet 4G en la misma página
                if "INTERNET 4G LTE" in text:
                    # Extraer las llamadas hasta el encabezado de Internet 4G LTE
                    llamadas_text = llamadas_text[:text.index("INTERNET 4G LTE")]
                
                resumen_llamadas_text += llamadas_text
            
            # Manejo de internet (INTERNET 4G LTE)
            if "INTERNET 4G LTE" in text:
                resumen_mensajes_found = True
                resumen_mensajes_text += text[text.index("INTERNET 4G LTE"):]

    if not resumen_abonados_found:
        # Devuelve un mensaje de error si no se encuentra "RESUMEN DE ABONADOS"
        return None
    
    resumen_abonados_text = resumen_abonados_text.replace('$','').replace('  ', ' ').replace(' ', ' | ')
    resumen_llamadas_text = resumen_llamadas_text.replace('$', '').replace('  ', ' ').replace(' ', ' | ')
    resumen_mensajes_text = resumen_mensajes_text.replace('$', '').replace('  ', ' ').replace(' ', ' | ')

    if resumen_abonados_found:
        data['resumen_abonados'] = resumen_abonados_text.strip()
    else:
        data['resumen_abonados'] = "No encontrado"
    
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
    # Patrones específicos para abonados
    abonados_headers_to_remove = [
        r"RESUMEN\s*\|\s*DE\s*\|\s*ABONADOS.*?\n",  # Patrones generales de abonados
        r"RESUMEN\s*\|\s*DE\s*\|\s*ABONADOS\s*\|\s*Continuación.*?\n",  # Abonados - continuación
        r"Total\s*\|\s*Factura\s*0.*?\n",  # Total factura en abonados
    ]

    # Patrones específicos para llamadas
    llamadas_headers_to_remove = [
        r"Minutos/Segundos\s*\|\s*del\s*\|\s*Plan\s*\|\s*Total\s*\|.*?\n",  # Patrones de llamadas generales
        r"Continúan\s+\|Minutos/Segundos\s+\|\s+del\s+\|.*?\|\s+Total\s+\|.*?\n",  # Llamadas - continuación
        r"Fecha\s+\|\s+Hora\s+\|\s+Número\s+\|\s+Marcado\s+\|\s+Duración\s+\|\s+Vlr\.\s+\|\s+Unidad\s+\|\s+Total.*?\n",  # Encabezados de llamadas
        r"\|\s*Fecha\s+\|\s+Hora\s+\|\s+Número\s+\|\s+Marcado\s+\|\s+Duración\s+\|\s+Vlr\.\s+\|\s+Unidad\s+\|\s+Total.*?\n",  # Encabezados de llamadas repetidos
        r"^INTERNET\s+4G\s+LTE.*\n",
        r"Larga\s*\|\s*Impto\.\s*\|\s*al\s*Cargo\s*\|\s*Fijo\s*\|\s*Consumo\s*\|\s*Servicios\s*\|\s*Servicios\s*Celular\s*\|.*?\n",  # Patrones de resumen
        r"Fecha\s*\|\s*Hora\s*\|\s*Número\s*\|\s*Marcado\s*\|\s*DuraciónVlr\.\s*\|\s*Unidad\s*\|\s*Total"  # Eliminando la última línea con espacios
    ]

    # Patrones específicos para mensajes y datos
    mensajes_headers_to_remove = [
        r"INTERNET\s+4G\s+LTE\s+\|.*?\|\s+Total\s+\|.*?\n",  # Patrones de Internet
        r"Continúan\s+INTERNET\s+4G\s+LTE\s+\|.*?\|\s+Total\s+\|.*?\n",  # Internet - continuación
        r"Fecha\s+\|\s+Hora\s+\|\s+Vlr\.\s+\|\s+Unidad\s+\|\s+Consumo\s+\|\s+Valor\s+\|\s+Total.*?\n",  # Encabezados de datos y mensajes
        r"\|\s*Fecha\s+\|\s+Hora\s+\|\s+Vlr\.\s+\|\s+Unidad\s+\|\s+Consumo\s+\|\s+Valor\s+\|\s+Total.*?\n"  # Encabezados de datos y mensajes repetidos
    ]

    # Eliminar encabezados en 'resumen_abonados'
    if 'resumen_abonados' in data:
        for pattern in abonados_headers_to_remove:
            data['resumen_abonados'] = re.sub(pattern, '', data['resumen_abonados'], flags=re.DOTALL)

    # Eliminar encabezados en 'resumen_llamadas'
    if 'resumen_llamadas' in data:
        for pattern in llamadas_headers_to_remove:
            data['resumen_llamadas'] = re.sub(pattern, '', data['resumen_llamadas'], flags=re.DOTALL)

    # Eliminar encabezados en 'resumen_mensajes'
    if 'resumen_mensajes' in data:
        for pattern in mensajes_headers_to_remove:
            data['resumen_mensajes'] = re.sub(pattern, '', data['resumen_mensajes'], flags=re.DOTALL)

    return data


if __name__ == '__main__':
    app.run(debug=True)
