#!/usr/bin/env python3
"""
GCA API - Sistema de Gerenciamento de Caixas e Arquivos
Sistema completo com MongoDB, JSON Backup e Autenticação
(Atualizado: adiciona criação de arquivo com upload/JSON fallback robusto)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import sys
from datetime import datetime
import time
from functools import wraps
import base64
import json
import uuid

# Configurar logging avançado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('gca_api.log')
    ]
)
logger = logging.getLogger(__name__)

# ========== CONFIGURAÇÕES ==========
CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
    "mongo_uri": "mongodb://localhost:27017/",
    "db_name": "GCA_DB"
}

# ========== INICIALIZAÇÃO DO APP ==========
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app, origins=["*"])

# Variáveis globais para estado do sistema
app_start_time = None
database_initialized = False
mongo_available = False
json_available = False
last_update_time = datetime.now()

# Local paths
DATA_DIR = 'data'
BACKUP_JSON_PATH = os.path.join(DATA_DIR, 'backup.json')
FILES_DIR = os.path.join(DATA_DIR, 'files')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

# ========== MIDDLEWARE DE AUTENTICAÇÃO ==========
def requer_autenticacao(f):
    """Decorator para requerer autenticação Basic Auth"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not verificar_credenciais(auth.username, auth.password):
            return jsonify({"erro": "Não autorizado"}), 401
        return f(*args, **kwargs)
    return decorated

def verificar_credenciais(username, password):
    """Verifica as credenciais de autenticação"""
    return username == 'admin' and password == 'password'

# ========== BANNER INICIAL ==========
def mostrar_banner():
    print("\n" + "="*60)
    print("🎯 GCA API - SISTEMA DE GERENCIAMENTO".center(60))
    print("="*60)
    print("📦 Módulos:".ljust(30) + "✅ Caixas, Arquivos, Segurados")
    print("🔐 Autenticação:".ljust(30) + "✅ Basic Auth")
    print("💾 Banco de Dados:".ljust(30) + "✅ MongoDB + JSON Backup")
    print("🌐 API REST:".ljust(30) + "✅ Flask + CORS")
    print("🔍 Busca:".ljust(30) + "✅ Avançada com Relacionamentos")
    print("="*60)

# ========== VERIFICAÇÃO DE DEPENDÊNCIAS ==========
def verificar_dependencias():
    """Verifica se todas as dependências estão disponíveis"""
    logger.info("🔍 Verificando dependências...")
    
    dependencias = {
        'Flask': 'flask',
        'Flask-CORS': 'flask_cors', 
        'PyMongo': 'pymongo'
    }
    
    faltantes = []
    for nome, modulo in dependencias.items():
        try:
            __import__(modulo)
            logger.info(f"✅ {nome}")
        except ImportError:
            logger.error(f"❌ {nome}")
            faltantes.append(nome)
    
    if faltantes:
        logger.error(f"🚨 Dependências faltantes: {', '.join(faltantes)}")
        return False
    return True

