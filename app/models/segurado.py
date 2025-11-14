# app/models/segurado.py
from datetime import datetime

class Segurado:
    def __init__(self, Nome, cpf):
        self.Nome = Nome
        self.cpf = cpf
        self.Arquivos = []
        self.data_criacao = datetime.now()
        self.data_atualizacao = datetime.now()
    
    def to_dict(self):
        return {
            "Nome": self.Nome,
            "cpf": self.cpf,
            "Arquivos": self.Arquivos,
            "data_criacao": self.data_criacao.isoformat(),
            "data_atualizacao": self.data_atualizacao.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        segurado = Segurado(data["Nome"], data["cpf"])
        segurado.Arquivos = data.get("Arquivos", [])
        if "data_criacao" in data:
            segurado.data_criacao = datetime.fromisoformat(data["data_criacao"])
        if "data_atualizacao" in data:
            segurado.data_atualizacao = datetime.fromisoformat(data["data_atualizacao"])
        return segurado