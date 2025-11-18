# screens_app/segurados_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import base64

class SeguradosScreen:
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
        
        title = tk.Label(self.frame, text="👤 Gerenciar Segurados",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        form_frame = tk.LabelFrame(self.frame, text="Dados do Segurado",
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8f9fa',
                                  padx=15,
                                  pady=15)
        form_frame.pack(fill='x', padx=20, pady=10)

        fields = [
            ("Nome *", "segurado_nome"),
            ("CPF *", "segurado_cpf")
        ]

        self.segurado_fields = {}
        for i, (label, field_name) in enumerate(fields):
            field_frame = tk.Frame(form_frame, bg='#f8f9fa')
            field_frame.grid(row=0, column=i, padx=20, pady=5, sticky='w')
            
            lbl = tk.Label(field_frame, text=label, font=('Arial', 9), bg='#f8f9fa')
            lbl.pack(anchor='w')
            
            entry = tk.Entry(field_frame, width=25, font=('Arial', 10))
            entry.pack(pady=2)
            self.segurado_fields[field_name] = entry

        button_frame = tk.Frame(self.frame, bg='white')
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

        self.message_segurados = tk.Label(self.frame, text="", font=('Arial', 10), bg='white')
        self.message_segurados.pack(pady=5)

        table_frame = tk.Frame(self.frame, bg='white')
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
    
    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.listar_segurados()
    
    def hide(self):
        self.frame.pack_forget()
    
    def show_message(self, message, message_type='success'):
        colors = {
            'success': ('#155724', '#d4edda'),
            'error': ('#721c24', '#f8d7da'),
            'warning': ('#856404', '#fff3cd')
        }
        
        fg_color, bg_color = colors.get(message_type, colors['success'])
        self.message_segurados.config(text=message, fg=fg_color, bg=bg_color)
        
        self.frame.after(5000, lambda: self.message_segurados.config(text="", bg='white'))
    
    def criar_segurado(self):
        def criar_thread():
            try:
                self.frame.after(0, lambda: self.btn_criar_segurado.config(state='disabled', text='⏳ Criando...'))
                
                nome = self.segurado_fields['segurado_nome'].get().strip()
                cpf = self.segurado_fields['segurado_cpf'].get().strip()
                
                if not nome:
                    raise ValueError("Nome é obrigatório")
                if not cpf:
                    raise ValueError("CPF é obrigatório")
                
                # Validar CPF (apenas verifica se tem 11 dígitos)
                if len(cpf) != 11 or not cpf.isdigit():
                    raise ValueError("CPF deve conter 11 dígitos numéricos")
                
                segurado_data = {
                    'Nome': nome,
                    'cpf': cpf
                }
                
                response = requests.post(f"{self.api_base}/segurados", json=segurado_data, headers=self.headers, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.frame.after(0, lambda: self.show_message("✅ Segurado criado com sucesso!"))
                    self.frame.after(0, self.limpar_form_segurado)
                    self.frame.after(0, lambda: self.listar_segurados(True))
                else:
                    error_msg = response.json().get('erro', f"Status {response.status_code}")
                    raise Exception(error_msg)
                    
            except Exception as e:
                self.frame.after(0, lambda: self.show_message(f"❌ Erro: {str(e)}", 'error'))
            finally:
                self.frame.after(0, lambda: self.btn_criar_segurado.config(state='normal', text='➕ Criar Segurado'))
        
        thread = threading.Thread(target=criar_thread)
        thread.daemon = True
        thread.start()
    
    def listar_segurados(self, force_refresh=False):
        def listar_thread():
            try:
                response = requests.get(f"{self.api_base}/segurados", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    segurados = response.json()
                    self.frame.after(0, lambda: self.render_segurados(segurados))
                else:
                    raise Exception(f"API retornou status {response.status_code}")
            except Exception as e:
                self.frame.after(0, lambda: self.render_segurados_error(str(e)))
        
        thread = threading.Thread(target=listar_thread)
        thread.daemon = True
        thread.start()
    
    def render_segurados(self, segurados):
        for item in self.segurados_tree.get_children():
            self.segurados_tree.delete(item)
        
        if not segurados:
            self.segurados_tree.insert('', 'end', values=('Nenhum segurado cadastrado', '', '', ''))
            return
        
        for segurado in segurados:
            cpf = segurado.get('cpf', '')
            nome = segurado.get('Nome', '')
            num_arquivos = len(segurado.get('Arquivos', []))
            
            acao = "🗑️" if self.admin_manager.has_permission() else "👁️"
            
            self.segurados_tree.insert('', 'end', values=(cpf, nome, num_arquivos, acao))
    
    def render_segurados_error(self, msg):
        for item in self.segurados_tree.get_children():
            self.segurados_tree.delete(item)
        self.segurados_tree.insert('', 'end', values=(f'❌ Erro: {msg}', '', '', ''))
    
    def on_segurado_click(self, event):
        item = self.segurados_tree.identify_row(event.y)
        column = self.segurados_tree.identify_column(event.x)
        
        if item and column == '#4':
            cpf = self.segurados_tree.item(item, 'values')[0]
            
            if self.admin_manager.has_permission():
                if messagebox.askyesno("Confirmar Exclusão", f"Excluir segurado {cpf}?"):
                    self.excluir_segurado(cpf)
            else:
                messagebox.showinfo("Visualizar", f"Visualizando segurado {cpf}\n\nApenas administradores podem excluir.")
    
    def excluir_segurado(self, cpf):
        def excluir_thread():
            try:
                response = requests.delete(f"{self.api_base}/segurados/{cpf}", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.frame.after(0, lambda: self.show_message("✅ Segurado excluído com sucesso"))
                    self.frame.after(0, lambda: self.listar_segurados(True))
                else:
                    error_msg = response.json().get('erro', f"Status {response.status_code}")
                    raise Exception(error_msg)
            except Exception as e:
                self.frame.after(0, lambda: self.show_message(f"❌ Erro ao excluir: {str(e)}", 'error'))
        
        thread = threading.Thread(target=excluir_thread)
        thread.daemon = True
        thread.start()
    
    def limpar_form_segurado(self):
        for field in self.segurado_fields.values():
            field.delete(0, tk.END)
        self.message_segurados.config(text="")