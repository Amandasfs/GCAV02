# app/routes/arquivos.py
from flask import Blueprint, request, jsonify
from auth import requer_autenticacao
from database.mongo_handler import MongoDBHandler
from database.json_handler import JSONHandler
from models.arquivo import Arquivo

# Criar blueprint - IMPORTANTE: nome no plural
arquivos_bp = Blueprint('arquivos', __name__)

mongo_handler = MongoDBHandler()
json_handler = JSONHandler()

@arquivos_bp.route('/arquivos', methods=['POST'])
@requer_autenticacao
def criar_arquivo():
    try:
        data = request.get_json()
        arquivo = Arquivo(
            NB=data['NB'],
            APS=data['APS'],
            SeguradoFK=data['SeguradoFK'],
            Tipo=data['Tipo'],
            Caixa_codigo=data['Caixa_codigo']
        )
        
        mongo_handler.inserir_arquivo(arquivo.to_dict())
        json_handler.inserir_arquivo(arquivo.to_dict())
        
        return jsonify({"mensagem": "Arquivo criado com sucesso", "arquivo": arquivo.to_dict()}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@arquivos_bp.route('/arquivos', methods=['GET'])
@requer_autenticacao
def listar_arquivos():
    try:
        arquivos = mongo_handler.listar_arquivos()
        return jsonify(arquivos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@arquivos_bp.route('/arquivos/<int:NB>', methods=['GET'])
@requer_autenticacao
def buscar_arquivo(NB):
    try:
        arquivo = mongo_handler.buscar_arquivo(NB)
        if arquivo:
            return jsonify(arquivo), 200
        return jsonify({"erro": "Arquivo não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
