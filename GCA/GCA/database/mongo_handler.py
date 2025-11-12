import logging
from datetime import datetime
from bson import ObjectId
import json

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
            from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, DuplicateKeyError
            
            logger.info("🔗 Tentando conectar ao MongoDB...")
            
            # Configurar timeout para não travar a aplicação
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,  # 5 segundos timeout
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
            
            # Criar índices para melhor performance
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
        """Cria índices para melhor performance das consultas"""
        if self.connected:
            try:
                # Índices únicos para chaves primárias
                self.caixas.create_index("codigo", unique=True)
                self.arquivos.create_index("NB", unique=True)
                self.segurados.create_index("cpf", unique=True)
                
                # Índices para consultas frequentes
                self.arquivos.create_index("Caixa_codigo")
                self.arquivos.create_index("SeguradoFK")
                self.arquivos.create_index("APS")
                self.caixas.create_index("prateleira")
                self.caixas.create_index("bloco")
                
                logger.info("✅ Índices do MongoDB criados/verificados")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao criar índices: {e}")
    
    def is_connected(self):
        """Verifica se está conectado ao MongoDB"""
        if not self.connected:
            return False
        
        try:
            self.client.admin.command('ping')
            return True
        except:
            self.connected = False
            return False
    
    def _sanitize_document(self, document):
        """Remove _id do documento para evitar conflitos na serialização"""
        if document and '_id' in document:
            document = document.copy()
            document['_id'] = str(document['_id'])
        return document
    
    def _sanitize_documents(self, documents):
        """Remove _id de uma lista de documentos"""
        return [self._sanitize_document(doc) for doc in documents]
    
    # ========== OPERAÇÕES PARA CAIXAS ==========
    def inserir_caixa(self, caixa_dict):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            from pymongo.errors import DuplicateKeyError
            
            # Adicionar timestamps
            caixa_dict["data_criacao"] = datetime.now().isoformat()
            caixa_dict["data_atualizacao"] = datetime.now().isoformat()
            
            result = self.caixas.insert_one(caixa_dict)
            logger.info(f"📦 Caixa {caixa_dict['codigo']} salva no MongoDB")
            
            return {
                "sucesso": True,
                "id": str(result.inserted_id),
                "mensagem": f"Caixa {caixa_dict['codigo']} criada com sucesso"
            }
            
        except DuplicateKeyError:
            erro_msg = f"Caixa com código {caixa_dict['codigo']} já existe"
            logger.warning(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
        except Exception as e:
            erro_msg = f"Erro ao inserir caixa no MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    def buscar_caixa(self, codigo):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            caixa = self.caixas.find_one({"codigo": codigo})
            return self._sanitize_document(caixa)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar caixa {codigo} no MongoDB: {e}")
            return None
    
    def listar_caixas(self, filtro=None):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return []
        
        try:
            if filtro:
                caixas = list(self.caixas.find(filtro))
            else:
                caixas = list(self.caixas.find())
            return self._sanitize_documents(caixas)
        except Exception as e:
            logger.error(f"❌ Erro ao listar caixas no MongoDB: {e}")
            return []
    
    def atualizar_caixa(self, codigo, atualizacao):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            # Atualizar timestamp
            atualizacao["data_atualizacao"] = datetime.now().isoformat()
            
            result = self.caixas.update_one(
                {"codigo": codigo}, 
                {"$set": atualizacao}
            )
            
            if result.matched_count == 0:
                return {"sucesso": False, "erro": f"Caixa {codigo} não encontrada"}
                
            if result.modified_count > 0:
                logger.info(f"📦 Caixa {codigo} atualizada no MongoDB")
                return {"sucesso": True, "mensagem": f"Caixa {codigo} atualizada com sucesso"}
            else:
                return {"sucesso": True, "mensagem": "Nenhuma alteração necessária"}
                
        except Exception as e:
            erro_msg = f"Erro ao atualizar caixa {codigo} no MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    def deletar_caixa(self, codigo):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            # Verificar se existem arquivos na caixa
            arquivos_na_caixa = self.arquivos.count_documents({"Caixa_codigo": codigo})
            if arquivos_na_caixa > 0:
                return {
                    "sucesso": False, 
                    "erro": f"Não é possível deletar a caixa {codigo}. Existem {arquivos_na_caixa} arquivos vinculados a ela."
                }
            
            result = self.caixas.delete_one({"codigo": codigo})
            
            if result.deleted_count > 0:
                logger.info(f"📦 Caixa {codigo} deletada do MongoDB")
                return {"sucesso": True, "mensagem": f"Caixa {codigo} deletada com sucesso"}
            else:
                return {"sucesso": False, "erro": f"Caixa {codigo} não encontrada"}
                
        except Exception as e:
            erro_msg = f"Erro ao deletar caixa {codigo} no MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    # ========== OPERAÇÕES PARA ARQUIVOS ==========
    def inserir_arquivo(self, arquivo_dict):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            from pymongo.errors import DuplicateKeyError
            
            # Verificar se a caixa existe
            caixa_existe = self.caixas.find_one({"codigo": arquivo_dict["Caixa_codigo"]})
            if not caixa_existe:
                return {"sucesso": False, "erro": f"Caixa {arquivo_dict['Caixa_codigo']} não existe"}
            
            # Verificar se o segurado existe
            segurado_existe = self.segurados.find_one({"cpf": arquivo_dict["SeguradoFK"]})
            if not segurado_existe:
                return {"sucesso": False, "erro": f"Segurado {arquivo_dict['SeguradoFK']} não existe"}
            
            # Adicionar timestamps
            arquivo_dict["data_criacao"] = datetime.now().isoformat()
            arquivo_dict["data_atualizacao"] = datetime.now().isoformat()
            
            result = self.arquivos.insert_one(arquivo_dict)
            logger.info(f"📁 Arquivo {arquivo_dict['NB']} salvo no MongoDB")
            
            return {
                "sucesso": True,
                "id": str(result.inserted_id),
                "mensagem": f"Arquivo {arquivo_dict['NB']} criado com sucesso"
            }
            
        except DuplicateKeyError:
            erro_msg = f"Arquivo com NB {arquivo_dict['NB']} já existe"
            logger.warning(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
        except Exception as e:
            erro_msg = f"Erro ao inserir arquivo no MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    def buscar_arquivo(self, NB):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            arquivo = self.arquivos.find_one({"NB": NB})
            return self._sanitize_document(arquivo)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar arquivo {NB} no MongoDB: {e}")
            return None
    
    def listar_arquivos(self, filtro=None):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return []
        
        try:
            if filtro:
                arquivos = list(self.arquivos.find(filtro))
            else:
                arquivos = list(self.arquivos.find())
            return self._sanitize_documents(arquivos)
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos no MongoDB: {e}")
            return []
    
    def atualizar_arquivo(self, NB, atualizacao):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            # Verificar integridade referencial se estiver atualizando Caixa_codigo ou SeguradoFK
            if "Caixa_codigo" in atualizacao:
                caixa_existe = self.caixas.find_one({"codigo": atualizacao["Caixa_codigo"]})
                if not caixa_existe:
                    return {"sucesso": False, "erro": f"Caixa {atualizacao['Caixa_codigo']} não existe"}
            
            if "SeguradoFK" in atualizacao:
                segurado_existe = self.segurados.find_one({"cpf": atualizacao["SeguradoFK"]})
                if not segurado_existe:
                    return {"sucesso": False, "erro": f"Segurado {atualizacao['SeguradoFK']} não existe"}
            
            # Atualizar timestamp
            atualizacao["data_atualizacao"] = datetime.now().isoformat()
            
            result = self.arquivos.update_one(
                {"NB": NB}, 
                {"$set": atualizacao}
            )
            
            if result.matched_count == 0:
                return {"sucesso": False, "erro": f"Arquivo {NB} não encontrado"}
                
            if result.modified_count > 0:
                logger.info(f"📁 Arquivo {NB} atualizado no MongoDB")
                return {"sucesso": True, "mensagem": f"Arquivo {NB} atualizado com sucesso"}
            else:
                return {"sucesso": True, "mensagem": "Nenhuma alteração necessária"}
                
        except Exception as e:
            erro_msg = f"Erro ao atualizar arquivo {NB} no MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    def deletar_arquivo(self, NB):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            result = self.arquivos.delete_one({"NB": NB})
            
            if result.deleted_count > 0:
                logger.info(f"📁 Arquivo {NB} deletado do MongoDB")
                return {"sucesso": True, "mensagem": f"Arquivo {NB} deletado com sucesso"}
            else:
                return {"sucesso": False, "erro": f"Arquivo {NB} não encontrado"}
                
        except Exception as e:
            erro_msg = f"Erro ao deletar arquivo {NB} no MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    # ========== OPERAÇÕES PARA SEGURADOS ==========
    def inserir_segurado(self, segurado_dict):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            from pymongo.errors import DuplicateKeyError
            
            # Adicionar timestamps
            segurado_dict["data_criacao"] = datetime.now().isoformat()
            segurado_dict["data_atualizacao"] = datetime.now().isoformat()
            segurado_dict["Arquivos"] = []  # Inicializar lista de arquivos vazia
            
            result = self.segurados.insert_one(segurado_dict)
            logger.info(f"👤 Segurado {segurado_dict['cpf']} salvo no MongoDB")
            
            return {
                "sucesso": True,
                "id": str(result.inserted_id),
                "mensagem": f"Segurado {segurado_dict['cpf']} criado com sucesso"
            }
            
        except DuplicateKeyError:
            erro_msg = f"Segurado com CPF {segurado_dict['cpf']} já existe"
            logger.warning(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
        except Exception as e:
            erro_msg = f"Erro ao inserir segurado no MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    def buscar_segurado(self, cpf):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            segurado = self.segurados.find_one({"cpf": cpf})
            if segurado:
                # Buscar arquivos do segurado
                arquivos_segurado = self.listar_arquivos({"SeguradoFK": cpf})
                segurado["Arquivos"] = arquivos_segurado
            
            return self._sanitize_document(segurado)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar segurado {cpf} no MongoDB: {e}")
            return None
    
    def listar_segurados(self, filtro=None):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return []
        
        try:
            if filtro:
                segurados = list(self.segurados.find(filtro))
            else:
                segurados = list(self.segurados.find())
            
            segurados_sanitized = self._sanitize_documents(segurados)
            
            # Adicionar contagem de arquivos para cada segurado
            for segurado in segurados_sanitized:
                if segurado:
                    contagem_arquivos = self.arquivos.count_documents({"SeguradoFK": segurado["cpf"]})
                    segurado["total_arquivos"] = contagem_arquivos
            
            return segurados_sanitized
        except Exception as e:
            logger.error(f"❌ Erro ao listar segurados no MongoDB: {e}")
            return []
    
    def atualizar_segurado(self, cpf, atualizacao):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            # Não permitir atualização do CPF (chave primária)
            if "cpf" in atualizacao and atualizacao["cpf"] != cpf:
                return {"sucesso": False, "erro": "Não é possível alterar o CPF de um segurado"}
            
            # Atualizar timestamp
            atualizacao["data_atualizacao"] = datetime.now().isoformat()
            
            result = self.segurados.update_one(
                {"cpf": cpf}, 
                {"$set": atualizacao}
            )
            
            if result.matched_count == 0:
                return {"sucesso": False, "erro": f"Segurado {cpf} não encontrado"}
                
            if result.modified_count > 0:
                logger.info(f"👤 Segurado {cpf} atualizado no MongoDB")
                return {"sucesso": True, "mensagem": f"Segurado {cpf} atualizado com sucesso"}
            else:
                return {"sucesso": True, "mensagem": "Nenhuma alteração necessária"}
                
        except Exception as e:
            erro_msg = f"Erro ao atualizar segurado {cpf} no MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    def deletar_segurado(self, cpf):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            # Verificar se existem arquivos vinculados ao segurado
            arquivos_segurado = self.arquivos.count_documents({"SeguradoFK": cpf})
            if arquivos_segurado > 0:
                return {
                    "sucesso": False, 
                    "erro": f"Não é possível deletar o segurado {cpf}. Existem {arquivos_segurado} arquivos vinculados a ele."
                }
            
            result = self.segurados.delete_one({"cpf": cpf})
            
            if result.deleted_count > 0:
                logger.info(f"👤 Segurado {cpf} deletado do MongoDB")
                return {"sucesso": True, "mensagem": f"Segurado {cpf} deletado com sucesso"}
            else:
                return {"sucesso": False, "erro": f"Segurado {cpf} não encontrado"}
                
        except Exception as e:
            erro_msg = f"Erro ao deletar segurado {cpf} no MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    # ========== OPERAÇÕES DE SINCRONIZAÇÃO E ESTATÍSTICAS ==========
    def sincronizar_com_json(self, json_data):
        """Sincroniza dados do JSON com MongoDB"""
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            stats = {
                "caixas_importadas": 0,
                "arquivos_importados": 0,
                "segurados_importados": 0,
                "erros": []
            }
            
            # Sincronizar caixas
            for caixa in json_data.get("caixas", []):
                try:
                    # Remover _id se existir para evitar conflito
                    caixa_copy = caixa.copy()
                    if "_id" in caixa_copy:
                        del caixa_copy["_id"]
                    
                    result = self.caixas.replace_one(
                        {"codigo": caixa["codigo"]}, 
                        caixa_copy, 
                        upsert=True
                    )
                    if result.upserted_id:
                        stats["caixas_importadas"] += 1
                except Exception as e:
                    stats["erros"].append(f"Caixa {caixa.get('codigo', 'N/A')}: {str(e)}")
            
            # Sincronizar segurados
            for segurado in json_data.get("segurados", []):
                try:
                    segurado_copy = segurado.copy()
                    if "_id" in segurado_copy:
                        del segurado_copy["_id"]
                    
                    result = self.segurados.replace_one(
                        {"cpf": segurado["cpf"]}, 
                        segurado_copy, 
                        upsert=True
                    )
                    if result.upserted_id:
                        stats["segurados_importados"] += 1
                except Exception as e:
                    stats["erros"].append(f"Segurado {segurado.get('cpf', 'N/A')}: {str(e)}")
            
            # Sincronizar arquivos
            for arquivo in json_data.get("arquivos", []):
                try:
                    arquivo_copy = arquivo.copy()
                    if "_id" in arquivo_copy:
                        del arquivo_copy["_id"]
                    
                    result = self.arquivos.replace_one(
                        {"NB": arquivo["NB"]}, 
                        arquivo_copy, 
                        upsert=True
                    )
                    if result.upserted_id:
                        stats["arquivos_importados"] += 1
                except Exception as e:
                    stats["erros"].append(f"Arquivo {arquivo.get('NB', 'N/A')}: {str(e)}")
            
            logger.info("🔄 Sincronização MongoDB/JSON concluída")
            stats["sucesso"] = True
            return stats
            
        except Exception as e:
            erro_msg = f"Erro na sincronização MongoDB/JSON: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    def get_stats(self):
        """Retorna estatísticas detalhadas do MongoDB"""
        if not self.is_connected():
            return {
                "total_caixas": 0,
                "total_arquivos": 0,
                "total_segurados": 0,
                "status": "offline",
                "database": "MongoDB"
            }
        
        try:
            total_caixas = self.caixas.count_documents({})
            total_arquivos = self.arquivos.count_documents({})
            total_segurados = self.segurados.count_documents({})
            
            # Estatísticas adicionais
            arquivos_por_caixa = list(self.arquivos.aggregate([
                {"$group": {"_id": "$Caixa_codigo", "count": {"$sum": 1}}}
            ]))
            
            arquivos_por_segurado = list(self.arquivos.aggregate([
                {"$group": {"_id": "$SeguradoFK", "count": {"$sum": 1}}}
            ]))
            
            return {
                "total_caixas": total_caixas,
                "total_arquivos": total_arquivos,
                "total_segurados": total_segurados,
                "status": "online",
                "database": "MongoDB",
                "estatisticas_avancadas": {
                    "caixas_com_arquivos": len(arquivos_por_caixa),
                    "segurados_com_arquivos": len(arquivos_por_segurado),
                    "caixa_mais_arquivos": max([a["count"] for a in arquivos_por_caixa]) if arquivos_por_caixa else 0,
                    "segurado_mais_arquivos": max([a["count"] for a in arquivos_por_segurado]) if arquivos_por_segurado else 0
                }
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas do MongoDB: {e}")
            return {
                "total_caixas": 0,
                "total_arquivos": 0,
                "total_segurados": 0,
                "status": "error",
                "database": "MongoDB",
                "erro": str(e)
            }
    
    def limpar_tudo(self):
        """Limpa todos os dados do MongoDB (apenas desenvolvimento)"""
        if not self.is_connected():
            return {"sucesso": False, "erro": "MongoDB offline"}
        
        try:
            result_caixas = self.caixas.delete_many({})
            result_arquivos = self.arquivos.delete_many({})
            result_segurados = self.segurados.delete_many({})
            
            logger.warning("🗑️ TODOS os dados do MongoDB foram limpos!")
            
            return {
                "sucesso": True,
                "mensagem": "Todos os dados foram limpos com sucesso",
                "estatisticas": {
                    "caixas_deletadas": result_caixas.deleted_count,
                    "arquivos_deletados": result_arquivos.deleted_count,
                    "segurados_deletados": result_segurados.deleted_count
                }
            }
        except Exception as e:
            erro_msg = f"Erro ao limpar dados do MongoDB: {str(e)}"
            logger.error(f"❌ {erro_msg}")
            return {"sucesso": False, "erro": erro_msg}
    
    def close(self):
        """Fecha a conexão com o MongoDB"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("🔌 Conexão com MongoDB fechada")
