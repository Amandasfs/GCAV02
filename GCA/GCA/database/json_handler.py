import json
import os
from datetime import datetime

class JSONHandler:
    def __init__(self, filename='data/backup.json'):
        self.filename = filename
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Garante que o arquivo JSON exista com estrutura inicial"""
        try:
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
                print("📁 Arquivo JSON criado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao criar arquivo JSON: {e}")
    
    def ler_dados(self):
        """Lê os dados do arquivo JSON"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao ler arquivo JSON: {e}")
            return self._criar_estrutura_vazia()
    
    def salvar_dados(self, data):
        """Salva os dados no arquivo JSON"""
        try:
            # Atualizar metadata
            data["metadata"]["ultima_atualizacao"] = datetime.now().isoformat()
            data["metadata"]["total_caixas"] = len(data["caixas"])
            data["metadata"]["total_arquivos"] = len(data["arquivos"])
            data["metadata"]["total_segurados"] = len(data["segurados"])
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo JSON: {e}")
            return False
    
    def _criar_estrutura_vazia(self):
        """Cria estrutura vazia em caso de erro"""
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
    
    # ========== MÉTODOS PARA ARQUIVOS ==========
    def inserir_arquivo(self, arquivo_data):
        """Insere um novo arquivo no JSON"""
        try:
            dados = self.ler_dados()
            
            # Verificar se NB já existe
            if any(a.get('NB') == arquivo_data.get('NB') for a in dados["arquivos"]):
                return {"erro": f"Arquivo com NB {arquivo_data.get('NB')} já existe"}
            
            # Adicionar timestamp
            arquivo_data['criado_em'] = datetime.now().isoformat()
            arquivo_data['atualizado_em'] = datetime.now().isoformat()
            
            dados["arquivos"].append(arquivo_data)
            
            if self.salvar_dados(dados):
                return {"sucesso": True, "mensagem": "Arquivo criado com sucesso"}
            else:
                return {"erro": "Erro ao salvar arquivo"}
                
        except Exception as e:
            return {"erro": f"Erro ao inserir arquivo: {str(e)}"}
    
    def listar_arquivos(self, filtro=None):
        """Lista arquivos com filtro opcional"""
        try:
            dados = self.ler_dados()
            arquivos = dados["arquivos"]
            
            if not filtro:
                return arquivos
            
            # Aplicar filtros
            resultados = []
            for arquivo in arquivos:
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
                    resultados.append(arquivo)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
            return []
    
    def buscar_arquivo(self, nb):
        """Busca um arquivo pelo NB"""
        try:
            dados = self.ler_dados()
            for arquivo in dados["arquivos"]:
                if arquivo.get('NB') == nb:
                    return arquivo
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar arquivo: {e}")
            return None
    
    def atualizar_arquivo(self, nb, atualizacao):
        """Atualiza um arquivo existente"""
        try:
            dados = self.ler_dados()
            
            for i, arquivo in enumerate(dados["arquivos"]):
                if arquivo.get('NB') == nb:
                    # Atualizar dados
                    atualizacao['atualizado_em'] = datetime.now().isoformat()
                    dados["arquivos"][i].update(atualizacao)
                    
                    if self.salvar_dados(dados):
                        return True
                    return False
            
            return False  # Arquivo não encontrado
            
        except Exception as e:
            print(f"❌ Erro ao atualizar arquivo: {e}")
            return False
    
    def deletar_arquivo(self, nb):
        """Deleta um arquivo pelo NB"""
        try:
            dados = self.ler_dados()
            
            # Filtrar arquivos, removendo o com NB especificado
            dados["arquivos"] = [a for a in dados["arquivos"] if a.get('NB') != nb]
            
            if self.salvar_dados(dados):
                return True
            return False
            
        except Exception as e:
            print(f"❌ Erro ao deletar arquivo: {e}")
            return False
    
    def get_stats(self):
        """Retorna estatísticas do JSON"""
        data = self.ler_dados()
        return {
            "total_caixas": len(data["caixas"]),
            "total_arquivos": len(data["arquivos"]),
            "total_segurados": len(data["segurados"]),
            "ultima_atualizacao": data["metadata"]["ultima_atualizacao"]
        }
    
    def limpar_tudo(self):
        """Limpa todos os dados"""
        try:
            data = self._criar_estrutura_vazia()
            return self.salvar_dados(data)
        except Exception as e:
            print(f"❌ Erro ao limpar dados: {e}")
            return False