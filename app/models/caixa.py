# app/models/caixa.py
from datetime import datetime

class Caixa:
    def __init__(self, codigo, NBI, NBF, prateleira, bloco, andar, corredor):
        self.codigo = codigo
        self.NBI = NBI
        self.NBF = NBF
        self.prateleira = prateleira
        self.bloco = bloco
        self.andar = andar
        self.corredor = corredor
        self.Arquivos = []  # lista de arquivos associada à caixa
        self.data_criacao = datetime.now()
        self.data_atualizacao = datetime.now()
    
    def to_dict(self):
        return {
            "codigo": self.codigo,
            "NBI": self.NBI,
            "NBF": self.NBF,
            "prateleira": self.prateleira,
            "bloco": self.bloco,
            "andar": self.andar,
            "corredor": self.corredor,
            "Arquivos": self.Arquivos,
            "data_criacao": self.data_criacao.isoformat(),
            "data_atualizacao": self.data_atualizacao.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        caixa = Caixa(
            data["codigo"],
            data["NBI"],
            data["NBF"],
            data["prateleira"],
            data["bloco"],
            data["andar"],
            data["corredor"]
        )
        if "Arquivos" in data:
            caixa.Arquivos = data["Arquivos"]  # recupera a lista de arquivos
        if "data_criacao" in data:
            caixa.data_criacao = datetime.fromisoformat(data["data_criacao"])
        if "data_atualizacao" in data:
            caixa.data_atualizacao = datetime.fromisoformat(data["data_atualizacao"])
        return caixa