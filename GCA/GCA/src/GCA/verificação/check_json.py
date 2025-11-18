#!/usr/bin/env python3
import json
import os
from datetime import datetime

def check_and_repair_json():
    file_path = "data/backup.json"
    
    print("🔍 Verificando arquivo JSON...")
    
    if not os.path.exists(file_path):
        print("❌ Arquivo JSON não existe")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            print("⚠️ Arquivo JSON está vazio")
            raise json.JSONDecodeError("Empty file", "", 0)
            
        data = json.loads(content)
        print("✅ JSON válido")
        print(f"📊 Conteúdo: {len(data.get('caixas', []))} caixas, "
              f"{len(data.get('arquivos', []))} arquivos, "
              f"{len(data.get('segurados', []))} segurados")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        print("🛠️ Reparando arquivo JSON...")
        
        # Recriar arquivo
        new_data = {
            "caixas": [],
            "arquivos": [],
            "segurados": [],
            "metadata": {
                "criado_em": datetime.now().isoformat(),
                "ultima_atualizacao": datetime.now().isoformat(),
                "total_caixas": 0,
                "total_arquivos": 0,
                "total_segurados": 0,
                "reparado_em": datetime.now().isoformat()
            }
        }
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        
        print("✅ JSON reparado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    if check_and_repair_json():
        print("🎯 JSON verificado/reparado com sucesso!")
    else:
        print("💥 Falha ao verificar/reparar JSON")