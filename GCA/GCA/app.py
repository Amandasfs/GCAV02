import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import threading
from datetime import datetime
import time
import base64

class GCAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GCA - Sistema de Gerenciamento")
        self.root.geometry("1200x800")
        self.root.configure(bg='#667eea')
        
        # Configurações da API
        self.API_BASE = 'http://localhost:5000/api'
        self.USERNAME = 'admin'
        self.PASSWORD = 'password'
        
        # Headers de autenticação
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode(f'{self.USERNAME}:{self.PASSWORD}'.encode()).decode()
        }
        
        # Estado da aplicação
        self.app_state = {
            'current_tab': 'dashboard',
            'auto_refresh': True,
            'refresh_interval': None,
            'last_update': None,
            'data': {
                'caixas': [],
                'arquivos': [],
                'segurados': []
            }
        }
        
        # Criar interface
        self.create_widgets()
        
        # Inicializar
        self.load_initial_data()
        
    def create_widgets(self):
        # Container principal
        self.main_container = tk.Frame(self.root, bg='white', bd=0, relief='flat')
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Cabeçalho
        self.create_header()
        
        # Barra de Status
        self.create_status_bar()
        
        # Navegação por abas
        self.create_tabs()
        
        # Conteúdo das abas
        self.create_tab_content()
        
    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg='#2c3e50', height=120)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="🏢 GCA Sistema", 
                              font=('Arial', 24, 'bold'),
                              fg='white', 
                              bg='#2c3e50')
        title_label.pack(pady=(30, 5))
        
        subtitle_label = tk.Label(header_frame,
                                 text="Sistema de Gerenciamento de Caixas e Arquivos",
                                 font=('Arial', 12),
                                 fg='white',
                                 bg='#2c3e50')
        subtitle_label.pack(pady=(0, 30))
        
    def create_status_bar(self):
        status_frame = tk.Frame(self.main_container, bg='#f8f9fa', height=80)
        status_frame.pack(fill='x', padx=0, pady=0)
        status_frame.pack_propagate(False)
        
        # Status items
        status_items = [
            ("Status API", "api_status", "🟡 VERIFICANDO"),
            ("MongoDB", "mongo_status", "🟡 VERIFICANDO"),
            ("JSON", "json_status", "🟡 VERIFICANDO"),
            ("Total Itens", "total_items", "0")
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
            ("📦 Caixas", "caixas"),
            ("📁 Arquivos", "arquivos"),
            ("👤 Segurados", "segurados")
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
        
        # Marcar dashboard como ativo inicialmente
        self.tabs['dashboard'].configure(bg='#3498db')
    
    def create_tab_content(self):
        self.content_frame = tk.Frame(self.main_container, bg='white')
        self.content_frame.pack(fill='both', expand=True)
        
        # Criar frames para cada aba
        self.tab_frames = {}
        
        # Dashboard
        self.create_dashboard_tab()
        
        # Caixas
        self.create_caixas_tab()
        
        # Arquivos
        self.create_arquivos_tab()
        
        # Segurados
        self.create_segurados_tab()
        
        # Mostrar dashboard inicialmente
        self.tab_frames['dashboard'].pack(fill='both', expand=True)
    
    def create_dashboard_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['dashboard'] = frame
        
        # Título
        title = tk.Label(frame, text="📊 Dashboard do Sistema", 
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)
        
        # Auto-refresh toggle
        toggle_frame = tk.Frame(frame, bg='white')
        toggle_frame.pack(pady=10, anchor='w', padx=20)
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        toggle_btn = tk.Checkbutton(toggle_frame, 
                                   variable=self.auto_refresh_var,
                                   command=self.toggle_auto_refresh,
                                   bg='white')
        toggle_btn.pack(side='left')
        
        toggle_label = tk.Label(toggle_frame, text="Atualização Automática", 
                               font=('Arial', 10), bg='white')
        toggle_label.pack(side='left', padx=5)
        
        # Stats grid
        self.stats_frame = tk.Frame(frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=20)
        
        # Placeholder para stats
        self.stats_placeholder = tk.Label(self.stats_frame, 
                                         text="Carregando estatísticas...",
                                         font=('Arial', 12),
                                         bg='white')
        self.stats_placeholder.pack()
        
        # Last update
        self.last_update_frame = tk.Frame(frame, bg='white')
        self.last_update_frame.pack(pady=10)
        
        self.last_update_label = tk.Label(self.last_update_frame,
                                         text="Última atualização: --:--:--",
                                         font=('Arial', 10),
                                         fg='#6c757d',
                                         bg='white')
        self.last_update_label.pack()
        
        # Botões de ação
        button_frame = tk.Frame(frame, bg='white')
        button_frame.pack(pady=20)
        
        buttons = [
            ("🔄 Atualizar Agora", self.load_stats, '#3498db'),
            ("🧪 Testar API", self.test_api, '#27ae60'),
            ("⚡ Forçar Sync", self.forcar_atualizacao, '#f39c12'),
            ("🗑️ Limpar Tudo", self.clear_all_data, '#e74c3c')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(button_frame,
                           text=text,
                           font=('Arial', 10, 'bold'),
                           fg='white',
                           bg=color,
                           relief='flat',
                           padx=15,
                           pady=8,
                           command=command)
            btn.pack(side='left', padx=5)
    
    def create_caixas_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['caixas'] = frame
        
        # Título
        title = tk.Label(frame, text="📦 Gerenciar Caixas", 
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)
        
        # Formulário
        form_frame = tk.LabelFrame(frame, text="Dados da Caixa", 
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8f9fa',
                                  padx=15,
                                  pady=15)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Campos do formulário
        fields = [
            ("Código da Caixa *", "caixa_codigo", "number"),
            ("NBI *", "caixa_nbi", "number"),
            ("NBF *", "caixa_nbf", "number"),
            ("Prateleira", "caixa_prateleira", "text"),
            ("Bloco", "caixa_bloco", "text"),
            ("Andar", "caixa_andar", "text"),
            ("Corredor", "caixa_corredor", "text")
        ]
        
        self.caixa_fields = {}
        for i, (label, field_name, field_type) in enumerate(fields):
            row = i % 4
            col = i // 4
            
            field_frame = tk.Frame(form_frame, bg='#f8f9fa')
            field_frame.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            lbl = tk.Label(field_frame, text=label, font=('Arial', 9), bg='#f8f9fa')
            lbl.pack(anchor='w')
            
            if field_type == "number":
                entry = tk.Entry(field_frame, width=15, font=('Arial', 10))
            else:
                entry = tk.Entry(field_frame, width=15, font=('Arial', 10))
            
            entry.pack(pady=2)
            self.caixa_fields[field_name] = entry
        
        # Botões
        button_frame = tk.Frame(frame, bg='white')
        button_frame.pack(pady=10, padx=20)
        
        self.btn_criar_caixa = tk.Button(button_frame,
                                        text="➕ Criar Caixa",
                                        font=('Arial', 10, 'bold'),
                                        fg='white',
                                        bg='#3498db',
                                        relief='flat',
                                        padx=15,
                                        pady=8,
                                        command=self.criar_caixa)
        self.btn_criar_caixa.pack(side='left', padx=5)
        
        tk.Button(button_frame,
                 text="🔄 Listar Caixas",
                 font=('Arial', 10, 'bold'),
                 fg='white',
                 bg='#27ae60',
                 relief='flat',
                 padx=15,
                 pady=8,
                 command=lambda: self.listar_caixas(True)).pack(side='left', padx=5)
        
        tk.Button(button_frame,
                 text="🧹 Limpar",
                 font=('Arial', 10, 'bold'),
                 fg='white',
                 bg='#f39c12',
                 relief='flat',
                 padx=15,
                 pady=8,
                 command=self.limpar_form_caixa).pack(side='left', padx=5)
        
        # Mensagens
        self.message_caixas = tk.Label(frame, text="", font=('Arial', 10), bg='white')
        self.message_caixas.pack(pady=5)
        
        # Tabela de caixas
        table_frame = tk.Frame(frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Criar treeview para tabela
        columns = ('Código', 'NBI', 'NBF', 'Localização', 'Ações')
        self.caixas_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.caixas_tree.heading(col, text=col)
            self.caixas_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.caixas_tree.yview)
        self.caixas_tree.configure(yscrollcommand=scrollbar.set)
        
        self.caixas_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Placeholder
        self.caixas_tree.insert('', 'end', values=('Carregando caixas...', '', '', '', ''))
    
    def create_arquivos_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['arquivos'] = frame
        
        # Título
        title = tk.Label(frame, text="📁 Gerenciar Arquivos", 
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)
        
        # Formulário
        form_frame = tk.LabelFrame(frame, text="Dados do Arquivo", 
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8f9fa',
                                  padx=15,
                                  pady=15)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Campos do formulário
        fields = [
            ("NB *", "arquivo_nb", "number"),
            ("APS *", "arquivo_aps", "text"),
            ("CPF Segurado *", "arquivo_seguradofk", "number"),
            ("Tipo *", "arquivo_tipo", "number"),
            ("Código da Caixa *", "arquivo_caixa", "number")
        ]
        
        self.arquivo_fields = {}
        for i, (label, field_name, field_type) in enumerate(fields):
            field_frame = tk.Frame(form_frame, bg='#f8f9fa')
            field_frame.grid(row=i, column=0, padx=10, pady=5, sticky='w')
            
            lbl = tk.Label(field_frame, text=label, font=('Arial', 9), bg='#f8f9fa')
            lbl.pack(anchor='w')
            
            entry = tk.Entry(field_frame, width=20, font=('Arial', 10))
            entry.pack(pady=2)
            self.arquivo_fields[field_name] = entry
        
        # Botões
        button_frame = tk.Frame(frame, bg='white')
        button_frame.pack(pady=10, padx=20)
        
        self.btn_criar_arquivo = tk.Button(button_frame,
                                          text="➕ Criar Arquivo",
                                          font=('Arial', 10, 'bold'),
                                          fg='white',
                                          bg='#3498db',
                                          relief='flat',
                                          padx=15,
                                          pady=8,
                                          command=self.criar_arquivo)
        self.btn_criar_arquivo.pack(side='left', padx=5)
        
        tk.Button(button_frame,
                 text="🔄 Listar Arquivos",
                 font=('Arial', 10, 'bold'),
                 fg='white',
                 bg='#27ae60',
                 relief='flat',
                 padx=15,
                 pady=8,
                 command=lambda: self.listar_arquivos(True)).pack(side='left', padx=5)
        
        tk.Button(button_frame,
                 text="🧹 Limpar",
                 font=('Arial', 10, 'bold'),
                 fg='white',
                 bg='#f39c12',
                 relief='flat',
                 padx=15,
                 pady=8,
                 command=self.limpar_form_arquivo).pack(side='left', padx=5)
        
        # Mensagens
        self.message_arquivos = tk.Label(frame, text="", font=('Arial', 10), bg='white')
        self.message_arquivos.pack(pady=5)
        
        # Tabela de arquivos
        table_frame = tk.Frame(frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('NB', 'APS', 'CPF Segurado', 'Tipo', 'Caixa', 'Ações')
        self.arquivos_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.arquivos_tree.heading(col, text=col)
            self.arquivos_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.arquivos_tree.yview)
        self.arquivos_tree.configure(yscrollcommand=scrollbar.set)
        
        self.arquivos_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.arquivos_tree.insert('', 'end', values=('Carregando arquivos...', '', '', '', '', ''))
    
    def create_segurados_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['segurados'] = frame
        
        # Título
        title = tk.Label(frame, text="👤 Gerenciar Segurados", 
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)
        
        # Formulário
        form_frame = tk.LabelFrame(frame, text="Dados do Segurado", 
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8f9fa',
                                  padx=15,
                                  pady=15)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Campos do formulário
        fields = [
            ("Nome *", "segurado_nome", "text"),
            ("CPF *", "segurado_cpf", "number")
        ]
        
        self.segurado_fields = {}
        for i, (label, field_name, field_type) in enumerate(fields):
            field_frame = tk.Frame(form_frame, bg='#f8f9fa')
            field_frame.grid(row=0, column=i, padx=20, pady=5, sticky='w')
            
            lbl = tk.Label(field_frame, text=label, font=('Arial', 9), bg='#f8f9fa')
            lbl.pack(anchor='w')
            
            if field_type == "number":
                entry = tk.Entry(field_frame, width=25, font=('Arial', 10))
            else:
                entry = tk.Entry(field_frame, width=25, font=('Arial', 10))
            
            entry.pack(pady=2)
            self.segurado_fields[field_name] = entry
        
        # Botões
        button_frame = tk.Frame(frame, bg='white')
        button_frame.pack(pady=10, padx=20)
        
        self.btn_criar_segurado = tk.Button(button_frame,
                                           text="➕ Criar Segurado",
                                           font=('Arial', 10, 'bold'),
                                           fg='white',
                                           bg='#3498db',
                                           relief='flat',
                                           padx=15,
                                           pady=8,
                                           command=self.criar_segurado)
        self.btn_criar_segurado.pack(side='left', padx=5)
        
        tk.Button(button_frame,
                 text="🔄 Listar Segurados",
                 font=('Arial', 10, 'bold'),
                 fg='white',
                 bg='#27ae60',
                 relief='flat',
                 padx=15,
                 pady=8,
                 command=lambda: self.listar_segurados(True)).pack(side='left', padx=5)
        
        tk.Button(button_frame,
                 text="🧹 Limpar",
                 font=('Arial', 10, 'bold'),
                 fg='white',
                 bg='#f39c12',
                 relief='flat',
                 padx=15,
                 pady=8,
                 command=self.limpar_form_segurado).pack(side='left', padx=5)
        
        # Mensagens
        self.message_segurados = tk.Label(frame, text="", font=('Arial', 10), bg='white')
        self.message_segurados.pack(pady=5)
        
        # Tabela de segurados
        table_frame = tk.Frame(frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('CPF', 'Nome', 'Arquivos', 'Ações')
        self.segurados_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.segurados_tree.heading(col, text=col)
            self.segurados_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.segurados_tree.yview)
        self.segurados_tree.configure(yscrollcommand=scrollbar.set)
        
        self.segurados_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.segurados_tree.insert('', 'end', values=('Carregando segurados...', '', '', ''))
    
    def open_tab(self, tab_name):
        # Esconder todas as abas
        for frame in self.tab_frames.values():
            frame.pack_forget()
        
        # Resetar cores dos botões
        for tab in self.tabs.values():
            tab.configure(bg='#2c3e50')
        
        # Mostrar aba selecionada
        self.tab_frames[tab_name].pack(fill='both', expand=True)
        self.tabs[tab_name].configure(bg='#3498db')
        self.app_state['current_tab'] = tab_name
        
        # Carregar dados se necessário
        self.load_tab_data(tab_name)
    
    def load_tab_data(self, tab_name):
        if tab_name == 'dashboard':
            self.load_stats()
        elif tab_name == 'caixas' and not self.app_state['data']['caixas']:
            self.listar_caixas()
        elif tab_name == 'arquivos' and not self.app_state['data']['arquivos']:
            self.listar_arquivos()
        elif tab_name == 'segurados' and not self.app_state['data']['segurados']:
            self.listar_segurados()
    
    def load_initial_data(self):
        # Verificar status da API
        self.check_api_status()
        
        # Carregar dados iniciais
        self.load_stats()
        self.start_auto_refresh()
    
    def check_api_status(self):
        try:
            response = requests.get(f"{self.API_BASE}/health", timeout=5)
            if response.status_code == 200:
                self.api_status_var.set("🟢 ONLINE")
            else:
                self.api_status_var.set("🔴 OFFLINE")
        except:
            self.api_status_var.set("🔴 OFFLINE")
    
    def toggle_auto_refresh(self):
        self.app_state['auto_refresh'] = self.auto_refresh_var.get()
        if self.app_state['auto_refresh']:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        if self.app_state['refresh_interval']:
            self.root.after_cancel(self.app_state['refresh_interval'])
        
        def refresh():
            if self.app_state['auto_refresh'] and self.app_state['current_tab'] == 'dashboard':
                self.load_stats()
            self.app_state['refresh_interval'] = self.root.after(10000, refresh)
        
        self.app_state['refresh_interval'] = self.root.after(10000, refresh)
    
    def stop_auto_refresh(self):
        if self.app_state['refresh_interval']:
            self.root.after_cancel(self.app_state['refresh_interval'])
            self.app_state['refresh_interval'] = None
    
    def update_last_update_time(self):
        now = datetime.now()
        self.app_state['last_update'] = now
        time_str = now.strftime('%H:%M:%S')
        self.last_update_label.config(text=f"Última atualização: {time_str}")
    
    def show_message(self, label_widget, message, message_type='success'):
        colors = {
            'success': ('#155724', '#d4edda'),
            'error': ('#721c24', '#f8d7da'),
            'warning': ('#856404', '#fff3cd')
        }
        
        fg_color, bg_color = colors.get(message_type, colors['success'])
        label_widget.config(text=message, fg=fg_color, bg=bg_color)
        
        # Limpar mensagem após 5 segundos
        self.root.after(5000, lambda: label_widget.config(text="", bg='white'))
    
    # Funções para Caixas
    def criar_caixa(self):
        def criar_caixa_thread():
            try:
                # Desabilitar botão
                self.root.after(0, lambda: self.btn_criar_caixa.config(state='disabled', text='⏳ Criando...'))
                
                caixa_data = {
                    'codigo': int(self.caixa_fields['caixa_codigo'].get()),
                    'NBI': int(self.caixa_fields['caixa_nbi'].get()),
                    'NBF': int(self.caixa_fields['caixa_nbf'].get()),
                    'prateleira': self.caixa_fields['caixa_prateleira'].get(),
                    'bloco': self.caixa_fields['caixa_bloco'].get(),
                    'andar': self.caixa_fields['caixa_andar'].get(),
                    'corredor': self.caixa_fields['caixa_corredor'].get()
                }
                
                # Validação
                if not caixa_data['codigo'] or not caixa_data['NBI'] or not caixa_data['NBF']:
                    raise ValueError("Código, NBI e NBF são obrigatórios")
                
                # Chamada à API
                response = requests.post(
                    f"{self.API_BASE}/caixas",
                    json=caixa_data,
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "✅ Caixa criada com sucesso!"))
                    self.root.after(0, self.limpar_form_caixa)
                    self.root.after(0, lambda: self.listar_caixas(True))
                    if self.app_state['current_tab'] == 'dashboard':
                        self.root.after(0, self.load_stats)
                else:
                    error_data = response.json()
                    error_msg = error_data.get('erro', 'Erro desconhecido na API')
                    raise Exception(f"API Error {response.status_code}: {error_msg}")
                    
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_caixas, f"❌ Erro: {str(e)}", 'error'))
            finally:
                self.root.after(0, lambda: self.btn_criar_caixa.config(state='normal', text='➕ Criar Caixa'))
        
        # Executar em thread separada
        thread = threading.Thread(target=criar_caixa_thread)
        thread.daemon = True
        thread.start()
    
    def listar_caixas(self, force_refresh=False):
        def listar_caixas_thread():
            try:
                # Chamada à API
                response = requests.get(
                    f"{self.API_BASE}/caixas",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    caixas = response.json()
                    self.app_state['data']['caixas'] = caixas
                    
                    # Atualizar interface na thread principal
                    self.root.after(0, self.render_caixas, caixas)
                    self.root.after(0, self.update_last_update_time)
                else:
                    raise Exception(f"API retornou status {response.status_code}")
                    
            except Exception as e:
                self.root.after(0, self.render_caixas_error, str(e))
        
        thread = threading.Thread(target=listar_caixas_thread)
        thread.daemon = True
        thread.start()
    
    def render_caixas(self, caixas):
        # Limpar treeview
        for item in self.caixas_tree.get_children():
            self.caixas_tree.delete(item)
        
        if not caixas:
            self.caixas_tree.insert('', 'end', values=('Nenhuma caixa cadastrada', '', '', '', ''))
            return
        
        # Adicionar dados
        for caixa in caixas:
            localizacao = f"{caixa.get('prateleira', '-')}/{caixa.get('bloco', '-')}/{caixa.get('andar', '-')}"
            self.caixas_tree.insert('', 'end', values=(
                caixa.get('codigo', ''),
                caixa.get('NBI', ''),
                caixa.get('NBF', ''),
                localizacao,
                "✏️ 🗑️"
            ))
    
    def render_caixas_error(self, error_msg):
        for item in self.caixas_tree.get_children():
            self.caixas_tree.delete(item)
        self.caixas_tree.insert('', 'end', values=(f'❌ Erro: {error_msg}', '', '', '', ''))
    
    def limpar_form_caixa(self):
        for field in self.caixa_fields.values():
            field.delete(0, tk.END)
    
    # Funções para Arquivos
    def criar_arquivo(self):
        def criar_arquivo_thread():
            try:
                self.root.after(0, lambda: self.btn_criar_arquivo.config(state='disabled', text='⏳ Criando...'))
                
                arquivo_data = {
                    'NB': int(self.arquivo_fields['arquivo_nb'].get()),
                    'APS': self.arquivo_fields['arquivo_aps'].get(),
                    'SeguradoFK': int(self.arquivo_fields['arquivo_seguradofk'].get()),
                    'Tipo': int(self.arquivo_fields['arquivo_tipo'].get()),
                    'Caixa_codigo': int(self.arquivo_fields['arquivo_caixa'].get())
                }
                
                # Validação
                required_fields = ['NB', 'APS', 'SeguradoFK', 'Tipo', 'Caixa_codigo']
                for field in required_fields:
                    if not arquivo_data[field]:
                        raise ValueError("Todos os campos são obrigatórios")
                
                # Chamada à API
                response = requests.post(
                    f"{self.API_BASE}/arquivos",
                    json=arquivo_data,
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    self.root.after(0, lambda: self.show_message(self.message_arquivos, "✅ Arquivo criado com sucesso!"))
                    self.root.after(0, self.limpar_form_arquivo)
                    self.root.after(0, lambda: self.listar_arquivos(True))
                    if self.app_state['current_tab'] == 'dashboard':
                        self.root.after(0, self.load_stats)
                else:
                    error_data = response.json()
                    error_msg = error_data.get('erro', 'Erro desconhecido na API')
                    raise Exception(f"API Error {response.status_code}: {error_msg}")
                    
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_arquivos, f"❌ Erro: {str(e)}", 'error'))
            finally:
                self.root.after(0, lambda: self.btn_criar_arquivo.config(state='normal', text='➕ Criar Arquivo'))
        
        thread = threading.Thread(target=criar_arquivo_thread)
        thread.daemon = True
        thread.start()
    
    def listar_arquivos(self, force_refresh=False):
        def listar_arquivos_thread():
            try:
                response = requests.get(
                    f"{self.API_BASE}/arquivos",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    arquivos = response.json()
                    self.app_state['data']['arquivos'] = arquivos
                    self.root.after(0, self.render_arquivos, arquivos)
                    self.root.after(0, self.update_last_update_time)
                else:
                    raise Exception(f"API retornou status {response.status_code}")
                    
            except Exception as e:
                self.root.after(0, self.render_arquivos_error, str(e))
        
        thread = threading.Thread(target=listar_arquivos_thread)
        thread.daemon = True
        thread.start()
    
    def render_arquivos(self, arquivos):
        for item in self.arquivos_tree.get_children():
            self.arquivos_tree.delete(item)
        
        if not arquivos:
            self.arquivos_tree.insert('', 'end', values=('Nenhum arquivo cadastrado', '', '', '', '', ''))
            return
        
        for arquivo in arquivos:
            self.arquivos_tree.insert('', 'end', values=(
                arquivo.get('NB', ''),
                arquivo.get('APS', ''),
                arquivo.get('SeguradoFK', ''),
                arquivo.get('Tipo', ''),
                arquivo.get('Caixa_codigo', ''),
                "✏️ 🗑️"
            ))
    
    def render_arquivos_error(self, error_msg):
        for item in self.arquivos_tree.get_children():
            self.arquivos_tree.delete(item)
        self.arquivos_tree.insert('', 'end', values=(f'❌ Erro: {error_msg}', '', '', '', '', ''))
    
    def limpar_form_arquivo(self):
        for field in self.arquivo_fields.values():
            field.delete(0, tk.END)
    
    # Funções para Segurados
    def criar_segurado(self):
        def criar_segurado_thread():
            try:
                self.root.after(0, lambda: self.btn_criar_segurado.config(state='disabled', text='⏳ Criando...'))
                
                segurado_data = {
                    'Nome': self.segurado_fields['segurado_nome'].get(),
                    'cpf': int(self.segurado_fields['segurado_cpf'].get())
                }
                
                if not segurado_data['Nome'] or not segurado_data['cpf']:
                    raise ValueError("Nome e CPF são obrigatórios")
                
                # Chamada à API
                response = requests.post(
                    f"{self.API_BASE}/segurados",
                    json=segurado_data,
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    self.root.after(0, lambda: self.show_message(self.message_segurados, "✅ Segurado criado com sucesso!"))
                    self.root.after(0, self.limpar_form_segurado)
                    self.root.after(0, lambda: self.listar_segurados(True))
                    if self.app_state['current_tab'] == 'dashboard':
                        self.root.after(0, self.load_stats)
                else:
                    error_data = response.json()
                    error_msg = error_data.get('erro', 'Erro desconhecido na API')
                    
                    # Tratar erro de CPF duplicado especificamente
                    if 'duplicate' in error_msg.lower() or 'duplicado' in error_msg.lower():
                        raise Exception("CPF já cadastrado no sistema")
                    else:
                        raise Exception(f"API Error {response.status_code}: {error_msg}")
                    
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_segurados, f"❌ Erro: {str(e)}", 'error'))
            finally:
                self.root.after(0, lambda: self.btn_criar_segurado.config(state='normal', text='➕ Criar Segurado'))
        
        thread = threading.Thread(target=criar_segurado_thread)
        thread.daemon = True
        thread.start()
    
    def listar_segurados(self, force_refresh=False):
        def listar_segurados_thread():
            try:
                response = requests.get(
                    f"{self.API_BASE}/segurados",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    segurados = response.json()
                    self.app_state['data']['segurados'] = segurados
                    self.root.after(0, self.render_segurados, segurados)
                    self.root.after(0, self.update_last_update_time)
                else:
                    raise Exception(f"API retornou status {response.status_code}")
                    
            except Exception as e:
                self.root.after(0, self.render_segurados_error, str(e))
        
        thread = threading.Thread(target=listar_segurados_thread)
        thread.daemon = True
        thread.start()
    
    def render_segurados(self, segurados):
        for item in self.segurados_tree.get_children():
            self.segurados_tree.delete(item)
        
        if not segurados:
            self.segurados_tree.insert('', 'end', values=('Nenhum segurado cadastrado', '', '', ''))
            return
        
        for segurado in segurados:
            num_arquivos = len(segurado.get('Arquivos', [])) if isinstance(segurado.get('Arquivos'), list) else 0
            self.segurados_tree.insert('', 'end', values=(
                segurado.get('cpf', ''),
                segurado.get('Nome', ''),
                num_arquivos,
                "✏️ 🗑️"
            ))
    
    def render_segurados_error(self, error_msg):
        for item in self.segurados_tree.get_children():
            self.segurados_tree.delete(item)
        self.segurados_tree.insert('', 'end', values=(f'❌ Erro: {error_msg}', '', '', ''))
    
    def limpar_form_segurado(self):
        for field in self.segurado_fields.values():
            field.delete(0, tk.END)
    
    # Funções do Dashboard
    def load_stats(self, force=False):
        def load_stats_thread():
            try:
                response = requests.get(
                    f"{self.API_BASE}/info",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    info = response.json()
                    self.root.after(0, self.render_stats, info)
                    
                    # Atualizar status
                    self.root.after(0, lambda: self.mongo_status_var.set(
                        "🟢 ONLINE" if info.get('status_banco_dados', {}).get('mongodb') else "🔴 OFFLINE"
                    ))
                    self.root.after(0, lambda: self.json_status_var.set(
                        "🟢 ONLINE" if info.get('status_banco_dados', {}).get('json') else "🔴 OFFLINE"
                    ))
                    
                    total = sum(info.get('estatisticas', {}).values())
                    self.root.after(0, lambda: self.total_items_var.set(str(total)))
                    
                    self.root.after(0, self.update_last_update_time)
                else:
                    raise Exception(f"API retornou status {response.status_code}")
                    
            except Exception as e:
                self.root.after(0, self.render_stats_error, str(e))
        
        thread = threading.Thread(target=load_stats_thread)
        thread.daemon = True
        thread.start()
    
    def render_stats(self, info):
        self.stats_placeholder.pack_forget()
        
        # Criar cards de estatísticas
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        stats = info.get('estatisticas', {})
        stats_cards = [
            ("📦 Caixas", stats.get('caixas', 0)),
            ("📁 Arquivos", stats.get('arquivos', 0)),
            ("👤 Segurados", stats.get('segurados', 0)),
            ("🕐 Uptime", info.get('uptime', 'N/A'))
        ]
        
        for i, (title, value) in enumerate(stats_cards):
            card = tk.Frame(self.stats_frame, bg='white', relief='raised', bd=1)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            
            title_label = tk.Label(card, text=title, font=('Arial', 12, 'bold'), bg='white')
            title_label.pack(pady=(15, 5))
            
            value_label = tk.Label(card, text=str(value), font=('Arial', 24, 'bold'), 
                                  fg='#3498db', bg='white')
            value_label.pack(pady=(5, 15))
        
        # Configurar grid
        for i in range(4):
            self.stats_frame.columnconfigure(i, weight=1)
    
    def render_stats_error(self, error_msg):
        self.stats_placeholder.config(text=f"❌ Erro ao carregar estatísticas: {error_msg}")
        self.stats_placeholder.pack()
    
    def test_api(self):
        def test_api_thread():
            try:
                response = requests.get(f"{self.API_BASE}/health", timeout=5)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "✅ API está funcionando corretamente!"))
                else:
                    raise Exception("API retornou erro")
            except:
                self.root.after(0, lambda: self.show_message(self.message_caixas, "❌ API não está respondendo!", 'error'))
        
        thread = threading.Thread(target=test_api_thread)
        thread.daemon = True
        thread.start()
    
    def forcar_atualizacao(self):
        def forcar_atualizacao_thread():
            try:
                response = requests.post(
                    f"{self.API_BASE}/refresh",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "✅ Sincronização forçada com sucesso!"))
                    
                    # Recarregar dados
                    if self.app_state['current_tab'] == 'dashboard':
                        self.root.after(0, lambda: self.load_stats(True))
                    else:
                        self.root.after(0, lambda: self.load_tab_data(self.app_state['current_tab']))
                else:
                    raise Exception("Falha na sincronização")
                    
            except:
                self.root.after(0, lambda: self.show_message(self.message_caixas, "❌ Erro na sincronização", 'error'))
        
        thread = threading.Thread(target=forcar_atualizacao_thread)
        thread.daemon = True
        thread.start()
    
    def clear_all_data(self):
        if not messagebox.askyesno("Confirmação", "⚠️ ATENÇÃO: Isso irá deletar TODOS os dados! Tem certeza?"):
            return
        
        def clear_all_data_thread():
            try:
                response = requests.post(
                    f"{self.API_BASE}/limpar",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    # Limpar estado local
                    self.app_state['data'] = {'caixas': [], 'arquivos': [], 'segurados': []}
                    
                    # Recarregar tudo
                    self.root.after(0, lambda: self.load_stats(True))
                    self.root.after(0, lambda: self.listar_caixas(True))
                    self.root.after(0, lambda: self.listar_arquivos(True))
                    self.root.after(0, lambda: self.listar_segurados(True))
                    
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "✅ Todos os dados foram limpos com sucesso!"))
                else:
                    raise Exception("Falha ao limpar dados")
                    
            except:
                self.root.after(0, lambda: self.show_message(self.message_caixas, "❌ Erro ao limpar dados", 'error'))
        
        thread = threading.Thread(target=clear_all_data_thread)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = GCAApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()