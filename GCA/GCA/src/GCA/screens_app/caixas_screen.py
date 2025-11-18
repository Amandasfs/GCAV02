# screens_app/caixas_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import base64

class CaixasScreen:
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
        
        title = tk.Label(self.frame, text="📦 Gerenciar Caixas",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        form_frame = tk.LabelFrame(self.frame, text="Dados da Caixa",
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8f9fa',
                                  padx=15,
                                  pady=15)
        form_frame.pack(fill='x', padx=20, pady=10)

        fields = [
            ("Código da Caixa *", "caixa_codigo"),
            ("NBI *", "caixa_nbi"), 
            ("NBF *", "caixa_nbf"),
            ("Prateleira", "caixa_prateleira"),
            ("Bloco", "caixa_bloco"),
            ("Andar", "caixa_andar"),
            ("Corredor", "caixa_corredor")
        ]

        self.caixa_fields = {}
        for i, (label, field_name) in enumerate(fields):
            row = i % 4
            col = i // 4
            
            field_frame = tk.Frame(form_frame, bg='#f8f9fa')
            field_frame.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            lbl = tk.Label(field_frame, text=label, font=('Arial', 9), bg='#f8f9fa')
            lbl.pack(anchor='w')
            
            entry = tk.Entry(field_frame, width=15, font=('Arial', 10))
            entry.pack(pady=2)
            self.caixa_fields[field_name] = entry

        button_frame = tk.Frame(self.frame, bg='white')
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

        self.message_caixas = tk.Label(self.frame, text="", font=('Arial', 10), bg='white')
        self.message_caixas.pack(pady=5)

        table_frame = tk.Frame(self.frame, bg='white')
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
    
    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.listar_caixas()
    
    def hide(self):
        self.frame.pack_forget()
    
    def show_message(self, message, message_type='success'):
        colors = {
            'success': ('#155724', '#d4edda'),
            'error': ('#721c24', '#f8d7da'),
            'warning': ('#856404', '#fff3cd')
        }
        
        fg_color, bg_color = colors.get(message_type, colors['success'])
        self.message_caixas.config(text=message, fg=fg_color, bg=bg_color)
        
        self.frame.after(5000, lambda: self.message_caixas.config(text="", bg='white'))
    
    def _safe_int_field(self, value, field_name, required=False):
        v = str(value).strip()
        if required and v == "":
            raise ValueError(f"{field_name} é obrigatório")
        if v == "":
            return None
        try:
            return int(v)
        except ValueError:
            raise ValueError(f"{field_name} deve ser um número inteiro válido")
    
    def criar_caixa(self):
        def criar_thread():
            try:
                self.frame.after(0, lambda: self.btn_criar_caixa.config(state='disabled', text='⏳ Criando...'))
                
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
                
                response = requests.post(f"{self.api_base}/caixas", json=caixa_data, headers=self.headers, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.frame.after(0, lambda: self.show_message("✅ Caixa criada com sucesso!"))
                    self.frame.after(0, self.limpar_form_caixa)
                    self.frame.after(0, lambda: self.listar_caixas(True))
                else:
                    error_msg = response.json().get('erro', f"Status {response.status_code}")
                    raise Exception(error_msg)
                    
            except Exception as e:
                self.frame.after(0, lambda: self.show_message(f"❌ Erro: {str(e)}", 'error'))
            finally:
                self.frame.after(0, lambda: self.btn_criar_caixa.config(state='normal', text='➕ Criar Caixa'))
        
        thread = threading.Thread(target=criar_thread)
        thread.daemon = True
        thread.start()
    
    def listar_caixas(self, force_refresh=False):
        def listar_thread():
            try:
                response = requests.get(f"{self.api_base}/caixas", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    caixas = response.json()
                    self.frame.after(0, lambda: self.render_caixas(caixas))
                else:
                    raise Exception(f"API retornou status {response.status_code}")
            except Exception as e:
                self.frame.after(0, lambda: self.render_caixas_error(str(e)))
        
        thread = threading.Thread(target=listar_thread)
        thread.daemon = True
        thread.start()
    
    def render_caixas(self, caixas):
        for item in self.caixas_tree.get_children():
            self.caixas_tree.delete(item)
        
        if not caixas:
            self.caixas_tree.insert('', 'end', values=('Nenhuma caixa cadastrada', '', '', '', ''))
            return
        
        for caixa in caixas:
            codigo = caixa.get('codigo', '')
            nbi = caixa.get('NBI', '')
            nbf = caixa.get('NBF', '')
            localizacao = f"{caixa.get('prateleira', '-')}/{caixa.get('bloco', '-')}/{caixa.get('andar', '-')}"
            
            acao = "🗑️" if self.admin_manager.has_permission() else "👁️"
            
            self.caixas_tree.insert('', 'end', values=(codigo, nbi, nbf, localizacao, acao))
    
    def render_caixas_error(self, msg):
        for item in self.caixas_tree.get_children():
            self.caixas_tree.delete(item)
        self.caixas_tree.insert('', 'end', values=(f'❌ Erro: {msg}', '', '', '', ''))
    
    def on_caixa_click(self, event):
        item = self.caixas_tree.identify_row(event.y)
        column = self.caixas_tree.identify_column(event.x)
        
        if item and column == '#5':
            codigo = self.caixas_tree.item(item, 'values')[0]
            
            if self.admin_manager.has_permission():
                if messagebox.askyesno("Confirmar Exclusão", f"Excluir caixa {codigo}?"):
                    self.excluir_caixa(codigo)
            else:
                messagebox.showinfo("Visualizar", f"Visualizando caixa {codigo}\n\nApenas administradores podem excluir.")
    
    def excluir_caixa(self, codigo):
        def excluir_thread():
            try:
                response = requests.delete(f"{self.api_base}/caixas/{codigo}", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.frame.after(0, lambda: self.show_message("✅ Caixa excluída com sucesso"))
                    self.frame.after(0, lambda: self.listar_caixas(True))
                else:
                    error_msg = response.json().get('erro', f"Status {response.status_code}")
                    raise Exception(error_msg)
            except Exception as e:
                self.frame.after(0, lambda: self.show_message(f"❌ Erro ao excluir: {str(e)}", 'error'))
        
        thread = threading.Thread(target=excluir_thread)
        thread.daemon = True
        thread.start()
    
    def limpar_form_caixa(self):
        for field in self.caixa_fields.values():
            field.delete(0, tk.END)
        self.message_caixas.config(text="")