# app/mongo/caixas_handler.py
import logging
from pymongo.errors import DuplicateKeyError
from base_handler import BaseHandler

logger = logging.getLogger(__name__)

class CaixasHandler(BaseHandler):
    def __init__(self, connection):
        self.connected = connection.is_connected()
        if self.connected:
            self.caixas = connection.db.caixas
            self.arquivos = connection.db.arquivos
            self._criar_indices()

    def _criar_indices(self):
        try:
            self.caixas.create_index("codigo", unique=True)
            self.caixas.create_index("prateleira")
            self.caixas.create_index("bloco")
            logger.info("✅ Índices de caixas criados/verificados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao criar índices de caixas: {e}")

    def inserir(self, caixa_dict):
        if not self.connected:
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            caixa_dict = self.add_timestamps(caixa_dict)
            result = self.caixas.insert_one(caixa_dict)
            return {"sucesso": True, "id": str(result.inserted_id)}
        except DuplicateKeyError:
            return {"sucesso": False, "erro": f"Caixa {caixa_dict['codigo']} já existe"}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    def listar(self, filtro=None):
        if not self.connected:
            return []
        try:
            if filtro:
                caixas = list(self.caixas.find(filtro))
            else:
                caixas = list(self.caixas.find())
            return self.sanitize_documents(caixas)
        except Exception as e:
            logger.error(f"Erro ao listar caixas: {e}")
            return []
    
    # Métodos buscar, atualizar, deletar seguem mesma estrutura modular...
