class TotalFactura:
    def __init__(self, total):
        self.total = total

    # Método para convertir el objeto en un diccionario
    def to_dict(self):
        return {
            'Total': self.total
        }