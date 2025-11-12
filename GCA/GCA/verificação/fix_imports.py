#!/usr/bin/env python3
import os
import shutil

def fix_imports():
    print("🔧 Corrigindo nomes de arquivos...")
    
    # Lista de correções necessárias
    corrections = [
        ('routes/arquivo.py', 'routes/arquivos.py'),
        ('routes/segurado.py', 'routes/segurados.py')
    ]
    
    for old_name, new_name in corrections:
        if os.path.exists(old_name) and not os.path.exists(new_name):
            shutil.move(old_name, new_name)
            print(f"✅ Renomeado: {old_name} -> {new_name}")
        elif os.path.exists(new_name):
            print(f"✅ Já existe: {new_name}")
        else:
            print(f"⚠️ Arquivo não encontrado: {old_name}")
    
    print("🎯 Correção de nomes concluída!")

if __name__ == "__main__":
    fix_imports()