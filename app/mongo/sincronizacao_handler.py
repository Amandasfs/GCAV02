# app/mongo/sincronizacao_handler.py
import logging

logger = logging.getLogger(__name__)

class SincronizacaoHandler:
    def __init__(self, connection):
        self.connected = connection.is_connected()
        if self.connected:
            self.caixas = connection.db.caixas
            self.arquivos = connection.db.arquivos
            self.segurados = connection.db.segurados

    def sincronizar_com_json(self, json_data):
        if not self.connected:
            return {"sucesso": False, "erro": "MongoDB offline"}

        stats = {"caixas_importadas": 0, "arquivos_importados": 0, "segurados_importados": 0, "erros": []}

        for caixa in json_data.get("caixas", []):
            try:
                caixa_copy = caixa.copy()
                caixa_copy.pop("_id", None)
                result = self.caixas.replace_one({"codigo": caixa["codigo"]}, caixa_copy, upsert=True)
                if result.upserted_id: stats["caixas_importadas"] += 1
            except Exception as e:
                stats["erros"].append(f"Caixa {caixa.get('codigo','N/A')}: {str(e)}")

        for segurado in json_data.get("segurados", []):
            try:
                s_copy = segurado.copy()
                s_copy.pop("_id", None)
                result = self.segurados.replace_one({"cpf": segurado["cpf"]}, s_copy, upsert=True)
                if result.upserted_id: stats["segurados_importados"] += 1
            except Exception as e:
                stats["erros"].append(f"Segurado {segurado.get('cpf','N/A')}: {str(e)}")

        for arquivo in json_data.get("arquivos", []):
            try:
                a_copy = arquivo.copy()
                a_copy.pop("_id", None)
                result = self.arquivos.replace_one({"NB": arquivo["NB"]}, a_copy, upsert=True)
                if result.upserted_id: stats["arquivos_importados"] += 1
            except Exception as e:
                stats["erros"].append(f"Arquivo {arquivo.get('NB','N/A')}: {str(e)}")

        stats["sucesso"] = True
        logger.info("🔄 Sincronização MongoDB/JSON concluída")
        return stats
