import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class SelectCadArqScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastrar Arquivo")
        self.root.geometry("600x400")
        self.root.configure(bg="white")

        self.primary_color = "#044793"

        # --- LABEL TÍTULO ---
        lbl_titulo = tk.Label(
            root,
            text="Em qual caixa deseja cadastrar o arquivo?",
            font=("System", 18, "bold"),
            fg=self.primary_color,
            bg="white"
        )
        lbl_titulo.place(x=14, y=12)

        # --- LABEL SUBTÍTULO ---
        lbl_subtitulo = tk.Label(
            root,
            text="Selecione a caixa em que deseja cadastrar o arquivo",
            font=("System", 14),
            fg=self.primary_color,
            bg="white"
        )
        lbl_subtitulo.place(x=26, y=40)

        # --- CAMPO Código da Caixa ---
        self.cod_caixa = ttk.Entry(root, font=("System", 12))
        self.cod_caixa.place(x=26, y=86, width=129, height=40)
        self.cod_caixa.insert(0, "Código da Caixa")

        # --- CAMPO NB ---
        self.nb_field = ttk.Entry(root, font=("System", 12))
        self.nb_field.place(x=162, y=86, width=129, height=40)
        self.nb_field.insert(0, "XXX.XXX.XXX-X")

        # --- BOTÃO ADICIONAR ---
        btn_adicionar = tk.Button(
            root,
            text="ADICIONAR",
            font=("System", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            activebackground="#033d73",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.adicionar_arquivo
        )
        btn_adicionar.place(x=300, y=86, width=95, height=37)

        # --- BOTÃO DE FECHAR (Imagem) ---
        try:
            img_close = Image.open("img/closeAzul.png")
            img_close = img_close.resize((20, 26), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)

            lbl_close = tk.Label(
                root,
                image=self.close_icon,
                bg="white",
                cursor="hand2"
            )
            lbl_close.place(x=410, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

        except Exception as e:
            print("Erro ao carregar imagem:", e)
            lbl_close = tk.Label(
                root,
                text="X",
                fg=self.primary_color,
                bg="white",
                font=("Arial", 16, "bold"),
                cursor="hand2"
            )
            lbl_close.place(x=410, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

    # --- AÇÕES ---
    def adicionar_arquivo(self):
        cod_caixa = self.cod_caixa.get().strip()
        nb = self.nb_field.get().strip()

        if not cod_caixa or cod_caixa == "Código da Caixa":
            messagebox.showwarning("Aviso", "Informe o código da caixa.")
            return
        if not nb or nb == "XXX.XXX.XXX-X":
            messagebox.showwarning("Aviso", "Informe o NB do arquivo.")
            return

        messagebox.showinfo(
            "Arquivo Cadastrado",
            f"Arquivo NB {nb} cadastrado na caixa {cod_caixa}!"
        )

    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app =SelectCadArqScreen(root)
    root.mainloop()

