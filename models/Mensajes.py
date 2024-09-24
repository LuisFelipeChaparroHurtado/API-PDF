

# Clase FacturaMovil con el método to_dict
class Mensajes:
    def __init__(self, fecha, hora, vlr_unidad, consumo, unidad_consumo, valor_total):
        self.fecha = fecha
        self.hora = hora
        self.vlr_unidad = vlr_unidad
        self.consumo = consumo
        self.unidad_consumo = unidad_consumo
        self.valor_total = valor_total

    # Método para convertir el objeto en un diccionario
    def to_dict(self):
        return {
            'Fecha': self.fecha,
            'Hora': self.hora,
            'Valor unidad': self.vlr_unidad,
            'Consumo': self.consumo,
            'Unidad consumo': self.unidad_consumo,
            'Valor Total': self.valor_total
        }
    