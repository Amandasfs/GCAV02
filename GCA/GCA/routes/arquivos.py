# routes/arquivos.py - VERSÃO SIMPLIFICADA
from flask import Blueprint, request, jsonify
from auth import requer_autenticacao
import json
import os
from datetime import datetime

arquivos_bp = Blueprint('arquivos', __name__)

class JSONHandler:
    def __init__(self, filename='data/backup.json'):
        self.filename = filename
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.filename):
            initial_data = {
                "caixas": [],
                "arquivos": [],
                "segurados": [],
                "metadata": {
                    "criado_em": datetime.now().isoformat(),
                    "ultima_atualizacao": datetime.now().isoformat(),
                    "total_caixas": 0,
                    "total_arquivos": 0,
                    "total_segurados": 0
                }
            }
            self.salvar_dados(initial_data)
    
    def ler_dados(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self._criar_estrutura_vazia()
    
    def salvar_dados(self, data):
        try:
            data["metadata"]["ultima_atualizacao"] = datetime.now().isoformat()
            data["metadata"]["total_caixas"] = len(data["caixas"])
            data["metadata"]["total_arquivos"] = len(data["arquivos"])
            data["metadata"]["total_segurados"] = len(data["segurados"])
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def _criar_estrutura_vazia(self):
        return {
            "caixas": [],
            "arquivos": [],
            "segurados": [],
            "metadata": {
                "criado_em": datetime.now().isoformat(),
                "ultima_atualizacao": datetime.now().isoformat(),
                "total_caixas": 0,
                "total_arquivos": 0,
                "total_segurados": 0
            }
        }
    
    def inserir_arquivo(self, arquivo_data):
        dados = self.ler_dados()
        
        # Verificar se NB já existe
        if any(a.get('NB') == arquivo_data.get('NB') for a in dados["arquivos"]):
            return False
        
        arquivo_data['criado_em'] = datetime.now().isoformat()
        dados["arquivos"].append(arquivo_data)
        
        return self.salvar_dados(dados)
    
    def listar_arquivos(self):
        dados = self.ler_dados()
        return dados["arquivos"]
    
    def buscar_arquivo(self, nb):
        dados = self.ler_dados()
        for arquivo in dados["arquivos"]:
            if arquivo.get('NB') == nb:
                return arquivo
        return None

json_handler = JSONHandler()

@arquivos_bp.route('/arquivos', methods=['POST'])
@requer_autenticacao
def criar_arquivo():
    try:
        data = request.get_json()
        print(f"📝 Dados recebidos: {data}")  # DEBUG
        
        # Validação básica
        campos_obrigatorios = ['NB', 'APS', 'SeguradoFK', 'Tipo', 'Caixa_codigo']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({"erro": f"Campo obrigatório faltando: {campo}"}), 400
        
        # Inserir no JSON
        sucesso = json_handler.inserir_arquivo(data)
        
        if sucesso:
            return jsonify({
                "mensagem": "Arquivo criado com sucesso", 
                "arquivo": data
            }), 201
        else:
            return jsonify({"erro": "NB já existe"}), 400
            
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")  # DEBUG
        return jsonify({"erro": str(e)}), 500

@arquivos_bp.route('/arquivos', methods=['GET'])
@requer_autenticacao
def listar_arquivos():
    try:
        arquivos = json_handler.listar_arquivos()
        print(f"📁 Arquivos encontrados: {len(arquivos)}")  # DEBUG
        
        # RETORNAR COMO LISTA SIMPLES para compatibilidade
        return jsonify(arquivos), 200
        
    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {e}")  # DEBUG
        return jsonify({"erro": str(e)}), 500

@arquivos_bp.route('/arquivos/<int:nb>', methods=['GET'])
@requer_autenticacao
def buscar_arquivo(nb):
    try:
        arquivo = json_handler.buscar_arquivo(nb)
        if arquivo:
            return jsonify(arquivo), 200
        return jsonify({"erro": "Arquivo não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Nota: Removemos PUT e DELETE para simplificar por enquanto