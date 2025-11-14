import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class SelectAltArqScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Alterar Arquivo")
        self.root.geometry("600x400")
        self.root.configure(bg="white")

        # Cor principal
        self.primary_color = "#044793"

        # --- LABEL TÍTULO ---
        lbl_titulo = tk.Label(
            root,
            text="ALTERAR ARQUIVO",
            font=("System", 26, "bold"),
            fg=self.primary_color,
            bg="white"
        )
        lbl_titulo.place(x=57, y=14)

        # --- LABEL SUBTÍTULO ---
        lbl_subtitulo = tk.Label(
            root,
            text="Selecione o arquivo que será alterado",
            font=("System", 14),
            fg=self.primary_color,
            bg="white"
        )
        lbl_subtitulo.place(x=60, y=51)

        # --- CAMPO DE TEXTO (NB) ---
        estilo_entry = ttk.Style()
        estilo_entry.configure("TEntry", padding=5, relief="flat")

        self.input_nb = ttk.Entry(root, font=("System", 12))
        self.input_nb.place(x=80, y=76, width=95, height=37)

        # --- BOTÃO ALTERAR ---
        self.btn_alterar = tk.Button(
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
        self.btn_alterar.place(x=186, y=76, width=95, height=37)

        # --- BOTÃO DE FECHAR (ícone imagem) ---
        try:
            img_close = Image.open("img/closeAzul.png")
            img_close = img_close.resize((19, 19), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)

            lbl_close = tk.Label(
                root,
                image=self.close_icon,
                bg="white",
                cursor="hand2"
            )
            lbl_close.place(x=337, y=14)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

        except Exception as e:
            print("Erro ao carregar imagem:", e)
            # fallback: texto
            lbl_close = tk.Label(
                root,
                text="X",
                fg=self.primary_color,
                bg="white",
                font=("Arial", 14, "bold"),
                cursor="hand2"
            )
            lbl_close.place(x=337, y=14)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

        # Responsividade mínima: centralizar conteúdo se redimensionar
        root.bind("<Configure>", self._ajustar_layout)

    # --- FUNÇÕES DE AÇÃO ---
    def confirmar(self):
        nb = self.input_nb.get().strip()
        if nb:
            print(f"Alterando arquivo NB: {nb}")
            tk.messagebox.showinfo("Alteração", f"Arquivo NB {nb} alterado com sucesso!")
        else:
            tk.messagebox.showwarning("Aviso", "Por favor, insira um número NB.")

    def handle_close(self):
        self.root.destroy()

    def _ajustar_layout(self, event):
        """Mantém tudo centralizado se a janela for redimensionada."""
        largura = event.width
        # Exemplo: se quiser adaptar posicionamento automático depois


if __name__ == "__main__":
    root = tk.Tk()
    app = SelectAltArqScreen(root)
    root.mainloop()
