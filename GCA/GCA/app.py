import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import threading
from datetime import datetime
import time
import base64
import webbrowser
from tkinter import filedialog
import csv
import os
import tempfile
from relatorios import GeradorRelatorios

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

        # Inicializar gerador de relatórios
        self.gerador_relatorios = GeradorRelatorios()

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

    # -------------------------
    # UI: criação de widgets
    # -------------------------
    def create_widgets(self):
        self.main_container = tk.Frame(self.root, bg='white', bd=0, relief='flat')
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)

        self.create_header()
        self.create_status_bar()
        self.create_tabs()
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

    def create_tab_content(self):
        self.content_frame = tk.Frame(self.main_container, bg='white')
        self.content_frame.pack(fill='both', expand=True)

        self.tab_frames = {}

        self.create_dashboard_tab()
        self.create_busca_tab()
        self.create_caixas_tab()
        self.create_arquivos_tab()
        self.create_segurados_tab()
        self.create_relatorios_tab()

        self.tab_frames['dashboard'].pack(fill='both', expand=True)

    # -------------------------
    # Dashboard
    # -------------------------
    def create_dashboard_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['dashboard'] = frame

        title = tk.Label(frame, text="📊 Dashboard do Sistema",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

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

        self.stats_frame = tk.Frame(frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=20)

        self.stats_placeholder = tk.Label(self.stats_frame,
                                         text="Carregando estatísticas...",
                                         font=('Arial', 12),
                                         bg='white')
        self.stats_placeholder.pack()

        self.last_update_frame = tk.Frame(frame, bg='white')
        self.last_update_frame.pack(pady=10)

        self.last_update_label = tk.Label(self.last_update_frame,
                                         text="Última atualização: --:--:--",
                                         font=('Arial', 10),
                                         fg='#6c757d',
                                         bg='white')
        self.last_update_label.pack()

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

    # -------------------------
    # Busca Avançada
    # -------------------------
    def create_busca_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['busca'] = frame

        title = tk.Label(frame, text="🔍 Busca Avançada",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        filter_frame = tk.LabelFrame(frame, text="Filtros de Busca",
                                   font=('Arial', 11, 'bold'),
                                   bg='#f8f9fa',
                                   padx=15,
                                   pady=15)
        filter_frame.pack(fill='x', padx=20, pady=10)

        type_frame = tk.Frame(filter_frame, bg='#f8f9fa')
        type_frame.pack(fill='x', pady=5)

        tk.Label(type_frame, text="Tipo:", font=('Arial', 9), bg='#f8f9fa').pack(side='left')

        self.busca_tipo_var = tk.StringVar(value="todos")
        tipos = [
            ("Todos", "todos"),
            ("Caixas", "caixas"),
            ("Arquivos", "arquivos"),
            ("Segurados", "segurados")
        ]

        for text, value in tipos:
            rb = tk.Radiobutton(type_frame, text=text, variable=self.busca_tipo_var,
                               value=value, bg='#f8f9fa', font=('Arial', 9))
            rb.pack(side='left', padx=10)

        fields_frame = tk.Frame(filter_frame, bg='#f8f9fa')
        fields_frame.pack(fill='x', pady=10)

        row1 = tk.Frame(fields_frame, bg='#f8f9fa')
        row1.pack(fill='x', pady=5)

        tk.Label(row1, text="Código/NB/CPF:", font=('Arial', 9), bg='#f8f9fa').pack(side='left')
        self.busca_codigo = tk.Entry(row1, width=15, font=('Arial', 10))
        self.busca_codigo.pack(side='left', padx=5)

        tk.Label(row1, text="Nome/APS:", font=('Arial', 9), bg='#f8f9fa').pack(side='left', padx=(20,0))
        self.busca_nome = tk.Entry(row1, width=20, font=('Arial', 10))
        self.busca_nome.pack(side='left', padx=5)

        row2 = tk.Frame(fields_frame, bg='#f8f9fa')
        row2.pack(fill='x', pady=5)

        tk.Label(row2, text="Localização:", font=('Arial', 9), bg='#f8f9fa').pack(side='left')
        self.busca_localizacao = tk.Entry(row2, width=15, font=('Arial', 10))
        self.busca_localizacao.pack(side='left', padx=5)

        tk.Label(row2, text="Tipo Arquivo:", font=('Arial', 9), bg='#f8f9fa').pack(side='left', padx=(20,0))
        self.busca_tipo_arquivo = tk.Entry(row2, width=10, font=('Arial', 10))
        self.busca_tipo_arquivo.pack(side='left', padx=5)

        button_frame = tk.Frame(frame, bg='white')
        button_frame.pack(pady=10, padx=20)

        tk.Button(button_frame,
                 text="🔍 Buscar",
                 font=('Arial', 10, 'bold'),
                 fg='white',
                 bg='#3498db',
                 relief='flat',
                 padx=20,
                 pady=8,
                 command=self.executar_busca).pack(side='left', padx=5)

        tk.Button(button_frame,
                 text="🧹 Limpar Filtros",
                 font=('Arial', 10, 'bold'),
                 fg='white',
                 bg='#f39c12',
                 relief='flat',
                 padx=15,
                 pady=8,
                 command=self.limpar_filtros_busca).pack(side='left', padx=5)

        tk.Button(button_frame,
                 text="📋 Exportar Resultados",
                 font=('Arial', 10, 'bold'),
                 fg='white',
                 bg='#27ae60',
                 relief='flat',
                 padx=15,
                 pady=8,
                 command=self.exportar_resultados_busca).pack(side='left', padx=5)

        self.message_busca = tk.Label(frame, text="", font=('Arial', 10), bg='white')
        self.message_busca.pack(pady=5)

        results_frame = tk.LabelFrame(frame, text="Resultados da Busca",
                                    font=('Arial', 11, 'bold'),
                                    bg='white',
                                    padx=15,
                                    pady=15)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('Tipo', 'Código/NB/CPF', 'Descrição', 'Localização', 'Detalhes')
        self.busca_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=12)

        for col in columns:
            self.busca_tree.heading(col, text=col)
            self.busca_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.busca_tree.yview)
        self.busca_tree.configure(yscrollcommand=scrollbar.set)

        self.busca_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.busca_tree.insert('', 'end', values=('Digite os critérios e clique em Buscar', '', '', '', ''))

        self.resultados_count = tk.Label(results_frame, text="Nenhuma busca realizada",
                                        font=('Arial', 10), bg='white', fg='#6c757d')
        self.resultados_count.pack(side='bottom', fill='x')

    # -------------------------
    # Relatórios tab
    # -------------------------
    def create_relatorios_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['relatorios'] = frame

        title = tk.Label(frame, text="📋 Relatórios do Sistema",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        reports_frame = tk.Frame(frame, bg='white')
        reports_frame.pack(fill='both', expand=True, padx=20, pady=10)

        relatorios = [
            {"titulo": "📦 Relatório de Caixas", "descricao": "Lista completa de todas as caixas cadastradas", "tipo": "caixas", "cor": "#3498db"},
            {"titulo": "📁 Relatório de Arquivos", "descricao": "Relatório detalhado de arquivos por tipo e localização", "tipo": "arquivos", "cor": "#27ae60"},
            {"titulo": "👤 Relatório de Segurados", "descricao": "Lista de segurados e seus arquivos associados", "tipo": "segurados", "cor": "#e74c3c"},
            {"titulo": "📊 Relatório Completo", "descricao": "Relatório geral com todos os dados do sistema", "tipo": "completo", "cor": "#f39c12"}
        ]

        for i, relatorio in enumerate(relatorios):
            row = i // 2
            col = i % 2

            card = tk.Frame(reports_frame, bg='#f8f9fa', relief='raised', bd=1)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

            title_label = tk.Label(card, text=relatorio["titulo"],
                                 font=('Arial', 14, 'bold'),
                                 fg=relatorio["cor"], bg='#f8f9fa')
            title_label.pack(pady=(15, 5), padx=15, anchor='w')

            desc_label = tk.Label(card, text=relatorio["descricao"],
                                font=('Arial', 10),
                                fg='#6c757d', bg='#f8f9fa', wraplength=250)
            desc_label.pack(pady=5, padx=15, anchor='w')

            btn_frame = tk.Frame(card, bg='#f8f9fa')
            btn_frame.pack(pady=10, padx=15, fill='x')

            tk.Button(btn_frame,
                     text="📄 Gerar PDF",
                     font=('Arial', 9, 'bold'),
                     fg='white',
                     bg=relatorio["cor"],
                     relief='flat',
                     padx=10,
                     pady=5,
                     command=lambda t=relatorio["tipo"]: self.gerar_relatorio_pdf(t)).pack(side='left', padx=2)

            tk.Button(btn_frame,
                     text="📊 Gerar Excel",
                     font=('Arial', 9, 'bold'),
                     fg='white',
                     bg=relatorio["cor"],
                     relief='flat',
                     padx=10,
                     pady=5,
                     command=lambda t=relatorio["tipo"]: self.gerar_relatorio_excel(t)).pack(side='left', padx=2)

            tk.Button(btn_frame,
                     text="👁️ Visualizar",
                     font=('Arial', 9, 'bold'),
                     fg='white',
                     bg=relatorio["cor"],
                     relief='flat',
                     padx=10,
                     pady=5,
                     command=lambda t=relatorio["tipo"]: self.visualizar_relatorio(t)).pack(side='left', padx=2)

        reports_frame.columnconfigure(0, weight=1)
        reports_frame.columnconfigure(1, weight=1)
        reports_frame.rowconfigure(0, weight=1)
        reports_frame.rowconfigure(1, weight=1)

        preview_frame = tk.LabelFrame(frame, text="Visualização do Relatório",
                                    font=('Arial', 11, 'bold'),
                                    bg='white',
                                    padx=15,
                                    pady=15)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.relatorio_text = scrolledtext.ScrolledText(preview_frame,
                                                       wrap=tk.WORD,
                                                       width=80,
                                                       height=15,
                                                       font=('Arial', 10))
        self.relatorio_text.pack(fill='both', expand=True)
        self.relatorio_text.insert('1.0', "Selecione um relatório para visualizar...")
        self.relatorio_text.config(state='disabled')

    # -------------------------
    # Caixas tab
    # -------------------------
    def create_caixas_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['caixas'] = frame

        title = tk.Label(frame, text="📦 Gerenciar Caixas",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        form_frame = tk.LabelFrame(frame, text="Dados da Caixa",
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8f9fa',
                                  padx=15,
                                  pady=15)
        form_frame.pack(fill='x', padx=20, pady=10)

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

            entry = tk.Entry(field_frame, width=15, font=('Arial', 10))
            entry.pack(pady=2)
            self.caixa_fields[field_name] = entry

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

        self.message_caixas = tk.Label(frame, text="", font=('Arial', 10), bg='white')
        self.message_caixas.pack(pady=5)

        table_frame = tk.Frame(frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('Código', 'NBI', 'NBF', 'Localização', 'Ações')
        self.caixas_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        for col in columns:
            self.caixas_tree.heading(col, text=col)
            self.caixas_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.caixas_tree.yview)
        self.caixas_tree.configure(yscrollcommand=scrollbar.set)

        self.caixas_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.caixas_tree.bind('<ButtonRelease-1>', self.on_caixa_click)

        self.caixas_tree.insert('', 'end', values=('Carregando caixas...', '', '', '', ''))

    # -------------------------
    # Arquivos tab
    # -------------------------
    def create_arquivos_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['arquivos'] = frame

        title = tk.Label(frame, text="📁 Gerenciar Arquivos",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        form_frame = tk.LabelFrame(frame, text="Dados do Arquivo",
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8f9fa',
                                  padx=15,
                                  pady=15)
        form_frame.pack(fill='x', padx=20, pady=10)

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

        self.message_arquivos = tk.Label(frame, text="", font=('Arial', 10), bg='white')
        self.message_arquivos.pack(pady=5)

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

        self.arquivos_tree.bind('<ButtonRelease-1>', self.on_arquivo_click)

        self.arquivos_tree.insert('', 'end', values=('Carregando arquivos...', '', '', '', '', ''))

    # -------------------------
    # Segurados tab
    # -------------------------
    def create_segurados_tab(self):
        frame = tk.Frame(self.content_frame, bg='white')
        self.tab_frames['segurados'] = frame

        title = tk.Label(frame, text="👤 Gerenciar Segurados",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        form_frame = tk.LabelFrame(frame, text="Dados do Segurado",
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8f9fa',
                                  padx=15,
                                  pady=15)
        form_frame.pack(fill='x', padx=20, pady=10)

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

            entry = tk.Entry(field_frame, width=25, font=('Arial', 10))
            entry.pack(pady=2)
            self.segurado_fields[field_name] = entry

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

        self.message_segurados = tk.Label(frame, text="", font=('Arial', 10), bg='white')
        self.message_segurados.pack(pady=5)

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

        self.segurados_tree.bind('<ButtonRelease-1>', self.on_segurado_click)

        self.segurados_tree.insert('', 'end', values=('Carregando segurados...', '', '', ''))

    # -------------------------
    # Navegação e carregamento
    # -------------------------
    def open_tab(self, tab_name):
        for frame in self.tab_frames.values():
            frame.pack_forget()

        for tab in self.tabs.values():
            tab.configure(bg='#2c3e50')

        self.tab_frames[tab_name].pack(fill='both', expand=True)
        self.tabs[tab_name].configure(bg='#3498db')
        self.app_state['current_tab'] = tab_name

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
        elif tab_name == 'busca':
            self.limpar_filtros_busca()

    def load_initial_data(self):
        self.check_api_status()
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

    # -------------------------
    # Auto-refresh
    # -------------------------
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
            try:
                if self.app_state['auto_refresh'] and self.app_state['current_tab'] == 'dashboard':
                    self.load_stats()
            except Exception:
                pass
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

        self.root.after(5000, lambda: label_widget.config(text="", bg='white'))

    # -------------------------
    # Helpers: normalização
    # -------------------------
    def _normalize_item_to_dict(self, item, kind='arquivo'):
        """
        Garante que 'item' seja um dict com as chaves mínimas esperadas.
        Se 'item' for str, converte para dict com o valor colocado em um campo apropriado.
        kind: 'arquivo' | 'caixa' | 'segurado' para definir campos padrão.
        """
        if isinstance(item, dict):
            return item
        if isinstance(item, (int, float)):
            item = str(item)
        if isinstance(item, str):
            if kind == 'arquivo':
                return {'NB': item}
            if kind == 'caixa':
                return {'codigo': item}
            if kind == 'segurado':
                return {'cpf': item}
        # fallback
        return {'id': str(item), 'raw': str(item)}

    def _normalize_list(self, lst, kind):
        """
        Converte lista possivelmente contendo strings/dicts em lista de dicts.
        """
        if not isinstance(lst, list):
            return []
        normalized = []
        for it in lst:
            try:
                d = self._normalize_item_to_dict(it, kind=kind)
            except Exception:
                d = {'raw': str(it)}
            normalized.append(d)
        return normalized

    # -------------------------
    # Busca Avançada (threaded)
    # -------------------------
    def executar_busca(self):
        def buscar_thread():
            try:
                criterios = {
                    'tipo': self.busca_tipo_var.get(),
                    'codigo': self.busca_codigo.get().strip(),
                    'nome': self.busca_nome.get().strip(),
                    'localizacao': self.busca_localizacao.get().strip(),
                    'tipo_arquivo': self.busca_tipo_arquivo.get().strip()
                }

                resultados = []

                if criterios['tipo'] in ['todos', 'caixas']:
                    response = requests.get(f"{self.API_BASE}/caixas", headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        caixas = response.json()
                        caixas = self._normalize_list(caixas if isinstance(caixas, list) else [], kind='caixa')
                        for caixa in caixas:
                            if self.filtrar_caixa(caixa, criterios):
                                resultados.append({
                                    'tipo': 'Caixa',
                                    'codigo': caixa.get('codigo', ''),
                                    'descricao': f"NBI: {caixa.get('NBI', '')} | NBF: {caixa.get('NBF', '')}",
                                    'localizacao': f"{caixa.get('prateleira', '')}/{caixa.get('bloco', '')}/{caixa.get('andar', '')}",
                                    'detalhes': f"Corredor: {caixa.get('corredor', '')}"
                                })

                if criterios['tipo'] in ['todos', 'arquivos']:
                    response = requests.get(f"{self.API_BASE}/arquivos", headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        arquivos = response.json()
                        arquivos = self._normalize_list(arquivos if isinstance(arquivos, list) else [], kind='arquivo')
                        for arquivo in arquivos:
                            if self.filtrar_arquivo(arquivo, criterios):
                                resultados.append({
                                    'tipo': 'Arquivo',
                                    'codigo': arquivo.get('NB', arquivo.get('id', '')),
                                    'descricao': f"APS: {arquivo.get('APS', '')} | Tipo: {arquivo.get('Tipo', '')}",
                                    'localizacao': f"Caixa: {arquivo.get('Caixa_codigo', '')}",
                                    'detalhes': f"Segurado: {arquivo.get('SeguradoFK', '')}"
                                })

                if criterios['tipo'] in ['todos', 'segurados']:
                    response = requests.get(f"{self.API_BASE}/segurados", headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        segurados = response.json()
                        segurados = self._normalize_list(segurados if isinstance(segurados, list) else [], kind='segurado')
                        for segurado in segurados:
                            if self.filtrar_segurado(segurado, criterios):
                                num_arquivos = len(segurado.get('Arquivos', [])) if isinstance(segurado.get('Arquivos'), list) else 0
                                resultados.append({
                                    'tipo': 'Segurado',
                                    'codigo': segurado.get('cpf', segurado.get('id', '')),
                                    'descricao': f"Nome: {segurado.get('Nome', '')}",
                                    'localizacao': f"Arquivos: {num_arquivos}",
                                    'detalhes': f"Total de arquivos: {num_arquivos}"
                                })

                self.root.after(0, self.render_resultados_busca, resultados)

            except Exception as error:
                error_message = str(error)
                self.root.after(0, lambda msg=error_message: self.show_message(self.message_busca, f"❌ Erro na busca: {msg}", 'error'))

        thread = threading.Thread(target=buscar_thread)
        thread.daemon = True
        thread.start()

    def filtrar_caixa(self, caixa, criterios):
        codigo = str(caixa.get('codigo', '') or '')
        if criterios['codigo'] and criterios['codigo'] not in codigo:
            return False

        if criterios['localizacao']:
            li = f"{caixa.get('prateleira', '')}{caixa.get('bloco', '')}{caixa.get('andar', '')}{caixa.get('corredor', '')}"
            if criterios['localizacao'] not in li:
                return False
        return True

    def filtrar_arquivo(self, arquivo, criterios):
        nb = str(arquivo.get('NB', '') or arquivo.get('id', ''))
        if criterios['codigo'] and criterios['codigo'] not in nb:
            return False

        if criterios['nome'] and criterios['nome'] not in str(arquivo.get('APS', '')):
            return False

        if criterios['tipo_arquivo'] and criterios['tipo_arquivo'] not in str(arquivo.get('Tipo', '')):
            return False

        return True

    def filtrar_segurado(self, segurado, criterios):
        cpf = str(segurado.get('cpf', segurado.get('id', '')) or '')
        if criterios['codigo'] and criterios['codigo'] not in cpf:
            return False

        if criterios['nome'] and criterios['nome'].lower() not in str(segurado.get('Nome', '')).lower():
            return False

        return True

    def render_resultados_busca(self, resultados):
        for item in self.busca_tree.get_children():
            self.busca_tree.delete(item)

        if not resultados:
            self.busca_tree.insert('', 'end', values=('Nenhum resultado encontrado', '', '', '', ''))
            self.resultados_count.config(text="Nenhum resultado encontrado")
            return

        for resultado in resultados:
            self.busca_tree.insert('', 'end', values=(
                resultado.get('tipo', ''),
                resultado.get('codigo', ''),
                resultado.get('descricao', ''),
                resultado.get('localizacao', ''),
                resultado.get('detalhes', '')
            ))

        self.resultados_count.config(text=f"Encontrados {len(resultados)} resultado(s)")

    def limpar_filtros_busca(self):
        self.busca_codigo.delete(0, tk.END)
        self.busca_nome.delete(0, tk.END)
        self.busca_localizacao.delete(0, tk.END)
        self.busca_tipo_arquivo.delete(0, tk.END)
        self.busca_tipo_var.set("todos")

        for item in self.busca_tree.get_children():
            self.busca_tree.delete(item)

        self.busca_tree.insert('', 'end', values=('Digite os critérios e clique em Buscar', '', '', '', ''))
        self.resultados_count.config(text="Nenhuma busca realizada")
        self.message_busca.config(text="")

    def exportar_resultados_busca(self):
        items = self.busca_tree.get_children()
        if not items or 'Nenhum' in self.busca_tree.item(items[0])['values'][0]:
            self.show_message(self.message_busca, "❌ Nenhum dado para exportar", 'warning')
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Salvar resultados como"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Tipo', 'Código/NB/CPF', 'Descrição', 'Localização', 'Detalhes'])

                for item in items:
                    values = self.busca_tree.item(item)['values']
                    writer.writerow(values)

            self.show_message(self.message_busca, f"✅ Resultados exportados para {filename}")
        except Exception as error:
            error_message = str(error)
            self.show_message(self.message_busca, f"❌ Erro ao exportar: {error_message}", 'error')

    # -------------------------
    # Métodos de limpeza de formulários (ADICIONADOS)
    # -------------------------
    def limpar_form_caixa(self):
        """Limpa todos os campos do formulário de caixas"""
        for field in self.caixa_fields.values():
            field.delete(0, tk.END)
        self.message_caixas.config(text="")

    def limpar_form_arquivo(self):
        """Limpa todos os campos do formulário de arquivos"""
        for field in self.arquivo_fields.values():
            field.delete(0, tk.END)
        self.message_arquivos.config(text="")

    def limpar_form_segurado(self):
        """Limpa todos os campos do formulário de segurados"""
        for field in self.segurado_fields.values():
            field.delete(0, tk.END)
        self.message_segurados.config(text="")

    # -------------------------
    # Métodos de renderização de estatísticas (ADICIONADOS)
    # -------------------------
    def render_stats(self, info):
        """Renderiza as estatísticas no dashboard"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = info.get('estatisticas', {})
        
        # Criar cards de estatísticas
        stats_cards = [
            ("📦 Caixas", stats.get('caixas', 0), '#3498db'),
            ("📁 Arquivos", stats.get('arquivos', 0), '#27ae60'),
            ("👤 Segurados", stats.get('segurados', 0), '#e74c3c'),
            ("📊 Total", sum(stats.values()) if isinstance(stats, dict) else 0, '#f39c12')
        ]

        for i, (title, value, color) in enumerate(stats_cards):
            card = tk.Frame(self.stats_frame, bg=color, relief='raised', bd=1)
            card.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')

            title_label = tk.Label(card, text=title,
                                 font=('Arial', 12, 'bold'),
                                 fg='white', bg=color)
            title_label.pack(pady=(10, 5))

            value_label = tk.Label(card, text=str(value),
                                 font=('Arial', 24, 'bold'),
                                 fg='white', bg=color)
            value_label.pack(pady=(5, 10))

        # Configurar grid
        for i in range(4):
            self.stats_frame.columnconfigure(i, weight=1)

    def render_stats_error(self, msg):
        """Renderiza mensagem de erro no dashboard"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        error_label = tk.Label(self.stats_frame,
                              text=f"❌ Erro ao carregar estatísticas: {msg}",
                              font=('Arial', 12),
                              fg='#e74c3c',
                              bg='white')
        error_label.pack(pady=20)

    # -------------------------
    # Métodos de relatórios (ADICIONADOS)
    # -------------------------
    def visualizar_relatorio(self, tipo):
        """Visualiza o relatório na área de preview"""
        try:
            self.relatorio_text.config(state='normal')
            self.relatorio_text.delete('1.0', tk.END)
            
            if tipo == 'caixas':
                dados = self.app_state['data']['caixas']
                conteudo = "RELATÓRIO DE CAIXAS\n\n"
                for caixa in dados:
                    conteudo += f"Código: {caixa.get('codigo', '')} | NBI: {caixa.get('NBI', '')} | NBF: {caixa.get('NBF', '')}\n"
                    conteudo += f"Localização: {caixa.get('prateleira', '')}/{caixa.get('bloco', '')}/{caixa.get('andar', '')}\n"
                    conteudo += f"Corredor: {caixa.get('corredor', '')}\n"
                    conteudo += "-" * 50 + "\n"
                    
            elif tipo == 'arquivos':
                dados = self.app_state['data']['arquivos']
                conteudo = "RELATÓRIO DE ARQUIVOS\n\n"
                for arquivo in dados:
                    conteudo += f"NB: {arquivo.get('NB', '')} | APS: {arquivo.get('APS', '')}\n"
                    conteudo += f"Tipo: {arquivo.get('Tipo', '')} | Caixa: {arquivo.get('Caixa_codigo', '')}\n"
                    conteudo += f"Segurado: {arquivo.get('SeguradoFK', '')}\n"
                    conteudo += "-" * 50 + "\n"
                    
            elif tipo == 'segurados':
                dados = self.app_state['data']['segurados']
                conteudo = "RELATÓRIO DE SEGURADOS\n\n"
                for segurado in dados:
                    conteudo += f"CPF: {segurado.get('cpf', '')} | Nome: {segurado.get('Nome', '')}\n"
                    conteudo += f"Total de Arquivos: {len(segurado.get('Arquivos', []))}\n"
                    conteudo += "-" * 50 + "\n"
                    
            elif tipo == 'completo':
                conteudo = "RELATÓRIO COMPLETO DO SISTEMA\n\n"
                conteudo += f"Total de Caixas: {len(self.app_state['data']['caixas'])}\n"
                conteudo += f"Total de Arquivos: {len(self.app_state['data']['arquivos'])}\n"
                conteudo += f"Total de Segurados: {len(self.app_state['data']['segurados'])}\n\n"
                
            self.relatorio_text.insert('1.0', conteudo)
            self.relatorio_text.config(state='disabled')
            
        except Exception as e:
            self.relatorio_text.config(state='normal')
            self.relatorio_text.delete('1.0', tk.END)
            self.relatorio_text.insert('1.0', f"Erro ao gerar visualização: {str(e)}")
            self.relatorio_text.config(state='disabled')

    def gerar_relatorio_pdf(self, tipo):
        def gerar_thread():
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    title=f"Salvar relatório {tipo} como"
                )
                if not filename:
                    return
                self.root.after(0, lambda: self.show_message(self.message_busca, f"⏳ Gerando relatório {tipo} em PDF...", 'warning'))
                if tipo == 'completo':
                    caminho = self.gerador_relatorios.gerar_relatorio_completo('pdf', filename)
                elif tipo == 'caixas':
                    caminho = self.gerador_relatorios.gerar_relatorio_caixas('pdf', filename)
                elif tipo == 'arquivos':
                    caminho = self.gerador_relatorios.gerar_relatorio_arquivos('pdf', filename)
                elif tipo == 'segurados':
                    caminho = self.gerador_relatorios.gerar_relatorio_segurados('pdf', filename)
                else:
                    raise ValueError(f"Tipo de relatório desconhecido: {tipo}")
                self.root.after(0, lambda: self.show_message(self.message_busca, f"✅ Relatório PDF gerado: {caminho}"))
                try:
                    webbrowser.open(caminho)
                except:
                    pass
            except Exception as error:
                self.root.after(0, lambda: self.show_message(self.message_busca, f"❌ Erro ao gerar relatório: {error}", 'error'))
        t = threading.Thread(target=gerar_thread); t.daemon = True; t.start()

    def gerar_relatorio_excel(self, tipo):
        def gerar_thread():
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    title=f"Salvar relatório {tipo} como"
                )
                if not filename:
                    return
                self.root.after(0, lambda: self.show_message(self.message_busca, f"⏳ Gerando relatório {tipo} em Excel...", 'warning'))
                if tipo == 'completo':
                    caminho = self.gerador_relatorios.gerar_relatorio_completo('excel', filename)
                elif tipo == 'caixas':
                    caminho = self.gerador_relatorios.gerar_relatorio_caixas('excel', filename)
                elif tipo == 'arquivos':
                    caminho = self.gerador_relatorios.gerar_relatorio_arquivos('excel', filename)
                elif tipo == 'segurados':
                    caminho = self.gerador_relatorios.gerar_relatorio_segurados('excel', filename)
                else:
                    raise ValueError(f"Tipo de relatório desconhecido: {tipo}")
                self.root.after(0, lambda: self.show_message(self.message_busca, f"✅ Relatório Excel gerado: {caminho}"))
                try:
                    webbrowser.open(caminho)
                except:
                    pass
            except Exception as error:
                self.root.after(0, lambda: self.show_message(self.message_busca, f"❌ Erro ao gerar relatório: {error}", 'error'))
        t = threading.Thread(target=gerar_thread); t.daemon = True; t.start()

    # -------------------------
    # Caixas: criar / listar / render / excluir
    # -------------------------
    def _safe_int_field(self, value, field_name, required=False, allow_zero=False):
        v = str(value).strip()
        if required and v == "":
            raise ValueError(f"{field_name} é obrigatório")
        if v == "":
            return None
        try:
            i = int(v)
            if not allow_zero and i == 0:
                raise ValueError(f"{field_name} não pode ser zero")
            return i
        except ValueError:
            raise ValueError(f"{field_name} deve ser um número inteiro válido")

    def criar_caixa(self):
        def criar_caixa_thread():
            try:
                self.root.after(0, lambda: self.btn_criar_caixa.config(state='disabled', text='⏳ Criando...'))
                codigo = self._safe_int_field(self.caixa_fields['caixa_codigo'].get(), "Código da Caixa", required=True)
                nbi = self._safe_int_field(self.caixa_fields['caixa_nbi'].get(), "NBI", required=True)
                nbf = self._safe_int_field(self.caixa_fields['caixa_nbf'].get(), "NBF", required=True)
                caixa_data = {
                    'codigo': codigo,
                    'NBI': nbi,
                    'NBF': nbf,
                    'prateleira': self.caixa_fields['caixa_prateleira'].get().strip(),
                    'bloco': self.caixa_fields['caixa_bloco'].get().strip(),
                    'andar': self.caixa_fields['caixa_andar'].get().strip(),
                    'corredor': self.caixa_fields['caixa_corredor'].get().strip()
                }
                response = requests.post(f"{self.API_BASE}/caixas", json=caixa_data, headers=self.headers, timeout=10)
                if response.status_code in [200,201]:
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "✅ Caixa criada com sucesso!"))
                    self.root.after(0, self.limpar_form_caixa)
                    self.root.after(0, lambda: self.listar_caixas(True))
                else:
                    err = response.json().get('erro', f"Status {response.status_code}")
                    raise Exception(err)
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_caixas, f"❌ Erro: {e}", 'error'))
            finally:
                self.root.after(0, lambda: self.btn_criar_caixa.config(state='normal', text='➕ Criar Caixa'))
        t = threading.Thread(target=criar_caixa_thread); t.daemon = True; t.start()

    def listar_caixas(self, force_refresh=False):
        def listar_thread():
            try:
                response = requests.get(f"{self.API_BASE}/caixas", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    caixas = response.json()
                    caixas = self._normalize_list(caixas if isinstance(caixas, list) else [], kind='caixa')
                    self.app_state['data']['caixas'] = caixas
                    self.root.after(0, lambda: self.render_caixas(caixas))
                    self.root.after(0, self.update_last_update_time)
                else:
                    raise Exception(f"API retornou status {response.status_code}")
            except Exception as e:
                self.root.after(0, lambda: self.render_caixas_error(str(e)))
        t = threading.Thread(target=listar_thread); t.daemon = True; t.start()

    def render_caixas(self, caixas):
        for item in self.caixas_tree.get_children():
            self.caixas_tree.delete(item)
        if not caixas:
            self.caixas_tree.insert('', 'end', values=('Nenhuma caixa cadastrada', '', '', '', ''))
            return
        for caixa in caixas:
            codigo = caixa.get('codigo', '') if isinstance(caixa, dict) else str(caixa)
            nbi = caixa.get('NBI', '') if isinstance(caixa, dict) else ''
            nbf = caixa.get('NBF', '') if isinstance(caixa, dict) else ''
            local = f"{caixa.get('prateleira', '-')}/{caixa.get('bloco', '-')}/{caixa.get('andar', '-')}" if isinstance(caixa, dict) else '-'
            self.caixas_tree.insert('', 'end', values=(codigo, nbi, nbf, local, "🗑️"))

    def render_caixas_error(self, msg):
        for item in self.caixas_tree.get_children():
            self.caixas_tree.delete(item)
        self.caixas_tree.insert('', 'end', values=(f'❌ Erro: {msg}', '', '', '', ''))

    def on_caixa_click(self, event):
        item = self.caixas_tree.identify_row(event.y)
        column = self.caixas_tree.identify_column(event.x)
        if item and column == '#5':
            codigo = self.caixas_tree.item(item, 'values')[0]
            if messagebox.askyesno("Confirmar Exclusão", f"Excluir caixa {codigo}?"):
                self.excluir_caixa(codigo)

    def excluir_caixa(self, codigo):
        def excluir_thread():
            try:
                response = requests.delete(f"{self.API_BASE}/caixas/{codigo}", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "✅ Caixa excluída"))
                    self.root.after(0, lambda: self.listar_caixas(True))
                else:
                    raise Exception(response.json().get('erro', f"Status {response.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_caixas, f"❌ Erro ao excluir: {e}", 'error'))
        t = threading.Thread(target=excluir_thread); t.daemon = True; t.start()

    # -------------------------
    # Arquivos: criar / listar / render / excluir
    # -------------------------
    def criar_arquivo(self):
        def criar_thread():
            try:
                self.root.after(0, lambda: self.btn_criar_arquivo.config(state='disabled', text='⏳ Criando...'))
                nb = self._safe_int_field(self.arquivo_fields['arquivo_nb'].get(), "NB", required=True)
                aps = self.arquivo_fields['arquivo_aps'].get().strip()
                seg = self._safe_int_field(self.arquivo_fields['arquivo_seguradofk'].get(), "CPF Segurado", required=True)
                tipo = self._safe_int_field(self.arquivo_fields['arquivo_tipo'].get(), "Tipo", required=True)
                caixa_codigo = self._safe_int_field(self.arquivo_fields['arquivo_caixa'].get(), "Código da Caixa", required=True)
                arquivo_data = {'NB': nb, 'APS': aps, 'SeguradoFK': seg, 'Tipo': tipo, 'Caixa_codigo': caixa_codigo}
                response = requests.post(f"{self.API_BASE}/arquivos", json=arquivo_data, headers=self.headers, timeout=10)
                if response.status_code in [200,201]:
                    self.root.after(0, lambda: self.show_message(self.message_arquivos, "✅ Arquivo criado!"))
                    self.root.after(0, self.limpar_form_arquivo)
                    self.root.after(0, lambda: self.listar_arquivos(True))
                else:
                    raise Exception(response.json().get('erro', f"Status {response.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_arquivos, f"❌ Erro: {e}", 'error'))
            finally:
                self.root.after(0, lambda: self.btn_criar_arquivo.config(state='normal', text='➕ Criar Arquivo'))
        t = threading.Thread(target=criar_thread); t.daemon = True; t.start()

    def listar_arquivos(self, force_refresh=False):
        def listar_thread():
            try:
                response = requests.get(f"{self.API_BASE}/arquivos", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    arquivos = response.json()
                    arquivos = self._normalize_list(arquivos if isinstance(arquivos, list) else [], kind='arquivo')
                    self.app_state['data']['arquivos'] = arquivos
                    self.root.after(0, lambda: self.render_arquivos(arquivos))
                    self.root.after(0, self.update_last_update_time)
                else:
                    raise Exception(f"API retornou status {response.status_code}")
            except Exception as e:
                self.root.after(0, lambda: self.render_arquivos_error(str(e)))
        t = threading.Thread(target=listar_thread); t.daemon = True; t.start()

    def render_arquivos(self, arquivos):
        for item in self.arquivos_tree.get_children():
            self.arquivos_tree.delete(item)
        if not arquivos:
            self.arquivos_tree.insert('', 'end', values=('Nenhum arquivo cadastrado', '', '', '', '', ''))
            return
        for arquivo in arquivos:
            nb = arquivo.get('NB', arquivo.get('id', '')) if isinstance(arquivo, dict) else str(arquivo)
            aps = arquivo.get('APS', '') if isinstance(arquivo, dict) else ''
            seg = arquivo.get('SeguradoFK', '') if isinstance(arquivo, dict) else ''
            tipo = arquivo.get('Tipo', '') if isinstance(arquivo, dict) else ''
            caixa = arquivo.get('Caixa_codigo', '') if isinstance(arquivo, dict) else ''
            self.arquivos_tree.insert('', 'end', values=(nb, aps, seg, tipo, caixa, "🗑️"))

    def render_arquivos_error(self, msg):
        for item in self.arquivos_tree.get_children():
            self.arquivos_tree.delete(item)
        self.arquivos_tree.insert('', 'end', values=(f'❌ Erro: {msg}', '', '', '', '', ''))

    def on_arquivo_click(self, event):
        item = self.arquivos_tree.identify_row(event.y)
        column = self.arquivos_tree.identify_column(event.x)
        if item and column == '#6':
            nb = self.arquivos_tree.item(item, 'values')[0]
            if messagebox.askyesno("Confirmar Exclusão", f"Excluir arquivo {nb}?"):
                self.excluir_arquivo(nb)

    def excluir_arquivo(self, nb):
        def excluir_thread():
            try:
                response = requests.delete(f"{self.API_BASE}/arquivos/{nb}", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.show_message(self.message_arquivos, "✅ Arquivo excluído"))
                    self.root.after(0, lambda: self.listar_arquivos(True))
                else:
                    raise Exception(response.json().get('erro', f"Status {response.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_arquivos, f"❌ Erro ao excluir: {e}", 'error'))
        t = threading.Thread(target=excluir_thread); t.daemon = True; t.start()

    # -------------------------
    # Segurados: criar / listar / render / excluir
    # -------------------------
    def criar_segurado(self):
        def criar_thread():
            try:
                self.root.after(0, lambda: self.btn_criar_segurado.config(state='disabled', text='⏳ Criando...'))
                nome = self.segurado_fields['segurado_nome'].get().strip()
                cpf_raw = self.segurado_fields['segurado_cpf'].get().strip()
                if not nome:
                    raise ValueError("Nome é obrigatório")
                # CPF: armazenar como string (preserva zeros à esquerda)
                cpf = cpf_raw
                resp = requests.post(f"{self.API_BASE}/segurados", json={'Nome': nome, 'cpf': cpf}, headers=self.headers, timeout=10)
                if resp.status_code in [200,201]:
                    self.root.after(0, lambda: self.show_message(self.message_segurados, "✅ Segurado criado!"))
                    self.root.after(0, self.limpar_form_segurado)
                    self.root.after(0, lambda: self.listar_segurados(True))
                else:
                    raise Exception(resp.json().get('erro', f"Status {resp.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_segurados, f"❌ Erro: {e}", 'error'))
            finally:
                self.root.after(0, lambda: self.btn_criar_segurado.config(state='normal', text='➕ Criar Segurado'))
        t = threading.Thread(target=criar_thread); t.daemon = True; t.start()

    def listar_segurados(self, force_refresh=False):
        def listar_thread():
            try:
                response = requests.get(f"{self.API_BASE}/segurados", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    segurados = response.json()
                    segurados = self._normalize_list(segurados if isinstance(segurados, list) else [], kind='segurado')
                    self.app_state['data']['segurados'] = segurados
                    self.root.after(0, lambda: self.render_segurados(segurados))
                    self.root.after(0, self.update_last_update_time)
                else:
                    raise Exception(f"API retornou status {response.status_code}")
            except Exception as e:
                self.root.after(0, lambda: self.render_segurados_error(str(e)))
        t = threading.Thread(target=listar_thread); t.daemon = True; t.start()

    def render_segurados(self, segurados):
        for item in self.segurados_tree.get_children():
            self.segurados_tree.delete(item)
        if not segurados:
            self.segurados_tree.insert('', 'end', values=('Nenhum segurado cadastrado', '', '', ''))
            return
        for s in segurados:
            cpf = s.get('cpf', s.get('id', '')) if isinstance(s, dict) else str(s)
            nome = s.get('Nome', '') if isinstance(s, dict) else ''
            num = len(s.get('Arquivos', [])) if isinstance(s, dict) and isinstance(s.get('Arquivos', []), list) else 0
            self.segurados_tree.insert('', 'end', values=(cpf, nome, num, "🗑️"))

    def render_segurados_error(self, msg):
        for item in self.segurados_tree.get_children():
            self.segurados_tree.delete(item)
        self.segurados_tree.insert('', 'end', values=(f'❌ Erro: {msg}', '', '', ''))

    def on_segurado_click(self, event):
        item = self.segurados_tree.identify_row(event.y)
        column = self.segurados_tree.identify_column(event.x)
        if item and column == '#4':
            cpf = self.segurados_tree.item(item, 'values')[0]
            if messagebox.askyesno("Confirmar Exclusão", f"Excluir segurado {cpf}?"):
                self.excluir_segurado(cpf)

    def excluir_segurado(self, cpf):
        def excluir_thread():
            try:
                response = requests.delete(f"{self.API_BASE}/segurados/{cpf}", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.show_message(self.message_segurados, "✅ Segurado excluído"))
                    self.root.after(0, lambda: self.listar_segurados(True))
                else:
                    raise Exception(response.json().get('erro', f"Status {response.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_segurados, f"❌ Erro ao excluir: {e}", 'error'))
        t = threading.Thread(target=excluir_thread); t.daemon = True; t.start()

    # -------------------------
    # Dashboard: stats, test, sync, clear
    # -------------------------
    def load_stats(self, force=False):
        def stats_thread():
            try:
                response = requests.get(f"{self.API_BASE}/info", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    info = response.json()
                    self.root.after(0, lambda: self.render_stats(info))
                    self.root.after(0, lambda: self.mongo_status_var.set("🟢 ONLINE" if info.get('status_banco_dados', {}).get('mongodb') else "🔴 OFFLINE"))
                    self.root.after(0, lambda: self.json_status_var.set("🟢 ONLINE" if info.get('status_banco_dados', {}).get('json') else "🔴 OFFLINE"))
                    stats = info.get('estatisticas', {})
                    total = sum(stats.values()) if isinstance(stats, dict) else 0
                    self.root.after(0, lambda: self.total_items_var.set(str(total)))
                    self.root.after(0, self.update_last_update_time)
                else:
                    raise Exception(f"Status {response.status_code}")
            except Exception as e:
                self.root.after(0, lambda: self.render_stats_error(str(e)))
        t = threading.Thread(target=stats_thread); t.daemon = True; t.start()

    def test_api(self):
        def test_thread():
            try:
                r = requests.get(f"{self.API_BASE}/health", timeout=5)
                if r.status_code == 200:
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "✅ API respondendo"))
                else:
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "❌ API erro", 'error'))
            except:
                self.root.after(0, lambda: self.show_message(self.message_caixas, "❌ API não respondeu", 'error'))
        t = threading.Thread(target=test_thread); t.daemon = True; t.start()

    def forcar_atualizacao(self):
        def sync_thread():
            try:
                r = requests.post(f"{self.API_BASE}/refresh", headers=self.headers, timeout=10)
                if r.status_code == 200:
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "✅ Sincronização forçada concluída"))
                    self.root.after(0, lambda: self.load_stats(True))
                    self.root.after(0, lambda: self.listar_caixas(True))
                    self.root.after(0, lambda: self.listar_arquivos(True))
                    self.root.after(0, lambda: self.listar_segurados(True))
                else:
                    raise Exception(f"Status {r.status_code}")
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_caixas, f"❌ Erro sync: {e}", 'error'))
        t = threading.Thread(target=sync_thread); t.daemon = True; t.start()

    def clear_all_data(self):
        if not messagebox.askyesno("Confirmar", "⚠️ Isso irá apagar TODOS os dados. Continuar?"):
            return
        def clear_thread():
            try:
                r = requests.post(f"{self.API_BASE}/limpar", headers=self.headers, timeout=10)
                if r.status_code == 200:
                    self.app_state['data'] = {'caixas': [], 'arquivos': [], 'segurados': []}
                    self.root.after(0, lambda: self.show_message(self.message_caixas, "✅ Dados limpos"))
                    self.root.after(0, lambda: self.listar_caixas(True))
                    self.root.after(0, lambda: self.listar_arquivos(True))
                    self.root.after(0, lambda: self.listar_segurados(True))
                else:
                    raise Exception(f"Status {r.status_code}")
            except Exception as e:
                self.root.after(0, lambda: self.show_message(self.message_caixas, f"❌ Erro ao limpar: {e}", 'error'))
        t = threading.Thread(target=clear_thread); t.daemon = True; t.start()

def main():
    root = tk.Tk()
    app = GCAApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()