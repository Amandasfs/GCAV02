# app.py
import tkinter as tk
import os
import sys

# Adicionar pasta screens ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'screens_app'))

from screens_app.login_screen import LoginScreen
from screens_app.admin_auth import AdminAuth
from screens_app.dashboard_screen import DashboardScreen
from screens_app.busca_screen import BuscaScreen
from screens_app.caixas_screen import CaixasScreen
from screens_app.arquivos_screen import ArquivosScreen
from screens_app.segurados_screen import SeguradosScreen
from screens_app.relatorios_screen import RelatoriosScreen

class GCAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GCA - Sistema de Gerenciamento")
        self.root.geometry("1200x800")
        
        # Configurações
        self.API_BASE = 'http://localhost:5000'
        
        # Gerenciador de admin
        self.admin_auth = AdminAuth()
        self.admin_auth.set_auth_callback(self.on_admin_auth_change)
        
        # Estado da aplicação
        self.current_screen = None
        self.user_credentials = {'username': 'user', 'password': 'pass'}
        self.screens = {}
        
        # Mostrar tela de login primeiro
        self.show_login_screen()
        
    def show_login_screen(self):
        # Destruir tela atual se existir
        if self.current_screen:
            if hasattr(self.current_screen, 'destroy'):
                self.current_screen.destroy()
            elif hasattr(self.current_screen, 'frame') and hasattr(self.current_screen.frame, 'destroy'):
                self.current_screen.frame.destroy()
            
        # Criar nova tela de login
        self.current_screen = LoginScreen(
            self.root, 
            self.on_login_success
        )
        
    def on_login_success(self):
        # Entrar direto no sistema após login
        self.show_main_app()
        
    def show_main_app(self):
        # Destruir tela de login
        if self.current_screen:
            if hasattr(self.current_screen, 'destroy'):
                self.current_screen.destroy()
            elif hasattr(self.current_screen, 'frame') and hasattr(self.current_screen.frame, 'destroy'):
                self.current_screen.frame.destroy()
            
        # Criar interface principal
        self.setup_main_interface()
        
    def setup_main_interface(self):
        # Container principal
        self.main_container = tk.Frame(self.root, bg='white')
        self.main_container.pack(fill='both', expand=True)
        
        # Header
        self.create_header()
        
        # Status Bar
        self.create_status_bar()
        
        # Abas
        self.create_tabs()
        
        # Área de conteúdo
        self.content_frame = tk.Frame(self.main_container, bg='white')
        self.content_frame.pack(fill='both', expand=True)
        
        # Inicializar telas
        self.screens = {
            'dashboard': DashboardScreen(self.content_frame, self.API_BASE, self.user_credentials, self.admin_auth),
            'busca': BuscaScreen(self.content_frame, self.API_BASE, self.user_credentials, self.admin_auth),
            'caixas': CaixasScreen(self.content_frame, self.API_BASE, self.user_credentials, self.admin_auth),
            'arquivos': ArquivosScreen(self.content_frame, self.API_BASE, self.user_credentials, self.admin_auth),
            'segurados': SeguradosScreen(self.content_frame, self.API_BASE, self.user_credentials, self.admin_auth),
            'relatorios': RelatoriosScreen(self.content_frame, self.API_BASE, self.user_credentials, self.admin_auth)
        }
        
        # Mostrar dashboard inicial
        self.show_screen('dashboard')
        
    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg='#2c3e50', height=120)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Frame do título (esquerda)
        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        title_frame.pack(side='left', fill='both', expand=True)

        title_label = tk.Label(title_frame,
                              text="🏢 GCA Sistema",
                              font=('Arial', 24, 'bold'),
                              fg='white',
                              bg='#2c3e50')
        title_label.pack(pady=(30, 5))

        subtitle_label = tk.Label(title_frame,
                                 text="Sistema de Gerenciamento de Caixas e Arquivos",
                                 font=('Arial', 12),
                                 fg='white',
                                 bg='#2c3e50')
        subtitle_label.pack(pady=(0, 30))

        # Frame dos botões (direita)
        button_frame = tk.Frame(header_frame, bg='#2c3e50')
        button_frame.pack(side='right', padx=20, pady=10)

        # Botão de Admin
        self.admin_button = tk.Button(
            button_frame,
            text="👤 Área Admin",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='#e74c3c',  # Vermelho quando não autenticado
            relief='flat',
            padx=15,
            pady=8,
            command=self.open_admin_panel
        )
        self.admin_button.pack(pady=5)

        # Botão de Logout
        logout_btn = tk.Button(
            button_frame,
            text="🚪 Sair",
            font=('Arial', 9),
            fg='white',
            bg='#95a5a6',
            relief='flat',
            padx=12,
            pady=5,
            command=self.logout
        )
        logout_btn.pack(pady=5)
        
    def create_status_bar(self):
        status_frame = tk.Frame(self.main_container, bg='#f8f9fa', height=80)
        status_frame.pack(fill='x', padx=0, pady=0)
        status_frame.pack_propagate(False)

        status_items = [
            ("Status API", "api_status", "🟡 VERIFICANDO"),
            ("MongoDB", "mongo_status", "🟡 VERIFICANDO"),
            ("JSON", "json_status", "🟡 VERIFICANDO"),
            ("Total Itens", "total_items", "0"),
            ("Status Admin", "admin_status", "🔒 Não Autenticado")
        ]

        for i, (label_text, var_name, default_value) in enumerate(status_items):
            item_frame = tk.Frame(status_frame, bg='#f8f9fa')
            item_frame.pack(side='left', expand=True, fill='both')

            label = tk.Label(item_frame,
                            text=label_text,
                            font=('Arial', 9),
                            fg='#6c757d',
                            bg='#f8f9fa')
            label.pack(pady=(15, 2))

            value_var = tk.StringVar(value=default_value)
            setattr(self, f"{var_name}_var", value_var)

            value_label = tk.Label(item_frame,
                                  textvariable=value_var,
                                  font=('Arial', 13, 'bold'),
                                  fg='#2c3e50',
                                  bg='#f8f9fa')
            value_label.pack(pady=(2, 15))
        
    def create_tabs(self):
        self.tab_frame = tk.Frame(self.main_container, bg='#34495e')
        self.tab_frame.pack(fill='x')

        self.tabs = {}
        tab_names = [
            ("📊 Dashboard", "dashboard"),
            ("🔍 Busca Avançada", "busca"),
            ("📦 Caixas", "caixas"),
            ("📁 Arquivos", "arquivos"),
            ("👤 Segurados", "segurados"),
            ("📋 Relatórios", "relatorios")
        ]

        for text, tab_id in tab_names:
            tab = tk.Button(self.tab_frame,
                           text=text,
                           font=('Arial', 11),
                           fg='white',
                           bg='#2c3e50',
                           relief='flat',
                           bd=0,
                           padx=20,
                           pady=15,
                           command=lambda t=tab_id: self.open_tab(t))
            tab.pack(side='left', fill='x', expand=True)
            self.tabs[tab_id] = tab

        self.tabs['dashboard'].configure(bg='#3498db')
        
    def open_tab(self, tab_name):
        for tab in self.tabs.values():
            tab.configure(bg='#2c3e50')

        self.tabs[tab_name].configure(bg='#3498db')
        
        self.show_screen(tab_name)
        
    def show_screen(self, screen_name):
        for screen in self.screens.values():
            screen.hide()
            
        if screen_name in self.screens:
            self.screens[screen_name].show()
    
    def open_admin_panel(self):
        """Abre o painel administrativo"""
        self.admin_auth.show_admin_panel(self.root)
    
    def on_admin_auth_change(self, is_authenticated, username):
        """Callback quando o estado de autenticação do admin muda"""
        if is_authenticated:
            self.admin_button.config(
                text=f"👤 Admin: {username}",
                bg='#27ae60'  # Verde quando autenticado
            )
            self.admin_status_var.set("🟢 Autenticado")
        else:
            self.admin_button.config(
                text="👤 Área Admin",
                bg='#e74c3c'  # Vermelho quando não autenticado
            )
            self.admin_status_var.set("🔒 Não Autenticado")
    
    def logout(self):
        """Faz logout do sistema"""
        from tkinter import messagebox
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            # Fazer logout do admin também
            self.admin_auth.logout()
            
            # Voltar para tela de login
            self.show_login_screen()

def main():
    root = tk.Tk()
    app = GCAApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
