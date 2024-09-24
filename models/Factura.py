class Factura:
    def __init__(self, FacturaMovil, Total, TotalFactura):
        self.FacturaMovil = FacturaMovil
        self.Total = Total
        self.TotalFactura = TotalFactura

    # Método para convertir el objeto en un diccionario
    def to_dict(self):
        return {
            'Factura Movil': self.FacturaMovil,
            'Total': self.Total,
            'Total Factura': self.TotalFactura
        }