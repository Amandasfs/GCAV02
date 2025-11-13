import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class MongoDBConnection:
    def __init__(self, connection_string="mongodb://localhost:27017/", db_name="GCA_DB"):
        self.connected = False
        self.client = None
        self.db = None
        try:
            logger.info("🔗 Tentando conectar ao MongoDB...")
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
                retryReads=True
            )
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            self.connected = True
            logger.info("✅ MongoDB conectado com sucesso!")
        except ConnectionFailure:
            logger.warning("⚠️ Não foi possível conectar ao MongoDB.")
        except ServerSelectionTimeoutError:
            logger.warning("⚠️ Timeout na conexão com MongoDB.")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao conectar ao MongoDB: {e}")

    def is_connected(self):
        if not self.connected:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            self.connected = False
            return False

    def close(self):
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("🔌 Conexão com MongoDB fechada")
