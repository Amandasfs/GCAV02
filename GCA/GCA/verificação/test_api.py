# test_api.py
import requests
import json
import base64

# Configurações
API_BASE = 'http://localhost:5000/api'
USERNAME = 'admin'
PASSWORD = 'password'

# Headers de autenticação
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic ' + base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()
}

def test_endpoints():
    print("🔍 Testando endpoints da API...")
    
    endpoints = [
        '/caixas',
        '/arquivos', 
        '/segurados',
        '/info',
        '/sync'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
            print(f"\n📊 {endpoint}: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   📦 Total: {len(data)} itens")
                    if data:
                        print(f"   📝 Primeiro item: {json.dumps(data[0], indent=2)}")
                elif isinstance(data, dict):
                    if 'total' in data:
                        print(f"   📦 Total: {data['total']}")
                    if 'arquivos' in data:
                        print(f"   📁 Arquivos: {len(data['arquivos'])}")
                        if data['arquivos']:
                            print(f"   📝 Primeiro arquivo: {json.dumps(data['arquivos'][0], indent=2)}")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")

if __name__ == "__main__":
    test_endpoints()