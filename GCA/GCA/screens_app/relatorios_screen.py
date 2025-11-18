# screens_app/relatorios_screen.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
import threading
import base64
import webbrowser
from relatorios import GeradorRelatorios

class RelatoriosScreen:
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
        
        self.gerador_relatorios = GeradorRelatorios()
        self.frame = None
        self.setup_ui()
        
    def setup_ui(self):
        self.frame = tk.Frame(self.parent, bg='white')
        
        title = tk.Label(self.frame, text="📋 Relatórios do Sistema",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        reports_frame = tk.Frame(self.frame, bg='white')
        reports_frame.pack(fill='both', expand=True, padx=20, pady=10)

        relatorios = [
            {
                "titulo": "📦 Relatório de Caixas", 
                "descricao": "Lista completa de todas as caixas cadastradas", 
                "tipo": "caixas", 
                "cor": "#3498db"
            },
            {
                "titulo": "📁 Relatório de Arquivos", 
                "descricao": "Relatório detalhado de arquivos por tipo e localização", 
                "tipo": "arquivos", 
                "cor": "#27ae60"
            },
            {
                "titulo": "👤 Relatório de Segurados", 
                "descricao": "Lista de segurados e seus arquivos associados", 
                "tipo": "segurados", 
                "cor": "#e74c3c"
            },
            {
                "titulo": "📊 Relatório Completo", 
                "descricao": "Relatório geral com todos os dados do sistema", 
                "tipo": "completo", 
                "cor": "#f39c12"
            }
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

        preview_frame = tk.LabelFrame(self.frame, text="Visualização do Relatório",
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
        
        self.dados_cache = {
            'caixas': [],
            'arquivos': [],
            'segurados': []
        }
    
    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.carregar_dados_cache()
    
    def hide(self):
        self.frame.pack_forget()
    
    def carregar_dados_cache(self):
        def carregar_thread():
            try:
                response = requests.get(f"{self.api_base}/caixas", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.dados_cache['caixas'] = response.json()
                
                response = requests.get(f"{self.api_base}/arquivos", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.dados_cache['arquivos'] = response.json()
                
                response = requests.get(f"{self.api_base}/segurados", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.dados_cache['segurados'] = response.json()
                    
            except Exception as e:
                print(f"Erro ao carregar dados para relatórios: {e}")
        
        thread = threading.Thread(target=carregar_thread)
        thread.daemon = True
        thread.start()
    
    def visualizar_relatorio(self, tipo):
        try:
            self.relatorio_text.config(state='normal')
            self.relatorio_text.delete('1.0', tk.END)
            
            if tipo == 'caixas':
                dados = self.dados_cache['caixas']
                conteudo = "RELATÓRIO DE CAIXAS\n\n"
                for caixa in dados:
                    conteudo += f"Código: {caixa.get('codigo', '')} | NBI: {caixa.get('NBI', '')} | NBF: {caixa.get('NBF', '')}\n"
                    conteudo += f"Localização: {caixa.get('prateleira', '')}/{caixa.get('bloco', '')}/{caixa.get('andar', '')}\n"
                    conteudo += f"Corredor: {caixa.get('corredor', '')}\n"
                    conteudo += "-" * 50 + "\n"
                    
            elif tipo == 'arquivos':
                dados = self.dados_cache['arquivos']
                conteudo = "RELATÓRIO DE ARQUIVOS\n\n"
                for arquivo in dados:
                    conteudo += f"NB: {arquivo.get('NB', '')} | APS: {arquivo.get('APS', '')}\n"
                    conteudo += f"Tipo: {arquivo.get('Tipo', '')} | Caixa: {arquivo.get('Caixa_codigo', '')}\n"
                    conteudo += f"Segurado: {arquivo.get('SeguradoFK', '')}\n"
                    conteudo += "-" * 50 + "\n"
                    
            elif tipo == 'segurados':
                dados = self.dados_cache['segurados']
                conteudo = "RELATÓRIO DE SEGURADOS\n\n"
                for segurado in dados:
                    conteudo += f"CPF: {segurado.get('cpf', '')} | Nome: {segurado.get('Nome', '')}\n"
                    conteudo += f"Total de Arquivos: {len(segurado.get('Arquivos', []))}\n"
                    conteudo += "-" * 50 + "\n"
                    
            elif tipo == 'completo':
                conteudo = "RELATÓRIO COMPLETO DO SISTEMA\n\n"
                conteudo += f"Total de Caixas: {len(self.dados_cache['caixas'])}\n"
                conteudo += f"Total de Arquivos: {len(self.dados_cache['arquivos'])}\n"
                conteudo += f"Total de Segurados: {len(self.dados_cache['segurados'])}\n\n"
                
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
                    title=f"Salvar relatório {tipo} como PDF"
                )
                
                if not filename:
                    return
                
                self.carregar_dados_cache()
                
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
                
                self.frame.after(0, lambda: messagebox.showinfo("Sucesso", f"✅ Relatório PDF gerado: {caminho}"))
                
                try:
                    webbrowser.open(caminho)
                except:
                    pass
                    
            except Exception as error:
                self.frame.after(0, lambda: messagebox.showerror("Erro", f"❌ Erro ao gerar relatório PDF: {str(error)}"))
        
        thread = threading.Thread(target=gerar_thread)
        thread.daemon = True
        thread.start()

    def gerar_relatorio_excel(self, tipo):
        def gerar_thread():
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    title=f"Salvar relatório {tipo} como Excel"
                )
                
                if not filename:
                    return
                
                self.carregar_dados_cache()
                
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
                
                self.frame.after(0, lambda: messagebox.showinfo("Sucesso", f"✅ Relatório Excel gerado: {caminho}"))
                
                try:
                    webbrowser.open(caminho)
                except:
                    pass
                    
            except Exception as error:
                self.frame.after(0, lambda: messagebox.showerror("Erro", f"❌ Erro ao gerar relatório Excel: {str(error)}"))
        
        thread = threading.Thread(target=gerar_thread)
        thread.daemon = True
        thread.start()