# app/mongo/base_handler.py
from datetime import datetime

class BaseHandler:
    """Classe base com utilitários comuns"""

    @staticmethod
    def sanitize_document(document):
        if document and '_id' in document:
            document = document.copy()
            document['_id'] = str(document['_id'])
        return document

    @staticmethod
    def sanitize_documents(documents):
        return [BaseHandler.sanitize_document(doc) for doc in documents]

    @staticmethod
    def add_timestamps(item):
        item["data_criacao"] = datetime.now().isoformat()
        item["data_atualizacao"] = datetime.now().isoformat()
        return item
