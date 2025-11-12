import hashlib
from functools import wraps
from flask import request, jsonify

# Simulação de banco de usuários (em produção usar MongoDB)
USUARIOS = {
    "admin": {
        "senha": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "senha inventada"
        "nivel": "admin"
    }
}

def gerar_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_autenticacao(username, senha):
    if username in USUARIOS:
        return USUARIOS[username]["senha"] == gerar_hash(senha)
    return False

def requer_autenticacao(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not verificar_autenticacao(auth.username, auth.password):
            return jsonify({"erro": "Autenticação requerida"}), 401
        return f(*args, **kwargs)
    return decorated