import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoDBHandler:
    def __init__(self, connection_string="mongodb://localhost:27017/", db_name="GCA_DB"):
        self.connected = False
        self.client = None
        self.db = None
        self.caixas = None
        self.arquivos = None
        self.segurados = None

        try:
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

            logger.info("🔗 Tentando conectar ao MongoDB...")

            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
                retryReads=True
            )

            # Testar conexão
            self.client.admin.command('ping')
            self.db = self.client[db_name]

            # Inicializar coleções
            self.caixas = self.db.caixas
            self.arquivos = self.db.arquivos
            self.segurados = self.db.segurados

            self.connected = True
            logger.info("✅ MongoDB conectado com sucesso!")

            # Criar índices
            self._criar_indices()

        except ImportError:
            logger.warning("⚠️ PyMongo não instalado. MongoDB não disponível.")
        except ConnectionFailure:
            logger.warning("⚠️ Não foi possível conectar ao MongoDB. Verifique se o serviço está rodando.")
        except ServerSelectionTimeoutError:
            logger.warning("⚠️ Timeout na conexão com MongoDB.")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao conectar com MongoDB: {e}")

    def _criar_indices(self):
        if not self.connected:
            return
        try:
            # Chaves únicas
            self.caixas.create_index("codigo", unique=True)
            self.arquivos.create_index("NB", unique=True)
            self.segurados.create_index("cpf", unique=True)
            # Índices de consulta
            self.arquivos.create_index("Caixa_codigo")
            self.arquivos.create_index("SeguradoFK")
            self.arquivos.create_index("APS")
            self.caixas.create_index("prateleira")
            self.caixas.create_index("bloco")
            logger.info("✅ Índices do MongoDB criados/verificados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao criar índices: {e}")

    def is_connected(self):
        if not self.connected:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            self.connected = False
            return False

    def _to_public(self, doc):
        if not doc:
            return None
        d = doc.copy()
        # Converte ObjectId para str
        if '_id' in d:
            d['_id'] = str(d['_id'])
        return d

    def _list_to_public(self, docs):
        return [self._to_public(d) for d in docs]

    # =================== CAIXAS ===================
    def criar_caixa(self, caixa_dict):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            from pymongo.errors import DuplicateKeyError

            now = datetime.now().isoformat()
            caixa_dict["data_criacao"] = now
            caixa_dict["data_atualizacao"] = now

            result = self.caixas.insert_one(caixa_dict)
            logger.info(f"📦 Caixa {caixa_dict['codigo']} salva no MongoDB")
            return {"sucesso": True, "id": str(result.inserted_id), "mensagem": f"Caixa {caixa_dict['codigo']} criada com sucesso"}
        except DuplicateKeyError:
            msg = f"Caixa com código {caixa_dict['codigo']} já existe"
            return {"sucesso": False, "erro": msg}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao inserir caixa: {e}"}

    def buscar_caixa(self, codigo):
        if not self.is_connected():
            return None
        try:
            caixa = self.caixas.find_one({"codigo": codigo})
            return self._to_public(caixa)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar caixa {codigo}: {e}")
            return None

    def listar_caixas(self, filtro=None):
        if not self.is_connected():
            return []
        try:
            query = filtro or {}
            docs = list(self.caixas.find(query))
            return self._list_to_public(docs)
        except Exception as e:
            logger.error(f"❌ Erro ao listar caixas: {e}")
            return []

    def atualizar_caixa(self, codigo, atualizacao):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            atualizacao["data_atualizacao"] = datetime.now().isoformat()
            result = self.caixas.update_one({"codigo": codigo}, {"$set": atualizacao})
            if result.matched_count == 0:
                return {"sucesso": False, "erro": f"Caixa {codigo} não encontrada"}
            if result.modified_count > 0:
                return {"sucesso": True, "mensagem": f"Caixa {codigo} atualizada com sucesso"}
            return {"sucesso": True, "mensagem": "Nenhuma alteração necessária"}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao atualizar caixa {codigo}: {e}"}

    def deletar_caixa(self, codigo):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            # impedimento por integridade
            qtd = self.arquivos.count_documents({"Caixa_codigo": codigo})
            if qtd > 0:
                return {"sucesso": False, "erro": f"Não é possível deletar a caixa {codigo}. Existem {qtd} arquivos vinculados."}
            result = self.caixas.delete_one({"codigo": codigo})
            if result.deleted_count > 0:
                return {"sucesso": True, "mensagem": f"Caixa {codigo} deletada com sucesso"}
            return {"sucesso": False, "erro": f"Caixa {codigo} não encontrada"}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao deletar caixa {codigo}: {e}"}

    # =================== ARQUIVOS ===================
    def criar_arquivo(self, arquivo_dict):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            from pymongo.errors import DuplicateKeyError

            # integridade referencial
            if not self.caixas.find_one({"codigo": arquivo_dict["Caixa_codigo"]}):
                return {"sucesso": False, "erro": f"Caixa {arquivo_dict['Caixa_codigo']} não existe"}
            if not self.segurados.find_one({"cpf": arquivo_dict["SeguradoFK"]}):
                return {"sucesso": False, "erro": f"Segurado {arquivo_dict['SeguradoFK']} não existe"}

            now = datetime.now().isoformat()
            arquivo_dict["data_criacao"] = now
            arquivo_dict["data_atualizacao"] = now

            result = self.arquivos.insert_one(arquivo_dict)
            logger.info(f"📁 Arquivo {arquivo_dict['NB']} salvo no MongoDB")
            # retorna documento público
            inserted = self.arquivos.find_one({"_id": result.inserted_id})
            return self._to_public(inserted)
        except DuplicateKeyError:
            return {"sucesso": False, "erro": f"Arquivo com NB {arquivo_dict['NB']} já existe"}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao inserir arquivo: {e}"}

    def buscar_arquivo(self, NB):
        if not self.is_connected():
            return None
        try:
            arq = self.arquivos.find_one({"NB": NB})
            return self._to_public(arq)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar arquivo {NB}: {e}")
            return None

    def listar_arquivos(self, filtro=None):
        if not self.is_connected():
            return []
        try:
            query = filtro or {}
            docs = list(self.arquivos.find(query))
            return self._list_to_public(docs)
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos: {e}")
            return []

    def atualizar_arquivo(self, NB, atualizacao):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            # checar integridade nas mudanças
            if "Caixa_codigo" in atualizacao:
                if not self.caixas.find_one({"codigo": atualizacao["Caixa_codigo"]}):
                    return {"sucesso": False, "erro": f"Caixa {atualizacao['Caixa_codigo']} não existe"}
            if "SeguradoFK" in atualizacao:
                if not self.segurados.find_one({"cpf": atualizacao["SeguradoFK"]}):
                    return {"sucesso": False, "erro": f"Segurado {atualizacao['SeguradoFK']} não existe"}

            atualizacao["data_atualizacao"] = datetime.now().isoformat()
            result = self.arquivos.update_one({"NB": NB}, {"$set": atualizacao})
            if result.matched_count == 0:
                return {"sucesso": False, "erro": f"Arquivo {NB} não encontrado"}
            if result.modified_count > 0:
                return {"sucesso": True, "mensagem": f"Arquivo {NB} atualizado com sucesso"}
            return {"sucesso": True, "mensagem": "Nenhuma alteração necessária"}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao atualizar arquivo {NB}: {e}"}

    def deletar_arquivo(self, NB):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            result = self.arquivos.delete_one({"NB": NB})
            if result.deleted_count > 0:
                return {"sucesso": True, "mensagem": f"Arquivo {NB} deletado com sucesso"}
            return {"sucesso": False, "erro": f"Arquivo {NB} não encontrado"}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao deletar arquivo {NB}: {e}"}

    def buscar_arquivos_por_caixa(self, codigo):
        if not self.is_connected():
            return []
        try:
            docs = list(self.arquivos.find({"Caixa_codigo": codigo}))
            return self._list_to_public(docs)
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos da caixa {codigo}: {e}")
            return []

    def buscar_arquivos_por_segurado(self, cpf):
        if not self.is_connected():
            return []
        try:
            docs = list(self.arquivos.find({"SeguradoFK": cpf}))
            return self._list_to_public(docs)
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos do segurado {cpf}: {e}")
            return []

    # =================== SEGURADOS ===================
    def criar_segurado(self, segurado_dict):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            from pymongo.errors import DuplicateKeyError

            now = datetime.now().isoformat()
            segurado_dict["data_criacao"] = now
            segurado_dict["data_atualizacao"] = now
            segurado_dict["Arquivos"] = []

            result = self.segurados.insert_one(segurado_dict)
            logger.info(f"👤 Segurado {segurado_dict['cpf']} salvo no MongoDB")
            inserted = self.segurados.find_one({"_id": result.inserted_id})
            return self._to_public(inserted)
        except DuplicateKeyError:
            return {"sucesso": False, "erro": f"Segurado com CPF {segurado_dict['cpf']} já existe"}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao inserir segurado: {e}"}

    def buscar_segurado(self, cpf):
        if not self.is_connected():
            return None
        try:
            seg = self.segurados.find_one({"cpf": cpf})
            if not seg:
                return None
            seg_pub = self._to_public(seg)
            # anexar arquivos
            seg_pub["Arquivos"] = self.listar_arquivos({"SeguradoFK": cpf})
            return seg_pub
        except Exception as e:
            logger.error(f"❌ Erro ao buscar segurado {cpf}: {e}")
            return None

    def listar_segurados(self, filtro=None):
        if not self.is_connected():
            return []
        try:
            query = filtro or {}
            docs = list(self.segurados.find(query))
            result = self._list_to_public(docs)
            # contagem de arquivos
            for s in result:
                cpf = s.get("cpf")
                s["total_arquivos"] = self.arquivos.count_documents({"SeguradoFK": cpf})
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao listar segurados: {e}")
            return []

    def atualizar_segurado(self, cpf, atualizacao):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            if "cpf" in atualizacao and atualizacao["cpf"] != cpf:
                return {"sucesso": False, "erro": "Não é possível alterar o CPF de um segurado"}
            atualizacao["data_atualizacao"] = datetime.now().isoformat()
            result = self.segurados.update_one({"cpf": cpf}, {"$set": atualizacao})
            if result.matched_count == 0:
                return {"sucesso": False, "erro": f"Segurado {cpf} não encontrado"}
            if result.modified_count > 0:
                return {"sucesso": True, "mensagem": f"Segurado {cpf} atualizado com sucesso"}
            return {"sucesso": True, "mensagem": "Nenhuma alteração necessária"}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao atualizar segurado {cpf}: {e}"}

    def deletar_segurado(self, cpf):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            qtd = self.arquivos.count_documents({"SeguradoFK": cpf})
            if qtd > 0:
                return {"sucesso": False, "erro": f"Não é possível deletar o segurado {cpf}. Existem {qtd} arquivos vinculados."}
            result = self.segurados.delete_one({"cpf": cpf})
            if result.deleted_count > 0:
                return {"sucesso": True, "mensagem": f"Segurado {cpf} deletado com sucesso"}
            return {"sucesso": False, "erro": f"Segurado {cpf} não encontrado"}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao deletar segurado {cpf}: {e}"}

    # =================== SINCRONIZAÇÃO/ESTATÍSTICAS ===================
    def sincronizar_com_json(self, json_data):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            stats = {"caixas_importadas": 0, "arquivos_importados": 0, "segurados_importados": 0, "erros": []}

            # Caixas
            for caixa in json_data.get("caixas", []):
                try:
                    c = caixa.copy()
                    c.pop("_id", None)
                    result = self.caixas.replace_one({"codigo": c["codigo"]}, c, upsert=True)
                    if result.upserted_id:
                        stats["caixas_importadas"] += 1
                except Exception as e:
                    stats["erros"].append(f"Caixa {caixa.get('codigo','N/A')}: {e}")

            # Segurados
            for segurado in json_data.get("segurados", []):
                try:
                    s = segurado.copy()
                    s.pop("_id", None)
                    result = self.segurados.replace_one({"cpf": s["cpf"]}, s, upsert=True)
                    if result.upserted_id:
                        stats["segurados_importados"] += 1
                except Exception as e:
                    stats["erros"].append(f"Segurado {segurado.get('cpf','N/A')}: {e}")

            # Arquivos
            for arquivo in json_data.get("arquivos", []):
                try:
                    a = arquivo.copy()
                    a.pop("_id", None)
                    result = self.arquivos.replace_one({"NB": a["NB"]}, a, upsert=True)
                    if result.upserted_id:
                        stats["arquivos_importados"] += 1
                except Exception as e:
                    stats["erros"].append(f"Arquivo {arquivo.get('NB','N/A')}: {e}")

            logger.info("🔄 Sincronização MongoDB/JSON concluída")
            stats["sucesso"] = True
            return stats
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro na sincronização: {e}"}

    def get_stats(self):
        if not self.is_connected():
            return {"total_caixas": 0, "total_arquivos": 0, "total_segurados": 0, "status": "offline", "database": "MongoDB"}
        try:
            total_caixas = self.caixas.count_documents({})
            total_arquivos = self.arquivos.count_documents({})
            total_segurados = self.segurados.count_documents({})

            arq_caixa = list(self.arquivos.aggregate([{"$group": {"_id": "$Caixa_codigo", "count": {"$sum": 1}}}]))
            arq_seg = list(self.arquivos.aggregate([{"$group": {"_id": "$SeguradoFK", "count": {"$sum": 1}}}]))

            return {
                "total_caixas": total_caixas,
                "total_arquivos": total_arquivos,
                "total_segurados": total_segurados,
                "status": "online",
                "database": "MongoDB",
                "estatisticas_avancadas": {
                    "caixas_com_arquivos": len(arq_caixa),
                    "segurados_com_arquivos": len(arq_seg),
                    "caixa_mais_arquivos": max([a["count"] for a in arq_caixa]) if arq_caixa else 0,
                    "segurado_mais_arquivos": max([a["count"] for a in arq_seg]) if arq_seg else 0
                }
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {"total_caixas": 0, "total_arquivos": 0, "total_segurados": 0, "status": "error", "database": "MongoDB", "erro": str(e)}

    def limpar_tudo(self):
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        try:
            r1 = self.caixas.delete_many({})
            r2 = self.arquivos.delete_many({})
            r3 = self.segurados.delete_many({})
            logger.warning("🗑️ TODOS os dados do MongoDB foram limpos!")
            return {
                "sucesso": True,
                "mensagem": "Todos os dados foram limpos com sucesso",
                "estatisticas": {
                    "caixas_deletadas": r1.deleted_count,
                    "arquivos_deletados": r2.deleted_count,
                    "segurados_deletados": r3.deleted_count
                }
            }
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao limpar dados: {e}"}

    def close(self):
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("🔌 Conexão com MongoDB fechada")