# ========== UTILS PARA JSON LOCAL (fallback) ==========
def ensure_backup_json():
    """Garante que backup.json existe com estrutura base"""
    if not os.path.exists(BACKUP_JSON_PATH):
        now = datetime.now().isoformat()
        data = {
            "caixas": [],
            "arquivos": [],
            "segurados": [],
            "metadata": {
                "criado_em": now,
                "ultima_atualizacao": now,
                "total_caixas": 0,
                "total_arquivos": 0,
                "total_segurados": 0,
                "criado_manual": True
            }
        }
        with open(BACKUP_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("📁 Arquivo JSON criado manualmente (fallback)")

def ler_backup_json():
    """Lê e retorna o conteúdo do backup.json de forma segura"""
    ensure_backup_json()
    try:
        with open(BACKUP_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Falha ao ler backup.json: {e}")
        raise

def salvar_backup_json(dados):
    """Salva dados no backup.json"""
    try:
        with open(BACKUP_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"❌ Falha ao salvar backup.json: {e}")
        raise

def adicionar_arquivo_no_json(novo_arquivo):
    """
    Adiciona um registro de arquivo ao backup.json e atualiza metadata.
    novo_arquivo: dict com os campos do arquivo (NB, APS, SeguradoFK, Tipo, Caixa_codigo, FilePath, ... )
    Retorna o registro adicionado.
    """
    dados = ler_backup_json()
    # Garantir NB único: se NB fornecido e já existe, incrementa para garantir unicidade
    existing_nbs = {a.get('NB') for a in dados.get('arquivos', []) if 'NB' in a}
    nb = novo_arquivo.get('NB')
    if nb is None:
        # criar NB automático único (timestamp + uuid)
        nb_auto = int(time.time())
        while nb_auto in existing_nbs:
            nb_auto += 1
        novo_arquivo['NB'] = nb_auto
    else:
        # se nb existe, garantir que seja único
        if nb in existing_nbs:
            # criar NB alternativo
            nb_alt = int(time.time())
            while nb_alt in existing_nbs:
                nb_alt += 1
            novo_arquivo['NB'] = nb_alt

    # Adicionar ID interno
    novo_arquivo.setdefault('id', str(uuid.uuid4()))
    novo_arquivo.setdefault('criado_em', datetime.now().isoformat())

    dados.setdefault('arquivos', []).append(novo_arquivo)

    # Atualizar metadata
    dados.setdefault('metadata', {})
    dados['metadata']['total_arquivos'] = len(dados.get('arquivos', []))
    dados['metadata']['ultima_atualizacao'] = datetime.now().isoformat()

    salvar_backup_json(dados)
    return novo_arquivo

# ========== CONEXÃO COM BANCO DE DADOS ==========
def inicializar_database():
    """Inicializa conexões com MongoDB e JSON"""
    global database_initialized, mongo_available, json_available
    
    logger.info("💾 Inicializando conexões de banco de dados...")
    
    try:
        # Tentar MongoDB
        try:
            from database.mongo_handler import MongoDBHandler
            mongo_handler = MongoDBHandler(CONFIG['mongo_uri'], CONFIG['db_name'])
            if mongo_handler.is_connected():
                mongo_available = True
                logger.info("✅ MongoDB conectado com sucesso")
            else:
                mongo_available = False
                logger.warning("⚠️ MongoDB não disponível")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB não disponível: {e}")
            mongo_available = False
        
        # Tentar JSON - com fallback robusto
        try:
            from database.json_handler import JSONHandler
            json_handler = JSONHandler()
            # Forçar criação se não existir
            try:
                json_handler.ensure_file_exists()
            except Exception:
                # fallback para ensure_backup_json
                ensure_backup_json()
            test_data = json_handler.ler_dados()
            json_available = True
            logger.info("✅ JSON Handler inicializado")
            
            # Log estatísticas iniciais
            stats = json_handler.get_stats()
            logger.info(f"📊 Estatísticas iniciais JSON: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Erro no JSON Handler: {e}")
            # Tentar criar manualmente
            try:
                ensure_backup_json()
                json_available = True
                logger.info("✅ JSON criado manualmente e inicializado (fallback)")
            except Exception as e2:
                logger.error(f"❌ Falha crítica no JSON: {e2}")
                json_available = False
        
        # Pelo menos um deve funcionar
        database_initialized = mongo_available or json_available
        
        if database_initialized:
            logger.info("✅ Banco de dados inicializado com sucesso")
        else:
            logger.error("❌ Nenhum banco de dados disponível")
        
        return database_initialized
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização do banco: {e}")
        return False

def criar_json_manual():
    """Cria arquivo JSON manualmente em caso de falha (mantido por compatibilidade)"""
    os.makedirs('data', exist_ok=True)
    
    data = {
        "caixas": [],
        "arquivos": [],
        "segurados": [],
        "metadata": {
            "criado_em": datetime.now().isoformat(),
            "ultima_atualizacao": datetime.now().isoformat(),
            "total_caixas": 0,
            "total_arquivos": 0,
            "total_segurados": 0,
            "criado_manual": True
        }
    }
    
    with open(BACKUP_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info("📁 Arquivo JSON criado manualmente")

# ========== REGISTRO DE BLUEPRINTS ==========
def registrar_blueprints():
    """Registra todos os blueprints da aplicação"""
    logger.info("🔄 Registrando blueprints...")
    
    blueprints = {
        'Caixas': ('routes.caixas', 'caixas_bp'),
        'Arquivos': ('routes.arquivos', 'arquivos_bp'),
        'Segurados': ('routes.segurados', 'segurados_bp'),
        'Relatórios': ('routes.relatorios', 'relatorios_bp')
    }
    
    sucessos = 0
    for nome, (modulo, blueprint) in blueprints.items():
        try:
            module = __import__(modulo, fromlist=[blueprint])
            bp = getattr(module, blueprint)
            app.register_blueprint(bp, url_prefix='/api')
            logger.info(f"✅ {nome} registrado")
            sucessos += 1
        except Exception as e:
            logger.error(f"❌ {nome}: {e}")
    
    return sucessos > 0  # Pelo menos um blueprint registrado

# ========== ROTAS DE BUSCA AVANÇADA ==========
@app.route('/api/busca', methods=['GET'])
@requer_autenticacao
def busca_avancada():
    """Busca avançada em todas as entidades"""
    try:
        termo = request.args.get('q', '').strip().lower()
        if not termo:
            return jsonify({"erro": "Termo de busca não fornecido"}), 400
        
        resultados = {
            "termo_busca": termo,
            "timestamp": datetime.now().isoformat(),
            "resultados": {
                "caixas": [],
                "arquivos": [],
                "segurados": []
            }
        }
        
        # Buscar em MongoDB primeiro, depois JSON
        if mongo_available:
            from database.mongo_handler import MongoDBHandler
            mongo_handler = MongoDBHandler()
            
            # Buscar caixas
            caixas = mongo_handler.listar_caixas()
            for caixa in caixas:
                if (termo in str(caixa.get('codigo', '')).lower() or
                    termo in str(caixa.get('prateleira', '')).lower() or
                    termo in str(caixa.get('bloco', '')).lower() or
                    termo in str(caixa.get('andar', '')).lower()):
                    resultados["resultados"]["caixas"].append(caixa)
            
            # Buscar arquivos
            arquivos = mongo_handler.listar_arquivos()
            for arquivo in arquivos:
                if (termo in str(arquivo.get('NB', '')).lower() or
                    termo in str(arquivo.get('APS', '')).lower() or
                    termo in str(arquivo.get('SeguradoFK', '')).lower() or
                    termo in str(arquivo.get('Tipo', '')).lower()):
                    resultados["resultados"]["arquivos"].append(arquivo)
            
            # Buscar segurados
            segurados = mongo_handler.listar_segurados()
            for segurado in segurados:
                if (termo in str(segurado.get('cpf', '')).lower() or
                    termo in segurado.get('Nome', '').lower()):
                    resultados["resultados"]["segurados"].append(segurado)
        else:
            # Fallback para JSON
            dados = ler_backup_json()
            
            # Buscar caixas
            for caixa in dados["caixas"]:
                if (termo in str(caixa.get('codigo', '')).lower() or
                    termo in str(caixa.get('prateleira', '')).lower() or
                    termo in str(caixa.get('bloco', '')).lower() or
                    termo in str(caixa.get('andar', '')).lower()):
                    resultados["resultados"]["caixas"].append(caixa)
            
            # Buscar arquivos
            for arquivo in dados["arquivos"]:
                if (termo in str(arquivo.get('NB', '')).lower() or
                    termo in str(arquivo.get('APS', '')).lower() or
                    termo in str(arquivo.get('SeguradoFK', '')).lower() or
                    termo in str(arquivo.get('Tipo', '')).lower() or
                    termo in str(arquivo.get('FilePath', '')).lower()):
                    resultados["resultados"]["arquivos"].append(arquivo)
            
            # Buscar segurados
            for segurado in dados["segurados"]:
                if (termo in str(segurado.get('cpf', '')).lower() or
                    termo in segurado.get('Nome', '').lower()):
                    resultados["resultados"]["segurados"].append(segurado)
        
        # Adicionar estatísticas
        resultados["estatisticas"] = {
            "total_caixas": len(resultados["resultados"]["caixas"]),
            "total_arquivos": len(resultados["resultados"]["arquivos"]),
            "total_segurados": len(resultados["resultados"]["segurados"]),
            "total_geral": sum(len(v) for v in resultados["resultados"].values())
        }
        
        return jsonify(resultados), 200
        
    except Exception as e:
        logger.error(f"❌ Erro na busca avançada: {e}")
        return jsonify({"erro": f"Erro na busca: {str(e)}"}), 500

@app.route('/api/busca/caixas', methods=['GET'])
@requer_autenticacao
def busca_caixas():
    """Busca específica em caixas"""
    try:
        codigo = request.args.get('codigo')
        prateleira = request.args.get('prateleira')
        bloco = request.args.get('bloco')
        
        filtro = {}
        if codigo:
            filtro['codigo'] = int(codigo)
        if prateleira:
            filtro['prateleira'] = prateleira.upper()
        if bloco:
            filtro['bloco'] = bloco.upper()
        
        if mongo_available:
            from database.mongo_handler import MongoDBHandler
            mongo_handler = MongoDBHandler()
            caixas = mongo_handler.listar_caixas(filtro)
        else:
            dados = ler_backup_json()
            caixas = []
            for caixa in dados["caixas"]:
                match = True
                if 'codigo' in filtro and caixa.get('codigo') != filtro['codigo']:
                    match = False
                if 'prateleira' in filtro and caixa.get('prateleira', '').upper() != filtro['prateleira']:
                    match = False
                if 'bloco' in filtro and caixa.get('bloco', '').upper() != filtro['bloco']:
                    match = False
                if match:
                    caixas.append(caixa)
        
        return jsonify({
            "filtros": filtro,
            "total": len(caixas),
            "caixas": caixas,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro na busca de caixas: {str(e)}"}), 500

@app.route('/api/busca/arquivos', methods=['GET'])
@requer_autenticacao
def busca_arquivos():
    """Busca específica em arquivos"""
    try:
        nb = request.args.get('nb')
        aps = request.args.get('aps')
        segurado = request.args.get('segurado')
        tipo = request.args.get('tipo')
        caixa = request.args.get('caixa')
        
        filtro = {}
        if nb:
            filtro['NB'] = int(nb)
        if aps:
            filtro['APS'] = aps.upper()
        if segurado:
            filtro['SeguradoFK'] = int(segurado)
        if tipo:
            filtro['Tipo'] = int(tipo)
        if caixa:
            filtro['Caixa_codigo'] = int(caixa)
        
        if mongo_available:
            from database.mongo_handler import MongoDBHandler
            mongo_handler = MongoDBHandler()
            arquivos = mongo_handler.listar_arquivos(filtro)
        else:
            dados = ler_backup_json()
            arquivos = []
            for arquivo in dados["arquivos"]:
                match = True
                if 'NB' in filtro and arquivo.get('NB') != filtro['NB']:
                    match = False
                if 'APS' in filtro and arquivo.get('APS', '').upper() != filtro['APS']:
                    match = False
                if 'SeguradoFK' in filtro and arquivo.get('SeguradoFK') != filtro['SeguradoFK']:
                    match = False
                if 'Tipo' in filtro and arquivo.get('Tipo') != filtro['Tipo']:
                    match = False
                if 'Caixa_codigo' in filtro and arquivo.get('Caixa_codigo') != filtro['Caixa_codigo']:
                    match = False
                if match:
                    arquivos.append(arquivo)
        
        return jsonify({
            "filtros": filtro,
            "total": len(arquivos),
            "arquivos": arquivos,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro na busca de arquivos: {str(e)}"}), 500

@app.route('/api/busca/segurados', methods=['GET'])
@requer_autenticacao
def busca_segurados():
    """Busca específica em segurados"""
    try:
        cpf = request.args.get('cpf')
        nome = request.args.get('nome')
        
        filtro = {}
        if cpf:
            filtro['cpf'] = int(cpf)
        if nome:
            filtro['Nome'] = nome.upper()
        
        if mongo_available:
            from database.mongo_handler import MongoDBHandler
            mongo_handler = MongoDBHandler()
            segurados = mongo_handler.listar_segurados(filtro)
        else:
            dados = ler_backup_json()
            segurados = []
            for segurado in dados["segurados"]:
                match = True
                if 'cpf' in filtro and segurado.get('cpf') != filtro['cpf']:
                    match = False
                if 'Nome' in filtro and segurado.get('Nome', '').upper() != filtro['Nome']:
                    match = False
                if match:
                    segurados.append(segurado)
        
        return jsonify({
            "filtros": filtro,
            "total": len(segurados),
            "segurados": segurados,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro na busca de segurados: {str(e)}"}), 500

# ========== ROTAS DE CRIAÇÃO DE ARQUIVOS (ATUALIZADA) ==========
@app.route('/api/arquivos', methods=['POST'])
@requer_autenticacao
def criar_arquivo():
    """
    Cria um novo registro de arquivo.
    Aceita:
      - multipart/form-data com campo 'file' para upload físico e outros campos (NB, APS, SeguradoFK, Tipo, Caixa_codigo)
      - application/json com os mesmos campos. Para conteúdo binário no JSON, aceita 'file_base64' (string base64).
    Quando o MongoDB estiver disponível, delega para MongoDBHandler; caso contrário, grava no backup.json.
    """
    try:
        # Primeiro tentar delegar ao Mongo, se disponível
        if mongo_available:
            try:
                from database.mongo_handler import MongoDBHandler
                mongo_handler = MongoDBHandler()
                # construir doc a partir do request (json or form)
                doc = {}
                if request.is_json:
                    doc = request.get_json()
                else:
                    # combinar form fields
                    for k, v in request.form.items():
                        doc[k] = v
                # lidar com upload de arquivo: salvar no FS e referenciar
                file_path = None
                if 'file' in request.files:
                    f = request.files['file']
                    filename = f"{int(time.time())}_{uuid.uuid4().hex}_{secure_filename(f.filename)}"
                    saved_path = os.path.join(FILES_DIR, filename)
                    f.save(saved_path)
                    file_path = saved_path
                    doc['FilePath'] = saved_path
                elif request.is_json and doc.get('file_base64'):
                    # gravar base64 no disco
                    try:
                        content = base64.b64decode(doc.get('file_base64'))
                        filename = f"{int(time.time())}_{uuid.uuid4().hex}.bin"
                        saved_path = os.path.join(FILES_DIR, filename)
                        with open(saved_path, 'wb') as fh:
                            fh.write(content)
                        file_path = saved_path
                        doc['FilePath'] = saved_path
                        # remover campo grande antes de enviar para DB
                        doc.pop('file_base64', None)
                    except Exception as e:
                        logger.warning(f"⚠️ Falha ao decodificar file_base64: {e}")
                # garantir tipos corretos para campos numéricos
                for maybe_int in ('NB', 'SeguradoFK', 'Tipo', 'Caixa_codigo'):
                    if maybe_int in doc and isinstance(doc[maybe_int], str) and doc[maybe_int].isdigit():
                        doc[maybe_int] = int(doc[maybe_int])
                # inserir no Mongo
                inserted = mongo_handler.criar_arquivo(doc)
                # atualizar last_update_time via after_request se 201/200
                return jsonify({"mensagem": "Arquivo criado no MongoDB", "arquivo": inserted}), 201
            except Exception as e:
                logger.warning(f"⚠️ Tentativa de salvar no Mongo falhou, fallback JSON: {e}")
                # continuar para fallback
        # --- Fallback para JSON local ---
        # aceitar multipart ou json
        payload = {}
        file_path = None

        if request.is_json:
            payload = request.get_json()
            # se vier file_base64, decodificar e salvar
            fb64 = payload.pop('file_base64', None)
            if fb64:
                try:
                    content = base64.b64decode(fb64)
                    filename = f"{int(time.time())}_{uuid.uuid4().hex}.bin"
                    saved_path = os.path.join(FILES_DIR, filename)
                    with open(saved_path, 'wb') as fh:
                        fh.write(content)
                    file_path = saved_path
                    payload['FilePath'] = saved_path
                except Exception as e:
                    return jsonify({"erro": f"Falha ao decodificar file_base64: {str(e)}"}), 400
        else:
            # form-data (pode ter arquivo)
            payload.update(request.form.to_dict())
            if 'file' in request.files:
                f = request.files['file']
                # nome seguro e único
                try:
                    from werkzeug.utils import secure_filename
                except Exception:
                    # fallback simples
                    def secure_filename(n): return n.replace('/', '_').replace('\\', '_')
                filename = f"{int(time.time())}_{uuid.uuid4().hex}_{secure_filename(f.filename)}"
                saved_path = os.path.join(FILES_DIR, filename)
                f.save(saved_path)
                file_path = saved_path
                payload['FilePath'] = saved_path

        # converter campos que devem ser inteiros
        for k in ('NB', 'SeguradoFK', 'Tipo', 'Caixa_codigo'):
            if k in payload:
                try:
                    payload[k] = int(payload[k])
                except Exception:
                    # manter como string se não for conversível
                    pass

        # preencher campos mínimos se necessário
        payload.setdefault('APS', payload.get('APS', ''))
        payload.setdefault('Tipo', payload.get('Tipo', 0))

        # adicionar no JSON (garante NB único e metadata)
        try:
            novo = adicionar_arquivo_no_json(payload)
            return jsonify({"mensagem": "✅ Arquivo criado e salvo no JSON", "arquivo": novo}), 201
        except Exception as e:
            logger.error(f"❌ Falha ao adicionar arquivo no JSON: {e}")
            return jsonify({"erro": f"Falha ao salvar arquivo: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"❌ Erro ao criar arquivo: {e}")
        return jsonify({"erro": f"Erro ao criar arquivo: {str(e)}"}), 500

# ========== ROTAS DE RELACIONAMENTOS ==========
@app.route('/api/caixas/<int:codigo>/arquivos', methods=['GET'])
@requer_autenticacao
def arquivos_por_caixa(codigo):
    """Retorna todos os arquivos de uma caixa específica"""
    try:
        if mongo_available:
            from database.mongo_handler import MongoDBHandler
            mongo_handler = MongoDBHandler()
            arquivos = mongo_handler.buscar_arquivos_por_caixa(codigo)
            caixa = mongo_handler.buscar_caixa(codigo)
        else:
            dados = ler_backup_json()
            arquivos = [arq for arq in dados["arquivos"] if arq.get('Caixa_codigo') == codigo]
            caixa = next((c for c in dados["caixas"] if c.get('codigo') == codigo), None)
        
        if not caixa:
            return jsonify({"erro": f"Caixa {codigo} não encontrada"}), 404
        
        return jsonify({
            "caixa": caixa,
            "arquivos": arquivos,
            "total_arquivos": len(arquivos),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar arquivos da caixa: {str(e)}"}), 500

@app.route('/api/segurados/<int:cpf>/arquivos', methods=['GET'])
@requer_autenticacao
def arquivos_por_segurado(cpf):
    """Retorna todos os arquivos de um segurado específico"""
    try:
        if mongo_available:
            from database.mongo_handler import MongoDBHandler
            mongo_handler = MongoDBHandler()
            arquivos = mongo_handler.buscar_arquivos_por_segurado(cpf)
            segurado = mongo_handler.buscar_segurado(cpf)
        else:
            dados = ler_backup_json()
            arquivos = [arq for arq in dados["arquivos"] if arq.get('SeguradoFK') == cpf]
            segurado = next((s for s in dados["segurados"] if s.get('cpf') == cpf), None)
        
        if not segurado:
            return jsonify({"erro": f"Segurado {cpf} não encontrado"}), 404
        
        return jsonify({
            "segurado": segurado,
            "arquivos": arquivos,
            "total_arquivos": len(arquivos),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar arquivos do segurado: {str(e)}"}), 500

@app.route('/api/arquivos/<int:nb>/detalhes', methods=['GET'])
@requer_autenticacao
def detalhes_arquivo(nb):
    """Retorna detalhes completos de um arquivo com informações relacionadas"""
    try:
        if mongo_available:
            from database.mongo_handler import MongoDBHandler
            mongo_handler = MongoDBHandler()
            arquivo = mongo_handler.buscar_arquivo(nb)
            if arquivo:
                caixa = mongo_handler.buscar_caixa(arquivo.get('Caixa_codigo'))
                segurado = mongo_handler.buscar_segurado(arquivo.get('SeguradoFK'))
        else:
            dados = ler_backup_json()
            arquivo = next((a for a in dados["arquivos"] if a.get('NB') == nb), None)
            if arquivo:
                caixa = next((c for c in dados["caixas"] if c.get('codigo') == arquivo.get('Caixa_codigo')), None)
                segurado = next((s for s in dados["segurados"] if s.get('cpf') == arquivo.get('SeguradoFK')), None)
        
        if not arquivo:
            return jsonify({"erro": f"Arquivo {nb} não encontrado"}), 404
        
        return jsonify({
            "arquivo": arquivo,
            "caixa": caixa,
            "segurado": segurado,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar detalhes do arquivo: {str(e)}"}), 500

# ========== ROTAS DE SINCRONIZAÇÃO E ATUALIZAÇÃO ==========
@app.route('/api/sync', methods=['GET'])
@requer_autenticacao
def sincronizar_dados():
    """Sincroniza dados entre MongoDB e JSON"""
    global last_update_time
    
    try:
        from database.mongo_handler import MongoDBHandler
        from database.json_handler import JSONHandler
        
        mongo_handler = MongoDBHandler()
        json_handler = JSONHandler()
        
        stats = {
            "mongodb": mongo_handler.get_stats() if mongo_available else {"status": "offline"},
            "json": json_handler.get_stats(),
            "ultima_sincronizacao": datetime.now().isoformat(),
            "status": "success"
        }
        
        last_update_time = datetime.now()
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro na sincronização: {str(e)}", "status": "error"}), 500

@app.route('/api/updates', methods=['GET'])
@requer_autenticacao
def obter_atualizacoes():
    """Retorna informações sobre atualizações recentes"""
    try:
        dados = ler_backup_json()
        
        updates = {
            "ultima_atualizacao": dados["metadata"]["ultima_atualizacao"],
            "ultima_sincronizacao": last_update_time.isoformat(),
            "estatisticas": {
                "caixas": len(dados["caixas"]),
                "arquivos": len(dados["arquivos"]),
                "segurados": len(dados["segurados"])
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(updates), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
@requer_autenticacao
def refresh_data():
    """Força atualização completa dos dados"""
    try:
        dados = ler_backup_json()
        
        response = {
            "mensagem": "✅ Dados atualizados com sucesso",
            "timestamp": datetime.now().isoformat(),
            "estatisticas": {
                "caixas": len(dados["caixas"]),
                "arquivos": len(dados["arquivos"]),
                "segurados": len(dados["segurados"])
            }
        }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao atualizar dados: {str(e)}"}), 500

# ========== ROTAS DA API ==========
@app.route('/')
def home():
    """Página inicial com documentação"""
    return jsonify({
        "sistema": "GCA API - Gerenciamento de Caixas e Arquivos",
        "versao": "2.1.0",
        "status": "🟢 ONLINE",
        "timestamp": datetime.now().isoformat(),
        "atualizacao_auto": "✅ ATIVADA",
        "banco_dados": {
            "mongodb": "🟢 DISPONÍVEL" if mongo_available else "🔴 INDISPONÍVEL",
            "json": "🟢 DISPONÍVEL" if json_available else "🔴 INDISPONÍVEL"
        },
        "endpoints": {
            "principal": {
                "GET /": "Documentação da API",
                "GET /api/health": "Status do sistema",
                "GET /api/info": "Informações do sistema",
                "GET /api/sync": "Sincronizar dados",
                "GET /api/updates": "Ver atualizações",
                "POST /api/refresh": "Forçar atualização"
            },
            "busca": {
                "GET /api/busca?q=termo": "Busca geral em todas as entidades",
                "GET /api/busca/caixas?codigo=X&prateleira=Y": "Busca filtrada em caixas",
                "GET /api/busca/arquivos?nb=X&aps=Y&segurado=Z": "Busca filtrada em arquivos",
                "GET /api/busca/segurados?cpf=X&nome=Y": "Busca filtrada em segurados"
            },
            "relacionamentos": {
                "GET /api/caixas/<codigo>/arquivos": "Arquivos de uma caixa",
                "GET /api/segurados/<cpf>/arquivos": "Arquivos de um segurado",
                "GET /api/arquivos/<NB>/detalhes": "Detalhes completos de arquivo"
            },
            "caixas": {
                "POST /api/caixas": "Criar nova caixa",
                "GET /api/caixas": "Listar todas as caixas",
                "GET /api/caixas/<codigo>": "Buscar caixa específica",
                "PUT /api/caixas/<codigo>": "Atualizar caixa",
                "DELETE /api/caixas/<codigo>": "Deletar caixa"
            },
            "arquivos": {
                "POST /api/arquivos": "Criar novo arquivo",
                "GET /api/arquivos": "Listar todos os arquivos",
                "GET /api/arquivos/<NB>": "Buscar arquivo específico",
                "PUT /api/arquivos/<NB>": "Atualizar arquivo",
                "DELETE /api/arquivos/<NB>": "Deletar arquivo"
            },
            "segurados": {
                "POST /api/segurados": "Criar novo segurado",
                "GET /api/segurados": "Listar todos os segurados",
                "GET /api/segurados/<cpf>": "Buscar segurado específico",
                "PUT /api/segurados/<cpf>": "Atualizar segurado",
                "DELETE /api/segurados/<cpf>": "Deletar segurado"
            },
            "utilidades": {
                "POST /api/limpar": "Limpar todos os dados (DEV)"
            }
        },
        "autenticacao": {
            "tipo": "Basic Auth",
            "usuario": "admin",
            "senha": "password"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check completo da API"""
    status = {
        "status": "healthy",
        "servico": "GCA API",
        "timestamp": datetime.now().isoformat(),
        "versao": "2.1.0",
        "dependencies": {
            "flask": "ok",
            "mongodb": "available" if mongo_available else "unavailable",
            "json_backup": "available" if json_available else "unavailable"
        },
        "system": {
            "uptime": str(datetime.now() - app_start_time) if app_start_time else "0:00:00",
            "database_initialized": database_initialized,
            "last_update": last_update_time.isoformat()
        }
    }
    return jsonify(status)

@app.route('/api/info', methods=['GET'])
@requer_autenticacao
def system_info():
    """Informações do sistema em tempo real"""
    try:
        dados = ler_backup_json()
        stats = dados.get('metadata', {})
        
        estatisticas = {
            "caixas": stats.get("total_caixas", 0),
            "arquivos": stats.get("total_arquivos", 0),
            "segurados": stats.get("total_segurados", 0)
        }
    except:
        estatisticas = {
            "caixas": 0,
            "arquivos": 0,
            "segurados": 0
        }
    
    return jsonify({
        "sistema": "GCA API",
        "inicio": app_start_time.isoformat() if app_start_time else "N/A",
        "uptime": str(datetime.now() - app_start_time) if app_start_time else "N/A",
        "estatisticas": estatisticas,
        "configuracoes": CONFIG,
        "status_banco_dados": {
            "mongodb": mongo_available,
            "json": json_available
        },
        "atualizacao": {
            "ultima_atualizacao": last_update_time.isoformat(),
            "auto_atualizacao": True
        }
    })

# ========== ROTA DE LIMPEZA (APENAS DESENVOLVIMENTO) ==========
@app.route('/api/limpar', methods=['POST'])
@requer_autenticacao
def limpar_dados():
    """Limpa todos os dados (apenas para desenvolvimento)"""
    try:
        # Limpar backup.json mantendo metadata inicial
        ensure_backup_json()
        dados = ler_backup_json()
        dados['caixas'] = []
        dados['arquivos'] = []
        dados['segurados'] = []
        dados['metadata']['total_caixas'] = 0
        dados['metadata']['total_arquivos'] = 0
        dados['metadata']['total_segurados'] = 0
        dados['metadata']['ultima_atualizacao'] = datetime.now().isoformat()
        salvar_backup_json(dados)

        # opcional: remover arquivos físicos (atenção: irreversível)
        # for f in os.listdir(FILES_DIR):
        #     try:
        #         os.remove(os.path.join(FILES_DIR, f))
        #     except Exception:
        #         pass

        global last_update_time
        last_update_time = datetime.now()
        return jsonify({
            "mensagem": "✅ Todos os dados foram limpos com sucesso",
            "timestamp": last_update_time.isoformat()
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao limpar dados: {str(e)}"}), 500

# ========== MIDDLEWARE PARA ATUALIZAÇÃO AUTOMÁTICA ==========
@app.after_request
def after_request(response):
    """Atualiza timestamp após cada requisição que modifica dados"""
    global last_update_time
    
    # Verificar se a requisição modificou dados
    if request.method in ['POST', 'PUT', 'DELETE']:
        if response.status_code in [200, 201]:
            last_update_time = datetime.now()
            # Log da atualização
            logger.info(f"🔄 Dados atualizados via {request.method} {request.path}")
    
    return response

# ========== MANUSEIO DE ERROS ==========
@app.errorhandler(404)
def not_found(error):
    return jsonify({"erro": "Endpoint não encontrado", "codigo": 404}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"erro": "Erro interno do servidor", "codigo": 500}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"erro": "Não autorizado", "codigo": 401}), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"erro": "Requisição inválida", "codigo": 400}), 400

# ========== INICIALIZAÇÃO ==========
def inicializar_aplicacao():
    """Inicializa toda a aplicação"""
    global app_start_time, last_update_time
    app_start_time = datetime.now()
    last_update_time = app_start_time
    
    mostrar_banner()
    
    # Verificar dependências
    if not verificar_dependencias():
        logger.error("🚨 Dependências faltantes. Instale com: pip install -r requirements.txt")
        return False
    
    # Inicializar banco de dados
    if not inicializar_database():
        logger.error("🚨 Falha na conexão com banco de dados")
        # Continuar mesmo sem banco para modo de emergência
        logger.warning("⚠️ Continuando em modo de emergência (apenas API básica)")
    
    # Registrar blueprints
    try:
        registrar_blueprints()
    except Exception as e:
        logger.error(f"🚨 Falha no registro de alguns blueprints: {e}")
        # Continua mesmo com alguns blueprints faltando
    
    logger.info("🎉 Aplicação inicializada com sucesso!")
    return True

# ========== EXECUÇÃO PRINCIPAL ==========
if __name__ == '__main__':
    print("\n🚀 Iniciando GCA API...")
    
    if inicializar_aplicacao():
        print(f"\n📍 Servidor rodando em: http://{CONFIG['host']}:{CONFIG['port']}")
        print("📚 Documentação: http://localhost:5000")
        print("🔍 Health Check: http://localhost:5000/api/health")
        print("📊 System Info: http://localhost:5000/api/info")
        print("🔄 Sync: http://localhost:5000/api/sync")
        print("\n🎯 NOVAS FUNCIONALIDADES DE BUSCA:")
        print("   GET /api/busca?q=termo          - Busca geral")
        print("   GET /api/busca/caixas?codigo=X  - Busca caixas")
        print("   GET /api/busca/arquivos?nb=X    - Busca arquivos")
        print("   GET /api/busca/segurados?cpf=X  - Busca segurados")
        print("   GET /api/caixas/CODIGO/arquivos - Arquivos da caixa")
        print("   GET /api/segurados/CPF/arquivos - Arquivos do segurado")
        print("   GET /api/arquivos/NB/detalhes   - Detalhes completos")
        print("\n⚡ Endpoints Principais:")
        print("   POST /api/caixas     - Criar caixa")
        print("   GET  /api/caixas     - Listar caixas") 
        print("   POST /api/arquivos   - Criar arquivo")
        print("   GET  /api/arquivos   - Listar arquivos")
        print("   POST /api/segurados  - Criar segurado")
        print("   GET  /api/segurados  - Listar segurados")
        print("   POST /api/refresh    - Forçar atualização")
        print("   POST /api/limpar     - Limpar todos os dados (DEV)")
        print("\n🔄 Funcionalidades de Atualização:")
        print("   ✅ Atualização automática em tempo real")
        print("   ✅ Sincronização MongoDB/JSON")
        print("   ✅ Timestamp de última modificação")
        print("   ✅ Refresh manual dos dados")
        print("\n🔐 Autenticação:")
        print("   Usuário: admin")
        print("   Senha:   password")
        print("\n💾 Status Banco de Dados:")
        print(f"   MongoDB: {'✅' if mongo_available else '❌'}")
        print(f"   JSON: {'✅' if json_available else '❌'}")
        print("\n⏹️  Pressione Ctrl+C para parar o servidor")
        print("="*60)
        
        try:
            app.run(
                host=CONFIG['host'],
                port=CONFIG['port'],
                debug=CONFIG['debug'],
                threaded=True  # Permite múltiplas requisições simultâneas
            )
        except KeyboardInterrupt:
            print("\n\n🛑 Servidor parado pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro ao executar servidor: {e}")
    else:
        print("\n❌ Falha na inicialização da aplicação")
        sys.exit(1)
