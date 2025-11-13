import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class CreateBoxScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastrar Caixa")
        self.root.geometry("403x304")
        self.root.configure(bg="white")

        self.primary_color = "#044793"
        self.border_color = "#005cb9"

        # --- TÍTULO ---
        lbl_titulo = tk.Label(
            root,
            text="CADASTRAR CAIXA",
            font=("System", 26, "bold"),
            fg=self.primary_color,
            bg="white"
        )
        lbl_titulo.place(x=86, y=42)

        # --- CAMPOS DE TEXTO ---
        self.cod_caixa = ttk.Entry(root, font=("System", 12))
        self.cod_caixa.place(x=22, y=95, width=124, height=40)
        self.cod_caixa.insert(0, "Código da Caixa")

        self.bloco = ttk.Entry(root, font=("System", 12))
        self.bloco.place(x=154, y=95, width=52, height=40)
        self.bloco.insert(0, "Bloco")

        self.rua = ttk.Entry(root, font=("System", 12))
        self.rua.place(x=220, y=95, width=45, height=40)
        self.rua.insert(0, "Rua")

        self.prateleira = ttk.Entry(root, font=("System", 12))
        self.prateleira.place(x=273, y=95, width=106, height=40)
        self.prateleira.insert(0, "Nº prateleira")

        self.nb_inicial = ttk.Entry(root, font=("System", 12))
        self.nb_inicial.place(x=22, y=143, width=357, height=40)
        self.nb_inicial.insert(0, "NB inicial")

        self.nb_final = ttk.Entry(root, font=("System", 12))
        self.nb_final.place(x=22, y=189, width=357, height=40)
        self.nb_final.insert(0, "NB final")

        # --- CHOICEBOX (Andar) ---
        self.andar_var = tk.StringVar(value="Andar")
        self.andar_select = ttk.Combobox(
            root,
            textvariable=self.andar_var,
            values=["Andar", "SEGUNDO", "TERCEIRO"],
            font=("System", 12),
            state="readonly"
        )
        self.andar_select.place(x=22, y=236, width=232, height=40)

        # --- BOTÃO CADASTRAR ---
        btn_cadastrar = tk.Button(
            root,
            text="CADASTRAR",
            font=("System", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            activebackground="#033d73",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.cadastrar_caixa
        )
        btn_cadastrar.place(x=258, y=236, width=124, height=40)

        # --- BOTÃO FECHAR (Imagem) ---
        try:
            img_close = Image.open("img/closeAzul.png")
            img_close = img_close.resize((28, 37), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)

            lbl_close = tk.Label(root, image=self.close_icon, bg="white", cursor="hand2")
            lbl_close.place(x=361, y=14)
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
            lbl_close.place(x=361, y=14)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

    # --- Função de cadastro ---
    def cadastrar_caixa(self):
        dados = {
            "Código": self.cod_caixa.get(),
            "Bloco": self.bloco.get(),
            "Rua": self.rua.get(),
            "Prateleira": self.prateleira.get(),
            "NB Inicial": self.nb_inicial.get(),
            "NB Final": self.nb_final.get(),
            "Andar": self.andar_var.get()
        }

        if not dados["Código"] or dados["Código"] == "Código da Caixa":
            messagebox.showwarning("Aviso", "Informe o código da caixa.")
            return
        if dados["Andar"] == "Andar":
            messagebox.showwarning("Aviso", "Selecione o andar.")
            return

        info = "\n".join([f"{k}: {v}" for k, v in dados.items()])
        messagebox.showinfo("Caixa cadastrada!", f"Dados salvos com sucesso:\n\n{info}")

    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CreateBoxScreen(root)
    root.mainloop()
