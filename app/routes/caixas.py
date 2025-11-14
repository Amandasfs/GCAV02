# app/routes/caixas.py
from flask import Blueprint, request, jsonify
from auth import requer_autenticacao
from database.mongo_handler import MongoDBHandler
from database.json_handler import JSONHandler
from models.caixa import Caixa

caixas_bp = Blueprint('caixas', __name__)
mongo_handler = MongoDBHandler()
json_handler = JSONHandler()

@caixas_bp.route('/caixas', methods=['POST'])
@requer_autenticacao
def criar_caixa():
    try:
        data = request.get_json()
        caixa = Caixa(
            codigo=data['codigo'],
            NBI=data['NBI'],
            NBF=data['NBF'],
            prateleira=data['prateleira'],
            bloco=data['bloco'],
            andar=data['andar'],
            corredor=data['corredor']
        )
        
        # Salvar em ambos MongoDB e JSON
        mongo_handler.inserir_caixa(caixa.to_dict())
        json_handler.inserir_caixa(caixa.to_dict())
        
        return jsonify({"mensagem": "Caixa criada com sucesso", "caixa": caixa.to_dict()}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@caixas_bp.route('/caixas', methods=['GET'])
@requer_autenticacao
def listar_caixas():
    try:
        caixas = mongo_handler.listar_caixas()
        return jsonify(caixas), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@caixas_bp.route('/caixas/<int:codigo>', methods=['GET'])
@requer_autenticacao
def buscar_caixa(codigo):
    try:
        caixa = mongo_handler.buscar_caixa(codigo)
        if caixa:
            return jsonify(caixa), 200
        return jsonify({"erro": "Caixa não encontrada"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@caixas_bp.route('/caixas/<int:codigo>', methods=['PUT'])
@requer_autenticacao
def atualizar_caixa(codigo):
    try:
        data = request.get_json()
        atualizacao = {k: v for k, v in data.items() if k != 'codigo'}
        
        resultado_mongo = mongo_handler.atualizar_caixa(codigo, atualizacao)
        resultado_json = json_handler.atualizar_caixa(codigo, atualizacao)
        
        if resultado_mongo.modified_count > 0 or resultado_json:
            return jsonify({"mensagem": "Caixa atualizada com sucesso"}), 200
        return jsonify({"erro": "Caixa não encontrada"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500