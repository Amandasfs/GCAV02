from flask import Blueprint, request, jsonify
from auth import requer_autenticacao
from database.mongo_handler import MongoDBHandler
from database.json_handler import JSONHandler
from models.segurado import Segurado

# Criar blueprint - IMPORTANTE: nome no plural
segurados_bp = Blueprint('segurados', __name__)

mongo_handler = MongoDBHandler()
json_handler = JSONHandler()

@segurados_bp.route('/segurados', methods=['POST'])
@requer_autenticacao
def criar_segurado():
    try:
        data = request.get_json()
        segurado = Segurado(
            Nome=data['Nome'],
            cpf=data['cpf']
        )
        
        mongo_handler.inserir_segurado(segurado.to_dict())
        json_handler.inserir_segurado(segurado.to_dict())
        
        return jsonify({"mensagem": "Segurado criado com sucesso", "segurado": segurado.to_dict()}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@segurados_bp.route('/segurados', methods=['GET'])
@requer_autenticacao
def listar_segurados():
    try:
        segurados = mongo_handler.listar_segurados()
        return jsonify(segurados), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@segurados_bp.route('/segurados/<int:cpf>', methods=['GET'])
@requer_autenticacao
def buscar_segurado(cpf):
    try:
        segurado = mongo_handler.buscar_segurado(cpf)
        if segurado:
            return jsonify(segurado), 200
        return jsonify({"erro": "Segurado não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@segurados_bp.route('/segurados/<int:cpf>', methods=['PUT'])
@requer_autenticacao
def atualizar_segurado(cpf):
    try:
        data = request.get_json()
        atualizacao = {k: v for k, v in data.items() if k != 'cpf'}
        
        resultado_mongo = mongo_handler.atualizar_segurado(cpf, atualizacao)
        resultado_json = json_handler.atualizar_segurado(cpf, atualizacao)
        
        if resultado_mongo.modified_count > 0 or resultado_json:
            return jsonify({"mensagem": "Segurado atualizado com sucesso"}), 200
        return jsonify({"erro": "Segurado não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
