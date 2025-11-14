# app/models/arquivo.py
from datetime import datetime

class Arquivo:
    def __init__(self, NB, APS, SeguradoFK, Tipo, Caixa_codigo):
        self.NB = NB
        self.APS = APS
        self.SeguradoFK = SeguradoFK
        self.Tipo = Tipo
        self.Caixa_codigo = Caixa_codigo
        self.data_criacao = datetime.now()
        self.data_atualizacao = datetime.now()
    
    def to_dict(self):
        return {
            "NB": self.NB,
            "APS": self.APS,
            "SeguradoFK": self.SeguradoFK,
            "Tipo": self.Tipo,
            "Caixa_codigo": self.Caixa_codigo,
            "data_criacao": self.data_criacao.isoformat(),
            "data_atualizacao": self.data_atualizacao.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        arquivo = Arquivo(
            data["NB"],
            data["APS"],
            data["SeguradoFK"],
            data["Tipo"],
            data["Caixa_codigo"]
        )
        if "data_criacao" in data:
            arquivo.data_criacao = datetime.fromisoformat(data["data_criacao"])
        if "data_atualizacao" in data:
            arquivo.data_atualizacao = datetime.fromisoformat(data["data_atualizacao"])
        return arquivo