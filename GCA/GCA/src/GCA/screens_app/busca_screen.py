# screens_app/busca_screen.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
import csv
import base64

class BuscaScreen:
    def __init__(self, parent, api_base, credentials, admin_manager):
        self.parent = parent
        self.api_base = api_base
        self.credentials = credentials
        self.admin_manager = admin_manager
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode(
                f"{self.credentials['username']}:{self.credentials['password']}".encode()
            ).decode()
        }
        
        self.frame = None
        self.setup_ui()
        
    def setup_ui(self):
        self.frame = tk.Frame(self.parent, bg='white')
        
        title = tk.Label(self.frame, text="🔍 Busca Avançada",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        filter_frame = tk.LabelFrame(self.frame, text="Filtros de Busca",
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

        button_frame = tk.Frame(self.frame, bg='white')
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

        self.message_busca = tk.Label(self.frame, text="", font=('Arial', 10), bg='white')
        self.message_busca.pack(pady=5)

        results_frame = tk.LabelFrame(self.frame, text="Resultados da Busca",
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

        self.resultados_count = tk.Label(results_frame, text="Nenhuma busca realizada",
                                        font=('Arial', 10), bg='white', fg='#6c757d')
        self.resultados_count.pack(side='bottom', fill='x')

        self.busca_tree.insert('', 'end', values=('Digite os critérios e clique em Buscar', '', '', '', ''))
    
    def show(self):
        self.frame.pack(fill='both', expand=True)
    
    def hide(self):
        self.frame.pack_forget()
    
    def show_message(self, message, message_type='success'):
        colors = {
            'success': ('#155724', '#d4edda'),
            'error': ('#721c24', '#f8d7da'),
            'warning': ('#856404', '#fff3cd')
        }
        
        fg_color, bg_color = colors.get(message_type, colors['success'])
        self.message_busca.config(text=message, fg=fg_color, bg=bg_color)
        
        self.frame.after(5000, lambda: self.message_busca.config(text="", bg='white'))
    
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
                    response = requests.get(f"{self.api_base}/caixas", headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        caixas = response.json()
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
                    response = requests.get(f"{self.api_base}/arquivos", headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        arquivos = response.json()
                        for arquivo in arquivos:
                            if self.filtrar_arquivo(arquivo, criterios):
                                resultados.append({
                                    'tipo': 'Arquivo',
                                    'codigo': arquivo.get('NB', ''),
                                    'descricao': f"APS: {arquivo.get('APS', '')} | Tipo: {arquivo.get('Tipo', '')}",
                                    'localizacao': f"Caixa: {arquivo.get('Caixa_codigo', '')}",
                                    'detalhes': f"Segurado: {arquivo.get('SeguradoFK', '')}"
                                })
                
                if criterios['tipo'] in ['todos', 'segurados']:
                    response = requests.get(f"{self.api_base}/segurados", headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        segurados = response.json()
                        for segurado in segurados:
                            if self.filtrar_segurado(segurado, criterios):
                                num_arquivos = len(segurado.get('Arquivos', []))
                                resultados.append({
                                    'tipo': 'Segurado',
                                    'codigo': segurado.get('cpf', ''),
                                    'descricao': f"Nome: {segurado.get('Nome', '')}",
                                    'localizacao': f"Arquivos: {num_arquivos}",
                                    'detalhes': f"Total de arquivos: {num_arquivos}"
                                })
                
                self.frame.after(0, lambda: self.render_resultados_busca(resultados))
                
            except Exception as error:
                self.frame.after(0, lambda: self.show_message(f"❌ Erro na busca: {str(error)}", 'error'))
        
        thread = threading.Thread(target=buscar_thread)
        thread.daemon = True
        thread.start()
    
    def filtrar_caixa(self, caixa, criterios):
        codigo = str(caixa.get('codigo', ''))
        if criterios['codigo'] and criterios['codigo'] not in codigo:
            return False
        
        if criterios['localizacao']:
            localizacao = f"{caixa.get('prateleira', '')}{caixa.get('bloco', '')}{caixa.get('andar', '')}{caixa.get('corredor', '')}"
            if criterios['localizacao'] not in localizacao:
                return False
        
        return True
    
    def filtrar_arquivo(self, arquivo, criterios):
        nb = str(arquivo.get('NB', ''))
        if criterios['codigo'] and criterios['codigo'] not in nb:
            return False
        
        if criterios['nome'] and criterios['nome'] not in str(arquivo.get('APS', '')):
            return False
        
        if criterios['tipo_arquivo'] and criterios['tipo_arquivo'] not in str(arquivo.get('Tipo', '')):
            return False
        
        return True
    
    def filtrar_segurado(self, segurado, criterios):
        cpf = str(segurado.get('cpf', ''))
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
        self.show_message(f"✅ Busca concluída - {len(resultados)} resultado(s) encontrado(s)")
    
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
            self.show_message("❌ Nenhum dado para exportar", 'warning')
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
            
            self.show_message(f"✅ Resultados exportados para {filename}")
        except Exception as error:
            self.show_message(f"❌ Erro ao exportar: {str(error)}", 'error')