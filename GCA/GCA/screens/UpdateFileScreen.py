import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class UpdateFileScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Alterar Arquivo")
        self.root.geometry("381x419")
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
        lbl_titulo.place(x=47, y=23)

        # --- BOTÃO FECHAR ---
        try:
            img_close = Image.open("img/closeAzul.png")
            img_close = img_close.resize((30, 26), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)
            lbl_close = tk.Label(root, image=self.close_icon, bg="white", cursor="hand2")
            lbl_close.place(x=342, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())
        except Exception as e:
            print("Erro ao carregar imagem:", e)
            lbl_close = tk.Label(root, text="X", fg=self.primary_color, bg="white", font=("Arial", 16, "bold"), cursor="hand2")
            lbl_close.place(x=342, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

        # --- CAMPOS ---
        self.nome_segurado = ttk.Entry(root, font=("System", 12))
        self.nome_segurado.place(x=47, y=84, width=284, height=37)
        self.nome_segurado.insert(0, "Segurado")

        self.cpf = ttk.Entry(root, font=("System", 12))
        self.cpf.place(x=47, y=134, width=284, height=37)
        self.cpf.insert(0, "CPF")

        lbl_tipo = tk.Label(
            root,
            text="Tipo de benefício:",
            fg=self.primary_color,
            bg="white",
            font=("System", 14)
        )
        lbl_tipo.place(x=47, y=184)

        # --- CHOICEBOX ---
        self.tipo_var = tk.StringVar(value="Selecione")
        self.tipo_select = ttk.Combobox(
            root,
            textvariable=self.tipo_var,
            values=["Selecione", "Aposentadoria", "Pensão", "Auxílio", "Outros"],
            font=("System", 12),
            state="readonly"
        )
        self.tipo_select.place(x=47, y=211, width=117, height=37)

        # --- viewTipoBeneficioField ---
        self.view_tipo = ttk.Entry(root, font=("System", 12))
        self.view_tipo.place(x=169, y=211, width=162, height=37)
        self.view_tipo.insert(0, "Tipo de Benefício")

        # --- NB e OL ---
        self.nb = ttk.Entry(root, font=("System", 12))
        self.nb.place(x=47, y=265, width=181, height=37)
        self.nb.insert(0, "NB")

        self.ol = ttk.Entry(root, font=("System", 12))
        self.ol.place(x=234, y=265, width=97, height=37)
        self.ol.insert(0, "OL")

        # --- APS e Nº Caixa ---
        self.aps = ttk.Entry(root, font=("System", 12))
        self.aps.place(x=47, y=314, width=181, height=37)
        self.aps.insert(0, "APS")

        self.num_caixa = ttk.Entry(root, font=("System", 12))
        self.num_caixa.place(x=234, y=314, width=97, height=37)
        self.num_caixa.insert(0, "Nº Caixa")

        # --- BOTÃO ATUALIZAR ---
        btn_atualizar = tk.Button(
            root,
            text="ATUALIZAR",
            font=("System", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            activebackground="#033d73",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.atualizar_arquivo
        )
        btn_atualizar.place(x=113, y=368, width=152, height=37)

    # --- Função atualizar ---
    def atualizar_arquivo(self):
        dados = {
            "Segurado": self.nome_segurado.get(),
            "CPF": self.cpf.get(),
            "Tipo Benefício": self.tipo_var.get(),
            "Descrição Tipo": self.view_tipo.get(),
            "NB": self.nb.get(),
            "OL": self.ol.get(),
            "APS": self.aps.get(),
            "Nº Caixa": self.num_caixa.get()
        }

        if not dados["CPF"] or dados["CPF"] == "CPF":
            messagebox.showwarning("Aviso", "Informe o CPF do segurado.")
            return

        info = "\n".join([f"{k}: {v}" for k, v in dados.items()])
        messagebox.showinfo("Arquivo atualizado!", f"Informações atualizadas:\n\n{info}")

    # --- Fechar janela ---
    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = UpdateFileScreen(root)
    root.mainloop()
