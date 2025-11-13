import logging
from pymongo.errors import DuplicateKeyError
from base_handler import BaseHandler

logger = logging.getLogger(__name__)

class ArquivosHandler(BaseHandler):
    def __init__(self, connection):
        self.connected = connection.is_connected()
        if self.connected:
            self.arquivos = connection.db.arquivos
            self.caixas = connection.db.caixas
            self.segurados = connection.db.segurados
            self._criar_indices()

    def _criar_indices(self):
        try:
            self.arquivos.create_index("NB", unique=True)
            self.arquivos.create_index("Caixa_codigo")
            self.arquivos.create_index("SeguradoFK")
            self.arquivos.create_index("APS")
            logger.info("✅ Índices de arquivos criados/verificados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao criar índices de arquivos: {e}")

    def inserir(self, arquivo_dict):
        if not self.connected:
            return {"sucesso": False, "erro": "MongoDB offline"}

        try:
            # Verificação integridade
            if not self.caixas.find_one({"codigo": arquivo_dict["Caixa_codigo"]}):
                return {"sucesso": False, "erro": f"Caixa {arquivo_dict['Caixa_codigo']} não existe"}
            if not self.segurados.find_one({"cpf": arquivo_dict["SeguradoFK"]}):
                return {"sucesso": False, "erro": f"Segurado {arquivo_dict['SeguradoFK']} não existe"}

            arquivo_dict = self.add_timestamps(arquivo_dict)
            result = self.arquivos.insert_one(arquivo_dict)
            return {"sucesso": True, "id": str(result.inserted_id)}

        except DuplicateKeyError:
            return {"sucesso": False, "erro": f"Arquivo {arquivo_dict['NB']} já existe"}
        except Exception as e:
            logger.error(f"Erro ao inserir arquivo: {e}")
            return {"sucesso": False, "erro": str(e)}

    def listar(self, filtro=None):
        if not self.connected:
            return []
        try:
            arquivos = list(self.arquivos.find(filtro) if filtro else self.arquivos.find())
            return self.sanitize_documents(arquivos)
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {e}")
            return []

    def buscar(self, NB):
        if not self.connected:
            return None
        try:
            arquivo = self.arquivos.find_one({"NB": NB})
            return self.sanitize_document(arquivo)
        except Exception as e:
            logger.error(f"Erro ao buscar arquivo {NB}: {e}")
            return None

    def atualizar(self, NB, atualizacao):
        if not self.connected:
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            if "Caixa_codigo" in atualizacao:
                if not self.caixas.find_one({"codigo": atualizacao["Caixa_codigo"]}):
                    return {"sucesso": False, "erro": f"Caixa {atualizacao['Caixa_codigo']} não existe"}
            if "SeguradoFK" in atualizacao:
                if not self.segurados.find_one({"cpf": atualizacao["SeguradoFK"]}):
                    return {"sucesso": False, "erro": f"Segurado {atualizacao['SeguradoFK']} não existe"}

            atualizacao["data_atualizacao"] = BaseHandler.add_timestamps({})["data_atualizacao"]
            result = self.arquivos.update_one({"NB": NB}, {"$set": atualizacao})

            if result.matched_count == 0:
                return {"sucesso": False, "erro": f"Arquivo {NB} não encontrado"}
            return {"sucesso": True, "mensagem": "Atualizado com sucesso" if result.modified_count > 0 else "Nenhuma alteração necessária"}

        except Exception as e:
            logger.error(f"Erro ao atualizar arquivo {NB}: {e}")
            return {"sucesso": False, "erro": str(e)}

    def deletar(self, NB):
        if not self.connected:
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            result = self.arquivos.delete_one({"NB": NB})
            if result.deleted_count > 0:
                return {"sucesso": True, "mensagem": f"Arquivo {NB} deletado com sucesso"}
            return {"sucesso": False, "erro": f"Arquivo {NB} não encontrado"}
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo {NB}: {e}")
            return {"sucesso": False, "erro": str(e)}
