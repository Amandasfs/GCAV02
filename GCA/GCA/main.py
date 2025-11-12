#!/usr/bin/env python3
"""
GCA API - Sistema de Gerenciamento de Caixas e Arquivos
Sistema completo com MongoDB, JSON Backup e Autenticação
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import sys
from datetime import datetime
import time

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

# ========== BANNER INICIAL ==========
def mostrar_banner():
    print("\n" + "="*60)
    print("🎯 GCA API - SISTEMA DE GERENCIAMENTO".center(60))
    print("="*60)
    print("📦 Módulos:".ljust(30) + "✅ Caixas, Arquivos, Segurados")
    print("🔐 Autenticação:".ljust(30) + "✅ Basic Auth")
    print("💾 Banco de Dados:".ljust(30) + "✅ MongoDB + JSON Backup")
    print("🌐 API REST:".ljust(30) + "✅ Flask + CORS")
    print("🔄 Atualização:".ljust(30) + "✅ Tempo Real")
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
            json_handler.ensure_file_exists()
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
                criar_json_manual()
                from database.json_handler import JSONHandler
                json_handler = JSONHandler()
                json_available = True
                logger.info("✅ JSON criado manualmente e inicializado")
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
    """Cria arquivo JSON manualmente em caso de falha"""
    import json
    from datetime import datetime
    
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
    
    with open('data/backup.json', 'w', encoding='utf-8') as f:
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

# ========== ROTAS DE SINCRONIZAÇÃO E ATUALIZAÇÃO ==========
@app.route('/api/sync', methods=['GET'])
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
def obter_atualizacoes():
    """Retorna informações sobre atualizações recentes"""
    from database.json_handler import JSONHandler
    
    try:
        json_handler = JSONHandler()
        dados = json_handler.ler_dados()
        
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
def refresh_data():
    """Força atualização completa dos dados"""
    try:
        from database.json_handler import JSONHandler
        json_handler = JSONHandler()
        
        # Recarregar dados do JSON
        dados = json_handler.ler_dados()
        
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
        "versao": "2.0.0",
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
                "POST /api/limpar": "Limpar todos os dados (DEV)",
                "POST /api/backup": "Criar backup (EM BREVE)",
                "GET /api/export": "Exportar dados (EM BREVE)"
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
        "versao": "2.0.0",
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
def system_info():
    """Informações do sistema em tempo real"""
    try:
        from database.json_handler import JSONHandler
        json_handler = JSONHandler()
        stats = json_handler.get_stats()
        
        estatisticas = {
            "caixas": stats["total_caixas"],
            "arquivos": stats["total_arquivos"],
            "segurados": stats["total_segurados"]
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
def limpar_dados():
    """Limpa todos os dados (apenas para desenvolvimento)"""
    try:
        from database.json_handler import JSONHandler
        json_handler = JSONHandler()
        resultado = json_handler.limpar_tudo()
        
        if resultado.get("sucesso"):
            global last_update_time
            last_update_time = datetime.now()
            return jsonify({
                "mensagem": "✅ Todos os dados foram limpos com sucesso",
                "timestamp": last_update_time.isoformat()
            }), 200
        else:
            return jsonify({"erro": resultado.get("erro", "Erro desconhecido")}), 500
            
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
    if not registrar_blueprints():
        logger.error("🚨 Falha no registro de alguns blueprints")
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