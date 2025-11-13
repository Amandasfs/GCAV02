import json
import os
import uuid
from datetime import datetime

class JSONBaseHandler:
    """Classe base para manipulação do arquivo JSON."""

    def __init__(self, file_path="data/backup.json"):
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            self._criar_arquivo_inicial()

    def _criar_arquivo_inicial(self):
        """Cria estrutura inicial do JSON"""
        self.salvar_dados(self._criar_estrutura_vazia())
        print(f"📁 Arquivo JSON inicializado: {self.file_path}")

    def _criar_estrutura_vazia(self):
        """Retorna estrutura vazia padrão"""
        return {
            "caixas": [],
            "arquivos": [],
            "segurados": [],
            "metadata": {
                "criado_em": datetime.now().isoformat(),
                "ultima_atualizacao": datetime.now().isoformat(),
                "total_caixas": 0,
                "total_arquivos": 0,
                "total_segurados": 0,
                "proximo_id": 1
            }
        }

    def ler_dados(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                conteudo = f.read().strip()
            if not conteudo:
                self._criar_arquivo_inicial()
                return self._criar_estrutura_vazia()
            dados = json.loads(conteudo)
            return self._validar_estrutura(dados)
        except (json.JSONDecodeError, Exception):
            self._criar_arquivo_inicial()
            return self._criar_estrutura_vazia()

    def _validar_estrutura(self, dados):
        estrutura = self._criar_estrutura_vazia()
        for key in estrutura.keys():
            if key not in dados:
                dados[key] = estrutura[key]
            elif key == "metadata":
                for meta_key in estrutura["metadata"].keys():
                    if meta_key not in dados["metadata"]:
                        dados["metadata"][meta_key] = estrutura["metadata"][meta_key]
        return dados

    def salvar_dados(self, dados):
        try:
            if "metadata" in dados:
                dados["metadata"]["ultima_atualizacao"] = datetime.now().isoformat()
                dados["metadata"]["total_caixas"] = len(dados.get("caixas", []))
                dados["metadata"]["total_arquivos"] = len(dados.get("arquivos", []))
                dados["metadata"]["total_segurados"] = len(dados.get("segurados", []))
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar JSON: {e}")
            return False

    def _gerar_id_unico(self):
        return f"{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"

    def _verificar_duplicata(self, dados, tipo, campo, valor):
        return any(item.get(campo) == valor for item in dados[tipo])

    def get_stats(self):
        dados = self.ler_dados()
        return {
            "total_caixas": len(dados["caixas"]),
            "total_arquivos": len(dados["arquivos"]),
            "total_segurados": len(dados["segurados"]),
            "ultima_atualizacao": dados["metadata"]["ultima_atualizacao"]
        }
