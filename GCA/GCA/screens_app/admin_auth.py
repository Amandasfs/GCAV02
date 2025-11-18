# screens_app/admin_auth.py
import tkinter as tk
from tkinter import messagebox, ttk

class AdminAuth:
    def __init__(self):
        # Credenciais de administrador (em produção, usar banco de dados seguro)
        self.admin_credentials = {
            'admin': 'admin123',
            'supervisor': 'super123'
        }
        self.is_authenticated = False
        self.current_user = None
        self.on_auth_change = None  # Callback para quando o estado de autenticação mudar
        
    def set_auth_callback(self, callback):
        """Define um callback para quando o estado de autenticação mudar"""
        self.on_auth_change = callback
        
    def show_login_dialog(self, parent):
        """Mostra diálogo de login para administrador"""
        dialog = tk.Toplevel(parent)
        dialog.title("🔐 Acesso Administrativo")
        dialog.geometry("350x250")
        dialog.configure(bg='#f8f9fa')
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Centralizar na tela
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Container principal
        main_frame = tk.Frame(dialog, bg='#f8f9fa', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="🔐 Acesso Administrativo",
            font=('Arial', 16, 'bold'),
            fg='#2c3e50',
            bg='#f8f9fa'
        )
        title_label.pack(pady=(0, 20))
        
        # Frame do formulário
        form_frame = tk.Frame(main_frame, bg='#f8f9fa')
        form_frame.pack(fill='x', pady=10)
        
        # Campo usuário
        user_frame = tk.Frame(form_frame, bg='#f8f9fa')
        user_frame.pack(fill='x', pady=8)
        
        tk.Label(user_frame, text="Usuário Admin:", font=('Arial', 10, 'bold'), 
                bg='#f8f9fa', fg='#2c3e50').pack(anchor='w')
        user_entry = tk.Entry(user_frame, font=('Arial', 11), width=25)
        user_entry.pack(fill='x', pady=5, ipady=3)
        
        # Campo senha
        pass_frame = tk.Frame(form_frame, bg='#f8f9fa')
        pass_frame.pack(fill='x', pady=8)
        
        tk.Label(pass_frame, text="Senha:", font=('Arial', 10, 'bold'), 
                bg='#f8f9fa', fg='#2c3e50').pack(anchor='w')
        pass_entry = tk.Entry(pass_frame, font=('Arial', 11), 
                             show='•', width=25)
        pass_entry.pack(fill='x', pady=5, ipady=3)
        
        # Frame de botões
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(pady=15)
        
        def attempt_login():
            username = user_entry.get().strip()
            password = pass_entry.get()
            
            if self.authenticate(username, password):
                self.is_authenticated = True
                self.current_user = username
                
                # Chamar callback se existir
                if self.on_auth_change:
                    self.on_auth_change(True, username)
                    
                dialog.destroy()
                messagebox.showinfo("Sucesso", f"Bem-vindo, {username}!\n\nAgora você pode:\n• Visualizar itens excluídos\n• Restaurar itens\n• Excluir permanentemente")
                return True
            else:
                messagebox.showerror("Erro", "Credenciais inválidas!\n\nTente:\nUsuário: admin | Senha: admin123\nou\nUsuário: supervisor | Senha: super123")
                user_entry.delete(0, tk.END)
                pass_entry.delete(0, tk.END)
                user_entry.focus()
                return False
        
        def cancel():
            dialog.destroy()
            return False
        
        # Botões
        login_btn = tk.Button(
            button_frame,
            text="🔓 Entrar como Admin",
            font=('Arial', 11, 'bold'),
            fg='white',
            bg='#27ae60',
            relief='flat',
            padx=20,
            pady=8,
            command=attempt_login
        )
        login_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancelar",
            font=('Arial', 10),
            fg='white',
            bg='#95a5a6',
            relief='flat',
            padx=15,
            pady=8,
            command=cancel
        )
        cancel_btn.pack(side='left', padx=5)
        
        # Dicas de credenciais
        hint_label = tk.Label(
            main_frame,
            text="💡 Dica: admin/admin123 ou supervisor/super123",
            font=('Arial', 8),
            fg='#7f8c8d',
            bg='#f8f9fa'
        )
        hint_label.pack(pady=(10, 0))
        
        # Focar no campo de usuário e bind Enter
        user_entry.focus()
        user_entry.bind('<Return>', lambda e: pass_entry.focus())
        pass_entry.bind('<Return>', lambda e: attempt_login())
        
        parent.wait_window(dialog)
        return self.is_authenticated
        
    def authenticate(self, username, password):
        """Autentica o usuário administrador"""
        return (username in self.admin_credentials and 
                self.admin_credentials[username] == password)
    
    def logout(self):
        """Faz logout do administrador"""
        was_authenticated = self.is_authenticated
        user_was = self.current_user
        
        self.is_authenticated = False
        self.current_user = None
        
        # Chamar callback se existir
        if was_authenticated and self.on_auth_change:
            self.on_auth_change(False, user_was)
    
    def has_permission(self):
        """Verifica se o usuário atual tem permissão de administrador"""
        return self.is_authenticated
    
    def get_current_user(self):
        """Retorna o usuário atual"""
        return self.current_user
    
    def show_admin_panel(self, parent):
        """Mostra painel administrativo para gerenciar itens excluídos"""
        if not self.has_permission():
            if not self.show_login_dialog(parent):
                return None
        
        # Criar painel administrativo
        panel = tk.Toplevel(parent)
        panel.title(f"🛠️ Painel Administrativo - {self.current_user}")
        panel.geometry("800x600")
        panel.configure(bg='#f8f9fa')
        
        # Header do painel
        header_frame = tk.Frame(panel, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text=f"🛠️ Painel Administrativo - Logado como: {self.current_user}",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=25)
        
        # Área de conteúdo
        content_frame = tk.Frame(panel, bg='#f8f9fa', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Abas para diferentes funcionalidades administrativas
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill='both', expand=True)
        
        # Aba de itens excluídos
        deleted_frame = tk.Frame(notebook, bg='#f8f9fa')
        notebook.add(deleted_frame, text="🗑️ Itens Excluídos")
        
        # Adicione aqui a lógica para listar itens excluídos
        deleted_label = tk.Label(
            deleted_frame,
            text="Aqui serão listados todos os itens excluídos do sistema\n\nFuncionalidades:\n• Visualizar itens excluídos\n• Restaurar itens\n• Excluir permanentemente",
            font=('Arial', 12),
            fg='#2c3e50',
            bg='#f8f9fa',
            justify='left'
        )
        deleted_label.pack(pady=50)
        
        # Aba de logs
        logs_frame = tk.Frame(notebook, bg='#f8f9fa')
        notebook.add(logs_frame, text="📊 Logs do Sistema")
        
        logs_label = tk.Label(
            logs_frame,
            text="Logs de atividades do sistema",
            font=('Arial', 12),
            fg='#2c3e50',
            bg='#f8f9fa'
        )
        logs_label.pack(pady=50)
        
        # Botão de logout
        logout_btn = tk.Button(
            content_frame,
            text="🚪 Sair do Modo Admin",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='#e74c3c',
            relief='flat',
            padx=15,
            pady=8,
            command=lambda: [panel.destroy(), self.logout()]
        )
        logout_btn.pack(pady=10)
        
        return panel