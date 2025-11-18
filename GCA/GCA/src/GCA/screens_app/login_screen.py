# screens_app/login_screen.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import os

class LoginScreen:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.create_login_screen()
        
    def create_login_screen(self):
        # Tela de login
        self.login_frame = tk.Frame(self.root, bg='#667eea')
        self.login_frame.pack(fill='both', expand=True)
        
        # Logo e título
        logo_frame = tk.Frame(self.login_frame, bg='#667eea')
        logo_frame.pack(expand=True, pady=50)
        
        # Carregar e exibir imagem
        self.load_image(logo_frame)
        
        self.logo_label = tk.Label(
            logo_frame,
            text="🏢 GCA SISTEMA",
            font=('Arial', 28, 'bold'),
            fg='white',
            bg='#667eea'
        )
        self.logo_label.pack(pady=10)
        
        self.subtitle_label = tk.Label(
            logo_frame,
            text="Sistema de Gerenciamento de Caixas e Arquivos",
            font=('Arial', 12),
            fg='white',
            bg='#667eea'
        )
        self.subtitle_label.pack(pady=5)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(
            logo_frame,
            orient='horizontal',
            length=300,
            mode='determinate'
        )
        self.progress.pack(pady=30)
        
        # Iniciar animação
        self.animate_progress()
    
    def load_image(self, parent_frame):
        """Carrega e exibe a imagem do logo"""
        try:
            # Caminho da imagem - MODIFIQUE AQUI COM O SEU CAMINHO
            image_path = "img/logoAzul.png"  # Você pode alterar para o caminho da sua imagem
            
            # Verificar se o arquivo existe
            if os.path.exists(image_path):
                # Carregar imagem com PIL
                image = Image.open(image_path)
                
                # Redimensionar mantendo a proporção (ajuste o tamanho conforme necessário)
                max_size = (150, 150)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Converter para PhotoImage
                self.logo_image = ImageTk.PhotoImage(image)
                
                # Criar label para a imagem
                image_label = tk.Label(
                    parent_frame,
                    image=self.logo_image,
                    bg='#667eea'
                )
                image_label.pack(pady=10)
                
            else:
                # Se a imagem não existir, mostrar um placeholder
                self.show_placeholder_image(parent_frame)
                
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            self.show_placeholder_image(parent_frame)
    
    def show_placeholder_image(self, parent_frame):
        """Mostra um placeholder se a imagem não for encontrada"""
        placeholder_label = tk.Label(
            parent_frame,
            text="🖼️",
            font=('Arial', 48),
            fg='white',
            bg='#667eea'
        )
        placeholder_label.pack(pady=10)
        
        info_label = tk.Label(
            parent_frame,
            text="Logo não encontrado\nConfigure o caminho em login_screen.py",
            font=('Arial', 8),
            fg='white',
            bg='#667eea'
        )
        info_label.pack(pady=5)
        
    def animate_progress(self):
        def update_progress(step=0):
            if step <= 100:
                self.progress['value'] = step
                self.root.after(30, lambda: update_progress(step + 1))
            else:
                # Quando a barra completar, mostrar a tela principal
                self.root.after(500, self.show_main_app)
                
        update_progress()
        
    def show_main_app(self):
        # CORREÇÃO: Chamar o callback sem parâmetros
        self.login_frame.destroy()
        self.on_login_success()  # ← SEM parâmetros!