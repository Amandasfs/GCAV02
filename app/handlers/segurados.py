from datetime import datetime
from .base import JSONBaseHandler

class SeguradoHandler(JSONBaseHandler):
    """CRUD de segurados"""

    def inserir(self, segurado_dict):
        dados = self.ler_dados()
        if self._verificar_duplicata(dados, "segurados", "cpf", segurado_dict["cpf"]):
            return {"erro": f"Já existe um segurado com CPF {segurado_dict['cpf']}"}
        segurado_dict["id"] = self._gerar_id_unico()
        segurado_dict["data_criacao"] = segurado_dict["data_atualizacao"] = datetime.now().isoformat()
        segurado_dict["Arquivos"] = segurado_dict.get("Arquivos", [])
        dados["segurados"].append(segurado_dict)
        return {"sucesso": True, "id": segurado_dict["id"], "cpf": segurado_dict["cpf"]} if self.salvar_dados(dados) else {"erro": "Falha ao salvar dados"}

    def buscar(self, cpf):
        return next((s for s in self.ler_dados()["segurados"] if s["cpf"] == cpf), None)

    def listar(self):
        return self.ler_dados()["segurados"]

    def atualizar(self, cpf, atualizacao):
        dados = self.ler_dados()
        for s in dados["segurados"]:
            if s["cpf"] == cpf:
                for k, v in atualizacao.items():
                    if k not in ["id", "cpf", "data_criacao"]:
                        s[k] = v
                s["data_atualizacao"] = datetime.now().isoformat()
                if self.salvar_dados(dados):
                    return {"sucesso": True, "cpf": cpf}
                return {"erro": "Falha ao salvar dados"}
        return {"erro": f"Segurado {cpf} não encontrado"}
