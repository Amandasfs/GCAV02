# app/mongo/caixas_handler.py
import logging
from pymongo.errors import DuplicateKeyError
from base_handler import BaseHandler

logger = logging.getLogger(__name__)

class SeguradosHandler(BaseHandler):
    def __init__(self, connection):
        self.connected = connection.is_connected()
        if self.connected:
            self.segurados = connection.db.segurados
            self.arquivos = connection.db.arquivos
            self._criar_indices()

    def _criar_indices(self):
        try:
            self.segurados.create_index("cpf", unique=True)
            logger.info("✅ Índices de segurados criados/verificados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao criar índices de segurados: {e}")

    def inserir(self, segurado_dict):
        if not self.connected:
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            segurado_dict = self.add_timestamps(segurado_dict)
            segurado_dict["Arquivos"] = []
            result = self.segurados.insert_one(segurado_dict)
            return {"sucesso": True, "id": str(result.inserted_id)}
        except DuplicateKeyError:
            return {"sucesso": False, "erro": f"Segurado {segurado_dict['cpf']} já existe"}
        except Exception as e:
            logger.error(f"Erro ao inserir segurado: {e}")
            return {"sucesso": False, "erro": str(e)}

    def listar(self, filtro=None):
        if not self.connected:
            return []
        try:
            segurados = list(self.segurados.find(filtro) if filtro else self.segurados.find())
            segurados_sanitized = self.sanitize_documents(segurados)
            for s in segurados_sanitized:
                s["total_arquivos"] = self.arquivos.count_documents({"SeguradoFK": s["cpf"]})
            return segurados_sanitized
        except Exception as e:
            logger.error(f"Erro ao listar segurados: {e}")
            return []

    def buscar(self, cpf):
        if not self.connected:
            return None
        try:
            segurado = self.segurados.find_one({"cpf": cpf})
            if segurado:
                arquivos = list(self.arquivos.find({"SeguradoFK": cpf}))
                segurado["Arquivos"] = self.sanitize_documents(arquivos)
            return self.sanitize_document(segurado)
        except Exception as e:
            logger.error(f"Erro ao buscar segurado {cpf}: {e}")
            return None

    def atualizar(self, cpf, atualizacao):
        if not self.connected:
            return {"sucesso": False, "erro": "MongoDB offline"}
        if "cpf" in atualizacao and atualizacao["cpf"] != cpf:
            return {"sucesso": False, "erro": "Não é possível alterar o CPF"}
        try:
            atualizacao["data_atualizacao"] = BaseHandler.add_timestamps({})["data_atualizacao"]
            result = self.segurados.update_one({"cpf": cpf}, {"$set": atualizacao})
            if result.matched_count == 0:
                return {"sucesso": False, "erro": f"Segurado {cpf} não encontrado"}
            return {"sucesso": True, "mensagem": "Atualizado com sucesso" if result.modified_count > 0 else "Nenhuma alteração necessária"}
        except Exception as e:
            logger.error(f"Erro ao atualizar segurado {cpf}: {e}")
            return {"sucesso": False, "erro": str(e)}

    def deletar(self, cpf):
        if not self.connected:
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            if self.arquivos.count_documents({"SeguradoFK": cpf}) > 0:
                return {"sucesso": False, "erro": f"Segurado {cpf} possui arquivos vinculados"}
            result = self.segurados.delete_one({"cpf": cpf})
            if result.deleted_count > 0:
                return {"sucesso": True, "mensagem": f"Segurado {cpf} deletado com sucesso"}
            return {"sucesso": False, "erro": f"Segurado {cpf} não encontrado"}
        except Exception as e:
            logger.error(f"Erro ao deletar segurado {cpf}: {e}")
            return {"sucesso": False, "erro": str(e)}
