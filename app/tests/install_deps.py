# File: app/tests/install_deps.py
#!/usr/bin/env python3
import subprocess
import sys
import os

def install_dependencies():
    print("Instalando dependências...")
    
    dependencies = [
        "flask==2.3.3",
        "flask-cors==4.0.0", 
        "pymongo==4.5.0"
    ]
    
    for dep in dependencies:
        print(f"Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"{dep} instalado com sucesso")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao instalar {dep}: {e}")
            return False
    
    print("Todas as dependências instaladas!")
    return True

def test_imports():
    print("\nTestando importações...")
    
    imports_to_test = [
        ("Flask", "flask"),
        ("Flask-CORS", "flask_cors"),
        ("PyMongo", "pymongo")
    ]
    
    all_ok = True
    for name, module in imports_to_test:
        try:
            __import__(module)
            print(f"{name} importado com sucesso")
        except ImportError as e:
            print(f"Falha ao importar {name}: {e}")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    if install_dependencies():
        if test_imports():
            print("\nTodas as dependências estão funcionando!")
            print("Agora execute: python main.py")
        else:
            print("\n Algumas importações falharam")
            sys.exit(1)
    else:
        print("\n Falha na instalação das dependências")
        sys.exit(1)