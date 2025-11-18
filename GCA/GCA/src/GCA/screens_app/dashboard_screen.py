# screens_app/dashboard_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import base64
from datetime import datetime
from api_utils import APIUtils

class DashboardScreen:
    def __init__(self, parent, api_base, credentials, admin_manager):
        self.parent = parent
        self.api_base = api_base
        self.credentials = credentials
        self.admin_manager = admin_manager

        def __init__(self, parent, api_base, credentials, admin_auth):
         self.api = APIUtils(api_base, credentials)

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode(
                f"{self.credentials['username']}:{self.credentials['password']}".encode()
            ).decode()
        }
        
        self.frame = None
        self.app_state = {
            'auto_refresh': True,
            'last_update': None
        }
        self.setup_ui()
        
    def setup_ui(self):
        self.frame = tk.Frame(self.parent, bg='white')

        title = tk.Label(self.frame, text="📊 Dashboard do Sistema",
                        font=('Arial', 18, 'bold'), bg='white')
        title.pack(pady=20, anchor='w', padx=20)

        toggle_frame = tk.Frame(self.frame, bg='white')
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

        self.stats_frame = tk.Frame(self.frame, bg='white')
        self.stats_frame.pack(fill='x', padx=20, pady=20)

        self.stats_placeholder = tk.Label(self.stats_frame,
                                         text="Carregando estatísticas...",
                                         font=('Arial', 12),
                                         bg='white')
        self.stats_placeholder.pack()

        self.last_update_frame = tk.Frame(self.frame, bg='white')
        self.last_update_frame.pack(pady=10)

        self.last_update_label = tk.Label(self.last_update_frame,
                                         text="Última atualização: --:--:--",
                                         font=('Arial', 10),
                                         fg='#6c757d',
                                         bg='white')
        self.last_update_label.pack()

        button_frame = tk.Frame(self.frame, bg='white')
        button_frame.pack(pady=20)

        buttons = [
            ("🔄 Atualizar Agora", self.load_stats, '#3498db'),
            ("🧪 Testar API", self.test_api, '#27ae60'),
            ("⚡ Forçar Sync", self.forcar_atualizacao, '#f39c12'),
        ]
        
        if self.admin_manager.has_permission():
            buttons.append(("🗑️ Limpar Tudo", self.clear_all_data, '#e74c3c'))

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

    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.load_stats()
        if self.app_state['auto_refresh']:
            self.start_auto_refresh()

    def hide(self):
        self.frame.pack_forget()
        self.stop_auto_refresh()

    def toggle_auto_refresh(self):
        self.app_state['auto_refresh'] = self.auto_refresh_var.get()
        if self.app_state['auto_refresh']:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()

    def start_auto_refresh(self):
        if hasattr(self, 'refresh_interval'):
            self.frame.after_cancel(self.refresh_interval)
        
        def refresh():
            if self.app_state['auto_refresh']:
                self.load_stats()
            self.refresh_interval = self.frame.after(10000, refresh)
        
        self.refresh_interval = self.frame.after(10000, refresh)

    def stop_auto_refresh(self):
        if hasattr(self, 'refresh_interval'):
            self.frame.after_cancel(self.refresh_interval)

    def update_last_update_time(self):
        now = datetime.now()
        self.app_state['last_update'] = now
        time_str = now.strftime('%H:%M:%S')
        self.last_update_label.config(text=f"Última atualização: {time_str}")

    def load_stats(self):
        def stats_thread():
            try:
                response = requests.get(f"{self.api_base}/info", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    info = response.json()
                    self.frame.after(0, lambda: self.render_stats(info))
                    self.frame.after(0, self.update_last_update_time)
                else:
                    raise Exception(f"Status {response.status_code}")
            except Exception as e:
                self.frame.after(0, lambda: self.render_stats_error(str(e)))
        
        thread = threading.Thread(target=stats_thread)
        thread.daemon = True
        thread.start()

    def render_stats(self, info):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = info.get('estatisticas', {})
        
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

        for i in range(4):
            self.stats_frame.columnconfigure(i, weight=1)

    def render_stats_error(self, msg):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        error_label = tk.Label(self.stats_frame,
                              text=f"❌ Erro ao carregar estatísticas: {msg}",
                              font=('Arial', 12),
                              fg='#e74c3c',
                              bg='white')
        error_label.pack(pady=20)

    def test_api(self):
        def test_thread():
            try:
                response = requests.get(f"{self.api_base}/health", timeout=5)
                if response.status_code == 200:
                    self.frame.after(0, lambda: messagebox.showinfo("Sucesso", "✅ API respondendo corretamente"))
                else:
                    self.frame.after(0, lambda: messagebox.showerror("Erro", f"❌ API retornou status {response.status_code}"))
            except Exception as e:
                self.frame.after(0, lambda: messagebox.showerror("Erro", f"❌ API não respondeu: {str(e)}"))
        
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()

    def forcar_atualizacao(self):
        def sync_thread():
            try:
                response = requests.post(f"{self.api_base}/refresh", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.frame.after(0, lambda: messagebox.showinfo("Sucesso", "✅ Sincronização forçada concluída"))
                    self.frame.after(0, self.load_stats)
                else:
                    raise Exception(f"Status {response.status_code}")
            except Exception as e:
                self.frame.after(0, lambda: messagebox.showerror("Erro", f"❌ Erro na sincronização: {str(e)}"))
        
        thread = threading.Thread(target=sync_thread)
        thread.daemon = True
        thread.start()

    def clear_all_data(self):
        if not self.admin_manager.has_permission():
            messagebox.showerror("Erro", "❌ Apenas administradores podem limpar todos os dados")
            return
            
        if not messagebox.askyesno("Confirmar", "⚠️ Isso irá apagar TODOS os dados. Continuar?"):
            return
        
        def clear_thread():
            try:
                response = requests.post(f"{self.api_base}/limpar", headers=self.headers, timeout=10)
                if response.status_code == 200:
                    self.frame.after(0, lambda: messagebox.showinfo("Sucesso", "✅ Todos os dados foram limpos"))
                    self.frame.after(0, self.load_stats)
                else:
                    raise Exception(f"Status {response.status_code}")
            except Exception as e:
                self.frame.after(0, lambda: messagebox.showerror("Erro", f"❌ Erro ao limpar dados: {str(e)}"))
        
        thread = threading.Thread(target=clear_thread)
        thread.daemon = True
        thread.start()