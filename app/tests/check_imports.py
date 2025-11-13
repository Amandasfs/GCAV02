#!/usr/bin/env python3

def test_imports():
    print("Testando importações...")
    
    try:
        from flask import Flask
        print("Flask importado")
    except ImportError as e:
        print(f"Flask: {e}")
    
    try:
        from auth import requer_autenticacao
        print("Auth importado")
    except ImportError as e:
        print(f"Auth: {e}")
    
    try:
        from database.mongo_handler import MongoDBHandler
        print("MongoDBHandler importado")
    except ImportError as e:
        print(f"MongoDBHandler: {e}")
    
    try:
        from database.json_handler import JSONHandler
        print("JSONHandler importado")
    except ImportError as e:
        print(f"JSONHandler: {e}")
    
    try:
        from GCA.routes.caixas import caixas_bp
        print("Caixas blueprint importado")
    except ImportError as e:
        print(f"Caixas blueprint: {e}")
    
    try:
        from routes.arquivos import arquivos_bp
        print("Arquivos blueprint importado")
    except ImportError as e:
        print(f"Arquivos blueprint: {e}")
    
    try:
        from routes.segurados import segurados_bp
        print("Segurados blueprint importado")
    except ImportError as e:
        print(f"Segurados blueprint: {e}")
    
    print("Teste de importações concluído!")

if __name__ == "__main__":
    test_imports()