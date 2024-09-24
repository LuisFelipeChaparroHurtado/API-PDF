

# Clase FacturaMovil con el método to_dict
class Llamadas:
    def __init__(self, fecha, hora, numero_marcado, operador, duracion, valr_unidad,
                 total):
        self.fecha = fecha
        self.hora = hora
        self.numero_marcado = numero_marcado
        self.operador = operador
        self.duracion = duracion
        self.valr_unidad = valr_unidad
        self.total = total

    # Método para convertir el objeto en un diccionario
    def to_dict(self):
        return {
            'Fecha': self.fecha,
            'Hora': self.hora,
            'Número marcado': self.numero_marcado,
            'Operador': self.operador,
            'Duración': self.duracion,
            'Valor unidad': self.valr_unidad,
            'Total': self.total
        }
    