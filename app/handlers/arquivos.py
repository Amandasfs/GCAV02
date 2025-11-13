from datetime import datetime
from .base import JSONBaseHandler

class ArquivoHandler(JSONBaseHandler):
    """CRUD de arquivos"""

    def inserir(self, arquivo_dict):
        dados = self.ler_dados()
        if self._verificar_duplicata(dados, "arquivos", "NB", arquivo_dict["NB"]):
            return {"erro": f"Já existe um arquivo com NB {arquivo_dict['NB']}"}
        if not any(c["codigo"] == arquivo_dict["Caixa_codigo"] for c in dados["caixas"]):
            return {"erro": f"Caixa {arquivo_dict['Caixa_codigo']} não existe"}
        arquivo_dict["id"] = self._gerar_id_unico()
        arquivo_dict["data_criacao"] = arquivo_dict["data_atualizacao"] = datetime.now().isoformat()
        dados["arquivos"].append(arquivo_dict)
        return {"sucesso": True, "id": arquivo_dict["id"], "NB": arquivo_dict["NB"]} if self.salvar_dados(dados) else {"erro": "Falha ao salvar dados"}

    def buscar(self, NB):
        return next((a for a in self.ler_dados()["arquivos"] if a["NB"] == NB), None)

    def listar(self):
        return self.ler_dados()["arquivos"]

    def atualizar(self, NB, atualizacao):
        dados = self.ler_dados()
        for arquivo in dados["arquivos"]:
            if arquivo["NB"] == NB:
                for k, v in atualizacao.items():
                    if k not in ["id", "NB", "data_criacao"]:
                        arquivo[k] = v
                arquivo["data_atualizacao"] = datetime.now().isoformat()
                if self.salvar_dados(dados):
                    return {"sucesso": True, "NB": NB}
                return {"erro": "Falha ao salvar dados"}
        return {"erro": f"Arquivo {NB} não encontrado"}