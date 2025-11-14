# app/mongo/stats_handler.py
import logging

logger = logging.getLogger(__name__)

class StatsHandler:
    def __init__(self, connection):
        self.connected = connection.is_connected()
        if self.connected:
            self.caixas = connection.db.caixas
            self.arquivos = connection.db.arquivos
            self.segurados = connection.db.segurados

    def get_stats(self):
        if not self.connected:
            return {"total_caixas":0,"total_arquivos":0,"total_segurados":0,"status":"offline"}

        try:
            total_caixas = self.caixas.count_documents({})
            total_arquivos = self.arquivos.count_documents({})
            total_segurados = self.segurados.count_documents({})

            arquivos_por_caixa = list(self.arquivos.aggregate([{"$group":{"_id":"$Caixa_codigo","count":{"$sum":1}}}]))
            arquivos_por_segurado = list(self.arquivos.aggregate([{"$group":{"_id":"$SeguradoFK","count":{"$sum":1}}}]))

            return {
                "total_caixas": total_caixas,
                "total_arquivos": total_arquivos,
                "total_segurados": total_segurados,
                "status": "online",
                "estatisticas_avancadas": {
                    "caixas_com_arquivos": len(arquivos_por_caixa),
                    "segurados_com_arquivos": len(arquivos_por_segurado),
                    "caixa_mais_arquivos": max([a["count"] for a in arquivos_por_caixa]) if arquivos_por_caixa else 0,
                    "segurado_mais_arquivos": max([a["count"] for a in arquivos_por_segurado]) if arquivos_por_segurado else 0
                }
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"total_caixas":0,"total_arquivos":0,"total_segurados":0,"status":"error","erro":str(e)}
