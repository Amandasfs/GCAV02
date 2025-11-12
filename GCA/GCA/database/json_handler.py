import json
import os
import uuid
from datetime import datetime

class JSONHandler:
    def __init__(self, file_path="data/backup.json"):
        self.file_path = file_path
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Garante que o arquivo existe e tem estrutura válida"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        # Se o arquivo não existe ou está vazio, criar estrutura inicial
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            self._criar_arquivo_inicial()
    
    def _criar_arquivo_inicial(self):
        """Cria arquivo inicial com estrutura válida"""
        initial_data = {
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
        self.salvar_dados(initial_data)
        print(f"📁 Arquivo JSON inicializado: {self.file_path}")
    
    def _gerar_id_unico(self):
        """Gera um ID único baseado no timestamp e UUID"""
        return f"{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"
    
    def ler_dados(self):
        """Lê dados do JSON com tratamento de erro robusto"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                conteudo = f.read().strip()
                
            # Se arquivo está vazio, recriar
            if not conteudo:
                print("⚠️ Arquivo JSON vazio, recriando...")
                self._criar_arquivo_inicial()
                return self._criar_estrutura_vazia()
            
            dados = json.loads(conteudo)
            return self._validar_estrutura(dados)
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON corrompido: {e}. Recriando...")
            self._criar_arquivo_inicial()
            return self._criar_estrutura_vazia()
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return self._criar_estrutura_vazia()
    
    def _validar_estrutura(self, dados):
        """Valida e corrige estrutura dos dados"""
        if not isinstance(dados, dict):
            return self._criar_estrutura_vazia()
        
        # Garantir que todas as chaves existem
        estrutura = self._criar_estrutura_vazia()
        for key in estrutura.keys():
            if key not in dados:
                dados[key] = estrutura[key]
            elif key == "metadata":
                for meta_key in estrutura["metadata"].keys():
                    if meta_key not in dados["metadata"]:
                        dados["metadata"][meta_key] = estrutura["metadata"][meta_key]
        
        return dados
    
    def _criar_estrutura_vazia(self):
        """Cria estrutura de dados vazia"""
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
    
    def salvar_dados(self, dados):
        """Salva dados no JSON com tratamento de erro"""
        try:
            # Atualizar metadata
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
    
    def _verificar_duplicata(self, dados, tipo, campo, valor):
        """Verifica se já existe um item com o mesmo valor no campo especificado"""
        for item in dados[tipo]:
            if item.get(campo) == valor:
                return True
        return False
    
    def get_stats(self):
        """Retorna estatísticas do banco"""
        dados = self.ler_dados()
        return {
            "total_caixas": len(dados["caixas"]),
            "total_arquivos": len(dados["arquivos"]),
            "total_segurados": len(dados["segurados"]),
            "ultima_atualizacao": dados["metadata"]["ultima_atualizacao"]
        }
    
    # ========== OPERAÇÕES PARA CAIXAS ==========
    def inserir_caixa(self, caixa_dict):
        try:
            dados = self.ler_dados()
            
            # Verificar se código já existe
            if self._verificar_duplicata(dados, "caixas", "codigo", caixa_dict["codigo"]):
                return {"erro": f"Já existe uma caixa com código {caixa_dict['codigo']}"}
            
            # Adicionar ID único e timestamps
            caixa_dict["id"] = self._gerar_id_unico()
            caixa_dict["data_atualizacao"] = datetime.now().isoformat()
            caixa_dict["data_criacao"] = datetime.now().isoformat()
            
            dados["caixas"].append(caixa_dict)
            
            if self.salvar_dados(dados):
                return {"sucesso": True, "id": caixa_dict["id"], "codigo": caixa_dict["codigo"]}
            else:
                return {"erro": "Falha ao salvar dados"}
                
        except Exception as e:
            return {"erro": f"Erro ao inserir caixa: {str(e)}"}
    
    def buscar_caixa(self, codigo):
        try:
            dados = self.ler_dados()
            for caixa in dados["caixas"]:
                if caixa["codigo"] == codigo:
                    return caixa
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar caixa: {e}")
            return None
    
    def listar_caixas(self):
        try:
            return self.ler_dados()["caixas"]
        except Exception as e:
            print(f"❌ Erro ao listar caixas: {e}")
            return []
    
    def atualizar_caixa(self, codigo, atualizacao):
        try:
            dados = self.ler_dados()
            for caixa in dados["caixas"]:
                if caixa["codigo"] == codigo:
                    # Atualizar campos, exceto ID e data_criacao
                    for key, value in atualizacao.items():
                        if key not in ["id", "data_criacao"]:
                            caixa[key] = value
                    
                    caixa["data_atualizacao"] = datetime.now().isoformat()
                    
                    if self.salvar_dados(dados):
                        return {"sucesso": True, "codigo": codigo}
                    else:
                        return {"erro": "Falha ao salvar dados"}
            
            return {"erro": f"Caixa com código {codigo} não encontrada"}
        except Exception as e:
            return {"erro": f"Erro ao atualizar caixa: {str(e)}"}
    
    def deletar_caixa(self, codigo):
        try:
            dados = self.ler_dados()
            caixas_originais = len(dados["caixas"])
            dados["caixas"] = [c for c in dados["caixas"] if c["codigo"] != codigo]
            caixas_finais = len(dados["caixas"])
            
            if caixas_finais < caixas_originais:
                if self.salvar_dados(dados):
                    return {"sucesso": True, "codigo": codigo}
                else:
                    return {"erro": "Falha ao salvar dados"}
            else:
                return {"erro": f"Caixa com código {codigo} não encontrada"}
        except Exception as e:
            return {"erro": f"Erro ao deletar caixa: {str(e)}"}
    
    # ========== OPERAÇÕES PARA ARQUIVOS ==========
    def inserir_arquivo(self, arquivo_dict):
        try:
            dados = self.ler_dados()
            
            # Verificar se NB já existe
            if self._verificar_duplicata(dados, "arquivos", "NB", arquivo_dict["NB"]):
                return {"erro": f"Já existe um arquivo com NB {arquivo_dict['NB']}"}
            
            # Verificar se a caixa existe
            caixa_existe = any(c["codigo"] == arquivo_dict["Caixa_codigo"] for c in dados["caixas"])
            if not caixa_existe:
                return {"erro": f"Caixa com código {arquivo_dict['Caixa_codigo']} não existe"}
            
            # Adicionar ID único e timestamps
            arquivo_dict["id"] = self._gerar_id_unico()
            arquivo_dict["data_atualizacao"] = datetime.now().isoformat()
            arquivo_dict["data_criacao"] = datetime.now().isoformat()
            
            dados["arquivos"].append(arquivo_dict)
            
            if self.salvar_dados(dados):
                return {"sucesso": True, "id": arquivo_dict["id"], "NB": arquivo_dict["NB"]}
            else:
                return {"erro": "Falha ao salvar dados"}
                
        except Exception as e:
            return {"erro": f"Erro ao inserir arquivo: {str(e)}"}
    
    def buscar_arquivo(self, NB):
        try:
            dados = self.ler_dados()
            for arquivo in dados["arquivos"]:
                if arquivo["NB"] == NB:
                    return arquivo
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar arquivo: {e}")
            return None
    
    def listar_arquivos(self):
        try:
            return self.ler_dados()["arquivos"]
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
            return []
    
    def atualizar_arquivo(self, NB, atualizacao):
        try:
            dados = self.ler_dados()
            for arquivo in dados["arquivos"]:
                if arquivo["NB"] == NB:
                    # Atualizar campos, exceto ID, NB e data_criacao
                    for key, value in atualizacao.items():
                        if key not in ["id", "NB", "data_criacao"]:
                            arquivo[key] = value
                    
                    arquivo["data_atualizacao"] = datetime.now().isoformat()
                    
                    if self.salvar_dados(dados):
                        return {"sucesso": True, "NB": NB}
                    else:
                        return {"erro": "Falha ao salvar dados"}
            
            return {"erro": f"Arquivo com NB {NB} não encontrado"}
        except Exception as e:
            return {"erro": f"Erro ao atualizar arquivo: {str(e)}"}
    
    def deletar_arquivo(self, NB):
        try:
            dados = self.ler_dados()
            arquivos_originais = len(dados["arquivos"])
            dados["arquivos"] = [a for a in dados["arquivos"] if a["NB"] != NB]
            arquivos_finais = len(dados["arquivos"])
            
            if arquivos_finais < arquivos_originais:
                if self.salvar_dados(dados):
                    return {"sucesso": True, "NB": NB}
                else:
                    return {"erro": "Falha ao salvar dados"}
            else:
                return {"erro": f"Arquivo com NB {NB} não encontrado"}
        except Exception as e:
            return {"erro": f"Erro ao deletar arquivo: {str(e)}"}
    
    # ========== OPERAÇÕES PARA SEGURADOS ==========
    def inserir_segurado(self, segurado_dict):
        try:
            dados = self.ler_dados()
            
            # Verificar se CPF já existe
            if self._verificar_duplicata(dados, "segurados", "cpf", segurado_dict["cpf"]):
                return {"erro": f"Já existe um segurado com CPF {segurado_dict['cpf']}"}
            
            # Adicionar ID único e timestamps
            segurado_dict["id"] = self._gerar_id_unico()
            segurado_dict["data_atualizacao"] = datetime.now().isoformat()
            segurado_dict["data_criacao"] = datetime.now().isoformat()
            segurado_dict["Arquivos"] = segurado_dict.get("Arquivos", [])
            
            dados["segurados"].append(segurado_dict)
            
            if self.salvar_dados(dados):
                return {"sucesso": True, "id": segurado_dict["id"], "cpf": segurado_dict["cpf"]}
            else:
                return {"erro": "Falha ao salvar dados"}
                
        except Exception as e:
            return {"erro": f"Erro ao inserir segurado: {str(e)}"}
    
    def buscar_segurado(self, cpf):
        try:
            dados = self.ler_dados()
            for segurado in dados["segurados"]:
                if segurado["cpf"] == cpf:
                    return segurado
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar segurado: {e}")
            return None
    
    def listar_segurados(self):
        try:
            return self.ler_dados()["segurados"]
        except Exception as e:
            print(f"❌ Erro ao listar segurados: {e}")
            return []
    
    def atualizar_segurado(self, cpf, atualizacao):
        try:
            dados = self.ler_dados()
            for segurado in dados["segurados"]:
                if segurado["cpf"] == cpf:
                    # Atualizar campos, exceto ID, CPF e data_criacao
                    for key, value in atualizacao.items():
                        if key not in ["id", "cpf", "data_criacao"]:
                            segurado[key] = value
                    
                    segurado["data_atualizacao"] = datetime.now().isoformat()
                    
                    if self.salvar_dados(dados):
                        return {"sucesso": True, "cpf": cpf}
                    else:
                        return {"erro": "Falha ao salvar dados"}
            
            return {"erro": f"Segurado com CPF {cpf} não encontrado"}
        except Exception as e:
            return {"erro": f"Erro ao atualizar segurado: {str(e)}"}
    
    def deletar_segurado(self, cpf):
        try:
            dados = self.ler_dados()
            segurados_originais = len(dados["segurados"])
            dados["segurados"] = [s for s in dados["segurados"] if s["cpf"] != cpf]
            segurados_finais = len(dados["segurados"])
            
            if segurados_finais < segurados_originais:
                if self.salvar_dados(dados):
                    return {"sucesso": True, "cpf": cpf}
                else:
                    return {"erro": "Falha ao salvar dados"}
            else:
                return {"erro": f"Segurado com CPF {cpf} não encontrado"}
        except Exception as e:
            return {"erro": f"Erro ao deletar segurado: {str(e)}"}
    
    def limpar_tudo(self):
        """Limpa todos os dados (apenas para desenvolvimento)"""
        try:
            dados = self._criar_estrutura_vazia()
            if self.salvar_dados(dados):
                return {"sucesso": True, "mensagem": "Todos os dados foram limpos"}
            else:
                return {"erro": "Falha ao limpar dados"}
        except Exception as e:
            return {"erro": f"Erro ao limpar dados: {str(e)}"}