"""
Utilitários para comunicação com a API GCA
"""

import requests
import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)

class APIUtils:
    def __init__(self, base_url, credentials):
        self.base_url = base_url
        self.credentials = credentials
        self.timeout = 30
    
    def make_request(self, method, endpoint, **kwargs):
        """
        Faz uma requisição para a API com tratamento de erros
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Adicionar autenticação se não for fornecida
            if 'auth' not in kwargs:
                kwargs['auth'] = self.credentials
            
            # Adicionar timeout se não for fornecido
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            
            response = requests.request(method, url, **kwargs)
            
            if response.status_code == 401:
                messagebox.showerror("Erro de Autenticação", 
                                   "Credenciais inválidas. Verifique usuário e senha.")
                return None
            elif response.status_code == 404:
                logger.warning(f"Endpoint não encontrado: {endpoint}")
                return None
            elif response.status_code >= 500:
                messagebox.showerror("Erro do Servidor", 
                                   "Erro interno do servidor. Tente novamente.")
                return None
            
            return response
            
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Erro de Conexão", 
                               "Não foi possível conectar com a API. Verifique se o servidor está rodando.")
            return None
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout", 
                               "A requisição demorou muito tempo. Tente novamente.")
            return None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro na requisição: {str(e)}")
            return None
    
    def get(self, endpoint, **kwargs):
        """Faz uma requisição GET"""
        return self.make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint, **kwargs):
        """Faz uma requisição POST"""
        return self.make_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint, **kwargs):
        """Faz uma requisição PUT"""
        return self.make_request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint, **kwargs):
        """Faz uma requisição DELETE"""
        return self.make_request('DELETE', endpoint, **kwargs)
    
    def check_health(self):
        """Verifica se a API está online"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False