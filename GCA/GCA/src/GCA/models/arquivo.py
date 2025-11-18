class Arquivo:
    def __init__(self, NB, APS, SeguradoFK, Tipo, Caixa_codigo):
        self.NB = NB
        self.APS = APS
        self.SeguradoFK = SeguradoFK
        self.Tipo = Tipo
        self.Caixa_codigo = Caixa_codigo
        self.criado_em = None
    
    def to_dict(self):
        return {
            'NB': self.NB,
            'APS': self.APS,
            'SeguradoFK': self.SeguradoFK,
            'Tipo': self.Tipo,
            'Caixa_codigo': self.Caixa_codigo,
            'criado_em': self.criado_em
        }