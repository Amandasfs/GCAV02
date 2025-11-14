# File: app/screens/SelectAltArqScreen.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from screens.UpdateFileScreen import UpdateFileScreen  # Importa a tela de atualização de arquivo

class SelectAltArqScreen:
    def __init__(self, root, api):
        self.root = root
        self.api = api
        self.root.title("Alterar Arquivo")
        self.root.geometry("600x400")
        self.root.configure(bg="white")
        self.primary_color = "#044793"

        # --- TÍTULO ---
        lbl_titulo = tk.Label(
            root,
            text="ALTERAR ARQUIVO",
            font=("System", 26, "bold"),
            fg=self.primary_color,
            bg="white"
        )
        lbl_titulo.place(x=57, y=14)

        lbl_subtitulo = tk.Label(
            root,
            text="Digite o NB do arquivo que será alterado",
            font=("System", 14),
            fg=self.primary_color,
            bg="white"
        )
        lbl_subtitulo.place(x=60, y=51)

        # --- CAMPO DE TEXTO (NB) ---
        self.input_nb = ttk.Entry(root, font=("System", 12))
        self.input_nb.place(x=80, y=100, width=150, height=37)

        # --- BOTÃO ALTERAR ---
        btn_alterar = tk.Button(
            root,
            text="ALTERAR",
            font=("System", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            activebackground="#033d73",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.confirmar
        )
        btn_alterar.place(x=250, y=100, width=100, height=37)

        # --- BOTÃO FECHAR ---
        try:
            img_close = Image.open("img/closeAzul.png").resize((19, 19), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)
            lbl_close = tk.Label(root, image=self.close_icon, bg="white", cursor="hand2")
            lbl_close.place(x=337, y=14)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())
        except:
            lbl_close = tk.Label(root, text="X", fg=self.primary_color, bg="white",
                                 font=("Arial", 14, "bold"), cursor="hand2")
            lbl_close.place(x=337, y=14)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

    def confirmar(self):
        nb = self.input_nb.get().strip()
        if not nb:
            messagebox.showwarning("Aviso", "Por favor, insira um número NB.")
            return

        # --- Consulta na API ---
        try:
            resposta = self.api.buscar_arquivo_por_nb(nb)
            if resposta.get("sucesso") and resposta.get("arquivo"):
                dados_arquivo = resposta["arquivo"]
                dados_caixa = dados_arquivo.get("caixa", {})
                # Abre a tela de edição passando os dados existentes
                UpdateFileScreen(self.root, self.api, dados_caixa, nb)
                self.root.withdraw()  # opcional: esconde a tela atual
            else:
                messagebox.showerror("Erro", f"Arquivo com NB {nb} não encontrado.")
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar com API:\n{e}")
            self.root.destroy()

    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    class DummyAPI:
        """API simulada para teste"""
        def buscar_arquivo_por_nb(self, nb):
            if nb == "123":
                return {"sucesso": True, "arquivo": {"caixa": {"codigo": "111"}}}
            return {"sucesso": False}

    root = tk.Tk()
    app = SelectAltArqScreen(root, DummyAPI())
    root.mainloop()
