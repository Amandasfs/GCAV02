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
            
            # Configurar timeout para não travar a aplicação
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,  # 5 segundos timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
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
                self.caixas.create_index("codigo", unique=True)
                self.arquivos.create_index("NB", unique=True)
                self.segurados.create_index("cpf", unique=True)
                self.arquivos.create_index("Caixa_codigo")
                self.arquivos.create_index("SeguradoFK")
                logger.info("✅ Índices do MongoDB criados")
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
    
    # ========== OPERAÇÕES PARA CAIXAS ==========
    def inserir_caixa(self, caixa_dict):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            result = self.caixas.insert_one(caixa_dict)
            logger.info(f"📦 Caixa {caixa_dict['codigo']} salva no MongoDB")
            return result.inserted_id
        except Exception as e:
            logger.error(f"❌ Erro ao inserir caixa no MongoDB: {e}")
            return None
    
    def buscar_caixa(self, codigo):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            caixa = self.caixas.find_one({"codigo": codigo})
            if caixa and '_id' in caixa:
                caixa['_id'] = str(caixa['_id'])  # Converter ObjectId para string
            return caixa
        except Exception as e:
            logger.error(f"❌ Erro ao buscar caixa no MongoDB: {e}")
            return None
    
    def listar_caixas(self):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return []
        
        try:
            caixas = list(self.caixas.find())
            for caixa in caixas:
                if '_id' in caixa:
                    caixa['_id'] = str(caixa['_id'])
            return caixas
        except Exception as e:
            logger.error(f"❌ Erro ao listar caixas no MongoDB: {e}")
            return []
    
    def atualizar_caixa(self, codigo, atualizacao):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            atualizacao["data_atualizacao"] = datetime.now()
            result = self.caixas.update_one(
                {"codigo": codigo}, 
                {"$set": atualizacao}
            )
            if result.modified_count > 0:
                logger.info(f"📦 Caixa {codigo} atualizada no MongoDB")
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar caixa no MongoDB: {e}")
            return None
    
    def deletar_caixa(self, codigo):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            result = self.caixas.delete_one({"codigo": codigo})
            if result.deleted_count > 0:
                logger.info(f"📦 Caixa {codigo} deletada do MongoDB")
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao deletar caixa no MongoDB: {e}")
            return None
    
    # ========== OPERAÇÕES PARA ARQUIVOS ==========
    def inserir_arquivo(self, arquivo_dict):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            result = self.arquivos.insert_one(arquivo_dict)
            logger.info(f"📁 Arquivo {arquivo_dict['NB']} salvo no MongoDB")
            return result.inserted_id
        except Exception as e:
            logger.error(f"❌ Erro ao inserir arquivo no MongoDB: {e}")
            return None
    
    def buscar_arquivo(self, NB):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            arquivo = self.arquivos.find_one({"NB": NB})
            if arquivo and '_id' in arquivo:
                arquivo['_id'] = str(arquivo['_id'])
            return arquivo
        except Exception as e:
            logger.error(f"❌ Erro ao buscar arquivo no MongoDB: {e}")
            return None
    
    def listar_arquivos(self):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return []
        
        try:
            arquivos = list(self.arquivos.find())
            for arquivo in arquivos:
                if '_id' in arquivo:
                    arquivo['_id'] = str(arquivo['_id'])
            return arquivos
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos no MongoDB: {e}")
            return []
    
    def atualizar_arquivo(self, NB, atualizacao):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            atualizacao["data_atualizacao"] = datetime.now()
            result = self.arquivos.update_one(
                {"NB": NB}, 
                {"$set": atualizacao}
            )
            if result.modified_count > 0:
                logger.info(f"📁 Arquivo {NB} atualizado no MongoDB")
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar arquivo no MongoDB: {e}")
            return None
    
    def deletar_arquivo(self, NB):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            result = self.arquivos.delete_one({"NB": NB})
            if result.deleted_count > 0:
                logger.info(f"📁 Arquivo {NB} deletado do MongoDB")
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao deletar arquivo no MongoDB: {e}")
            return None
    
    # ========== OPERAÇÕES PARA SEGURADOS ==========
    def inserir_segurado(self, segurado_dict):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            result = self.segurados.insert_one(segurado_dict)
            logger.info(f"👤 Segurado {segurado_dict['cpf']} salvo no MongoDB")
            return result.inserted_id
        except Exception as e:
            logger.error(f"❌ Erro ao inserir segurado no MongoDB: {e}")
            return None
    
    def buscar_segurado(self, cpf):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            segurado = self.segurados.find_one({"cpf": cpf})
            if segurado and '_id' in segurado:
                segurado['_id'] = str(segurado['_id'])
            return segurado
        except Exception as e:
            logger.error(f"❌ Erro ao buscar segurado no MongoDB: {e}")
            return None
    
    def listar_segurados(self):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return []
        
        try:
            segurados = list(self.segurados.find())
            for segurado in segurados:
                if '_id' in segurado:
                    segurado['_id'] = str(segurado['_id'])
            return segurados
        except Exception as e:
            logger.error(f"❌ Erro ao listar segurados no MongoDB: {e}")
            return []
    
    def atualizar_segurado(self, cpf, atualizacao):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            atualizacao["data_atualizacao"] = datetime.now()
            result = self.segurados.update_one(
                {"cpf": cpf}, 
                {"$set": atualizacao}
            )
            if result.modified_count > 0:
                logger.info(f"👤 Segurado {cpf} atualizado no MongoDB")
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar segurado no MongoDB: {e}")
            return None
    
    def deletar_segurado(self, cpf):
        if not self.is_connected():
            logger.warning("📝 MongoDB offline - operação apenas no JSON")
            return None
        
        try:
            result = self.segurados.delete_one({"cpf": cpf})
            if result.deleted_count > 0:
                logger.info(f"👤 Segurado {cpf} deletado do MongoDB")
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao deletar segurado no MongoDB: {e}")
            return None
    
    def get_stats(self):
        """Retorna estatísticas do MongoDB"""
        if not self.is_connected():
            return {
                "total_caixas": 0,
                "total_arquivos": 0,
                "total_segurados": 0,
                "status": "offline"
            }
        
        try:
            return {
                "total_caixas": self.caixas.count_documents({}),
                "total_arquivos": self.arquivos.count_documents({}),
                "total_segurados": self.segurados.count_documents({}),
                "status": "online"
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas do MongoDB: {e}")
            return {
                "total_caixas": 0,
                "total_arquivos": 0,
                "total_segurados": 0,
                "status": "error"
            }