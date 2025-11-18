# screens_app/arquivos_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import base64

class ArquivosScreen:
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
        
        title = tk.Label(self.frame, text="📁 Gerenciar Arquivos",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        form_frame = tk.LabelFrame(self.frame, text="Dados do Arquivo",
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8f9fa',
                                  padx=15,
                                  pady=15)
        form_frame.pack(fill='x', padx=20, pady=10)

        fields = [
            ("NB *", "arquivo_nb"),
            ("APS *", "arquivo_aps"),
            ("CPF Segurado *", "arquivo_seguradofk"),
            ("Tipo *", "arquivo_tipo"),
            ("Código da Caixa *", "arquivo_caixa")
        ]

        self.arquivo_fields = {}
        for i, (label, field_name) in enumerate(fields):
            field_frame = tk.Frame(form_frame, bg='#f8f9fa')
            field_frame.grid(row=i, column=0, padx=10, pady=5, sticky='w')
            
            lbl = tk.Label(field_frame, text=label, font=('Arial', 9), bg='#f8f9fa')
            lbl.pack(anchor='w')
            
            entry = tk.Entry(field_frame, width=20, font=('Arial', 10))
            entry.pack(pady=2)
            self.arquivo_fields[field_name] = entry

        button_frame = tk.Frame(self.frame, bg='white')
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

        self.message_arquivos = tk.Label(self.frame, text="", font=('Arial', 10), bg='white')
        self.message_arquivos.pack(pady=5)

        table_frame = tk.Frame(self.frame, bg='white')
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
    
    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.listar_arquivos()
    
    def hide(self):
        self.frame.pack_forget()
    
    def show_message(self, message, message_type='success'):
        colors = {
            'success': ('#155724', '#d4edda'),
            'error': ('#721c24', '#f8d7da'),
            'warning': ('#856404', '#fff3cd')
        }
        
        fg_color, bg_color = colors.get(message_type, colors['success'])
        self.message_arquivos.config(text=message, fg=fg_color, bg=bg_color)
        
        self.frame.after(5000, lambda: self.message_arquivos.config(text="", bg='white'))
    
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
    
    def criar_arquivo(self):
        def criar_thread():
            try:
                self.frame.after(0, lambda: self.btn_criar_arquivo.config(state='disabled', text='⏳ Criando...'))
                
                nb = self._safe_int_field(self.arquivo_fields['arquivo_nb'].get(), "NB", required=True)
                aps = self.arquivo_fields['arquivo_aps'].get().strip()
                seguradofk = self._safe_int_field(self.arquivo_fields['arquivo_seguradofk'].get(), "CPF Segurado", required=True)
                tipo = self._safe_int_field(self.arquivo_fields['arquivo_tipo'].get(), "Tipo", required=True)
                caixa = self._safe_int_field(self.arquivo_fields['arquivo_caixa'].get(), "Código da Caixa", required=True)
                
                if not aps:
                    raise ValueError("APS é obrigatório")
                
                arquivo_data = {
                    'NB': nb,
                    'APS': aps,
                    'SeguradoFK': seguradofk,
                    'Tipo': tipo,
                    'Caixa_codigo': caixa
                }
                
                response = requests.post(f"{self.api_base}/arquivos", json=arquivo_data, headers=self.headers, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.frame.after(0, lambda: self.show_message("✅ Arquivo criado com sucesso!"))
                    self.frame.after(0, self.limpar_form_arquivo)
                    self.frame.after(0, lambda: self.listar_arquivos(True))
                else:
                    error_msg = response.json().get('erro', f"Status {response.status_code}")
                    raise Exception(error_msg)
                    
            except Exception as e:
                self.frame.after(0, lambda: self.show_message(f"❌ Erro: {str(e)}", 'error'))
            finally:
                self.frame.after(0, lambda: self.btn_criar_arquivo.config(state='normal', text='➕ Criar Arquivo'))
        
        thread = threading.Thread(target=criar_thread)
        thread.daemon = True
        thread.start()
    
    def listar_arquivos(self, force_refresh=False):
        def listar_thread():
            try:
                response = requests.get(f"{self.api_base}/arquivos", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    arquivos = response.json()
                    self.frame.after(0, lambda: self.render_arquivos(arquivos))
                else:
                    raise Exception(f"API retornou status {response.status_code}")
            except Exception as e:
                self.frame.after(0, lambda: self.render_arquivos_error(str(e)))
        
        thread = threading.Thread(target=listar_thread)
        thread.daemon = True
        thread.start()
    
    def render_arquivos(self, arquivos):
        for item in self.arquivos_tree.get_children():
            self.arquivos_tree.delete(item)
        
        if not arquivos:
            self.arquivos_tree.insert('', 'end', values=('Nenhum arquivo cadastrado', '', '', '', '', ''))
            return
        
        for arquivo in arquivos:
            nb = arquivo.get('NB', '')
            aps = arquivo.get('APS', '')
            segurado = arquivo.get('SeguradoFK', '')
            tipo = arquivo.get('Tipo', '')
            caixa = arquivo.get('Caixa_codigo', '')
            
            acao = "🗑️" if self.admin_manager.has_permission() else "👁️"
            
            self.arquivos_tree.insert('', 'end', values=(nb, aps, segurado, tipo, caixa, acao))
    
    def render_arquivos_error(self, msg):
        for item in self.arquivos_tree.get_children():
            self.arquivos_tree.delete(item)
        self.arquivos_tree.insert('', 'end', values=(f'❌ Erro: {msg}', '', '', '', '', ''))
    
    def on_arquivo_click(self, event):
        item = self.arquivos_tree.identify_row(event.y)
        column = self.arquivos_tree.identify_column(event.x)
        
        if item and column == '#6':
            nb = self.arquivos_tree.item(item, 'values')[0]
            
            if self.admin_manager.has_permission():
                if messagebox.askyesno("Confirmar Exclusão", f"Excluir arquivo {nb}?"):
                    self.excluir_arquivo(nb)
            else:
                messagebox.showinfo("Visualizar", f"Visualizando arquivo {nb}\n\nApenas administradores podem excluir.")
    
    def excluir_arquivo(self, nb):
        def excluir_thread():
            try:
                response = requests.delete(f"{self.api_base}/arquivos/{nb}", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.frame.after(0, lambda: self.show_message("✅ Arquivo excluído com sucesso"))
                    self.frame.after(0, lambda: self.listar_arquivos(True))
                else:
                    error_msg = response.json().get('erro', f"Status {response.status_code}")
                    raise Exception(error_msg)
            except Exception as e:
                self.frame.after(0, lambda: self.show_message(f"❌ Erro ao excluir: {str(e)}", 'error'))
        
        thread = threading.Thread(target=excluir_thread)
        thread.daemon = True
        thread.start()
    
    def limpar_form_arquivo(self):
        for field in self.arquivo_fields.values():
            field.delete(0, tk.END)
        self.message_arquivos.config(text="")