from datetime import datetime
from .base import JSONBaseHandler

class CaixaHandler(JSONBaseHandler):
    """CRUD de caixas"""

    def inserir(self, caixa_dict):
        try:
            dados = self.ler_dados()
            if self._verificar_duplicata(dados, "caixas", "codigo", caixa_dict["codigo"]):
                return {"erro": f"Já existe uma caixa com código {caixa_dict['codigo']}"}
            caixa_dict["id"] = self._gerar_id_unico()
            caixa_dict["data_criacao"] = caixa_dict["data_atualizacao"] = datetime.now().isoformat()
            dados["caixas"].append(caixa_dict)
            if self.salvar_dados(dados):
                return {"sucesso": True, "id": caixa_dict["id"], "codigo": caixa_dict["codigo"]}
            return {"erro": "Falha ao salvar dados"}
        except Exception as e:
            return {"erro": str(e)}

    def buscar(self, codigo):
        dados = self.ler_dados()
        return next((c for c in dados["caixas"] if c["codigo"] == codigo), None)

    def listar(self):
        return self.ler_dados()["caixas"]

    def atualizar(self, codigo, atualizacao):
        dados = self.ler_dados()
        for caixa in dados["caixas"]:
            if caixa["codigo"] == codigo:
                for k, v in atualizacao.items():
                    if k not in ["id", "data_criacao"]:
                        caixa[k] = v
                caixa["data_atualizacao"] = datetime.now().isoformat()
                if self.salvar_dados(dados):
                    return {"sucesso": True, "codigo": codigo}
                return {"erro": "Falha ao salvar dados"}
        return {"erro": f"Caixa {codigo} não encontrada"}

