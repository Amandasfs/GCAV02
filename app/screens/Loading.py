# File: app/screens/Loading.py
import tkinter as tk
from PIL import Image, ImageTk
import os

class LoadingScreen:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Remove a toolbar do sistema
        self.root.configure(bg="#044793")

        # Define tamanho base e centraliza a janela na tela
        largura, altura = 400, 250
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")

        # Permite redimensionamento proporcional
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Frame principal (para centralizar)
        self.frame = tk.Frame(self.root, bg="#044793")
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Caminho relativo da imagem
        caminho_img = os.path.join(os.path.dirname(__file__), "img", "logoBranco.png")

        # Carregar a imagem
        try:
            img_original = Image.open(caminho_img)
            self.img_original = img_original
            self.logo = ImageTk.PhotoImage(img_original)
        except Exception as e:
            print("Erro ao carregar a imagem:", e)
            self.logo = None

        # Label com a imagem
        if self.logo:
            self.logo_label = tk.Label(self.frame, image=self.logo, bg="#044793")
            self.logo_label.pack(expand=True)

        # Label "Carregando..."
        self.label_texto = tk.Label(
            self.frame,
            text="Carregando...",
            bg="#044793",
            fg="white",
            font=("Arial", 14, "italic")
        )
        self.label_texto.pack(pady=(0, 20))

        # Fade-in suave
        self.root.attributes("-alpha", 0.0)
        self.fade_in()

    def fade_in(self):
        alpha = self.root.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.root.attributes("-alpha", alpha)
            self.root.after(50, self.fade_in)
