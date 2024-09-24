
class Total:
    def __init__(self, cargo_fijo_mensual, consumo_adicional_voz, mensajes,
                 larga_distancia_internacional, roaming, datos, servicios_movistar, 
                 servicios_especiales, descuentos, iva_19, impto_consumo_gravamenes, subtotal):
        
        self.cargo_fijo_mensual = cargo_fijo_mensual
        self.consumo_adicional_voz = consumo_adicional_voz
        self.mensajes = mensajes
        self.larga_distancia_internacional = larga_distancia_internacional
        self.roaming = roaming
        self.datos = datos
        self.servicios_movistar = servicios_movistar
        self.servicios_especiales = servicios_especiales
        self.descuentos = descuentos
        self.iva_19 = iva_19
        self.impto_consumo_gravamenes = impto_consumo_gravamenes
        self.subtotal = subtotal

    # Método para convertir el objeto en un diccionario
    def to_dict(self):
        return {
            'Cargo Fijo Mensual': self.cargo_fijo_mensual,
            'Consumo Adicional Voz': self.consumo_adicional_voz,
            'Mensajes': self.mensajes,
            'Larga Distancia Internacional': self.larga_distancia_internacional,
            'Roaming': self.roaming,
            'Datos': self.datos,
            'Servicios movistar': self.servicios_movistar,
            'Servicios Especiales': self.servicios_especiales,
            'Descuentos': self.descuentos,
            'IVA 19%': self.iva_19,
            'Impto. al Consumo y otros Gravámenes': self.impto_consumo_gravamenes,
            'SUBTOTAL': self.subtotal
        }
