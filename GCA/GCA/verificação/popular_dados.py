# popular_dados.py
import requests
import json
import base64

# Configurações
API_BASE = 'http://localhost:5000/api'
USERNAME = 'admin'
PASSWORD = 'password'

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic ' + base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()
}

def popular_dados_teste():
    print("🎯 Populando dados de teste...")
    
    # Dados de teste
    caixas_teste = [
        {
            "codigo": 1,
            "NBI": 1001,
            "NBF": 2001,
            "prateleira": "A",
            "bloco": "B",
            "andar": "1",
            "corredor": "C1"
        },
        {
            "codigo": 2, 
            "NBI": 1002,
            "NBF": 2002,
            "prateleira": "A",
            "bloco": "B", 
            "andar": "1",
            "corredor": "C2"
        }
    ]
    
    segurados_teste = [
        {
            "Nome": "João Silva",
            "cpf": 12345678901
        },
        {
            "Nome": "Maria Santos", 
            "cpf": 98765432109
        }
    ]
    
    arquivos_teste = [
        {
            "NB": 5001,
            "APS": "APS001",
            "SeguradoFK": 12345678901,
            "Tipo": 1,
            "Caixa_codigo": 1
        },
        {
            "NB": 5002,
            "APS": "APS002", 
            "SeguradoFK": 98765432109,
            "Tipo": 2,
            "Caixa_codigo": 2
        }
    ]
    
    # Popular caixas
    print("📦 Criando caixas...")
    for caixa in caixas_teste:
        try:
            response = requests.post(f"{API_BASE}/caixas", json=caixa, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   ✅ Caixa {caixa['codigo']} criada")
            else:
                print(f"   ❌ Erro na caixa {caixa['codigo']}: {response.text}")
        except Exception as e:
            print(f"   💥 Exception na caixa {caixa['codigo']}: {e}")
    
    # Popular segurados
    print("👤 Criando segurados...")
    for segurado in segurados_teste:
        try:
            response = requests.post(f"{API_BASE}/segurados", json=segurado, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   ✅ Segurado {segurado['cpf']} criado")
            else:
                print(f"   ❌ Erro no segurado {segurado['cpf']}: {response.text}")
        except Exception as e:
            print(f"   💥 Exception no segurado {segurado['cpf']}: {e}")
    
    # Popular arquivos
    print("📁 Criando arquivos...")
    for arquivo in arquivos_teste:
        try:
            response = requests.post(f"{API_BASE}/arquivos", json=arquivo, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   ✅ Arquivo {arquivo['NB']} criado")
            else:
                print(f"   ❌ Erro no arquivo {arquivo['NB']}: {response.text}")
        except Exception as e:
            print(f"   💥 Exception no arquivo {arquivo['NB']}: {e}")
    
    print("\n🎉 População de dados concluída!")

if __name__ == "__main__":
    popular_dados_teste()