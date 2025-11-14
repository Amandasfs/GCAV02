# File: app/screens/CreateBoxScreen.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class CreateBoxScreen:
    def __init__(self, root, api):
        self.root = root
        self.api = api  # API passada do main
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

    # --- Função de cadastro com API ---
    def cadastrar_caixa(self):
        dados = {
            "codigo": self.cod_caixa.get().strip(),
            "bloco": self.bloco.get().strip(),
            "rua": self.rua.get().strip(),
            "prateleira": self.prateleira.get().strip(),
            "nb_inicial": self.nb_inicial.get().strip(),
            "nb_final": self.nb_final.get().strip(),
            "andar": self.andar_var.get().strip()
        }

        # Validações
        if not dados["codigo"] or dados["codigo"] == "Código da Caixa":
            messagebox.showwarning("Aviso", "Informe o código da caixa.")
            return
        if dados["andar"] == "Andar":
            messagebox.showwarning("Aviso", "Selecione o andar.")
            return

        try:
            # Chama a API
            resposta = self.api.criar_caixa(dados)
            if resposta["sucesso"]:
                messagebox.showinfo("Sucesso", "Caixa cadastrada com sucesso!")
                self.handle_close()
            else:
                messagebox.showerror("Erro", f"Falha ao cadastrar caixa:\n{resposta['mensagem']}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao conectar com a API:\n{e}")

    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    # Apenas para teste isolado
    class DummyAPI:
        def criar_caixa(self, dados):
            print("Chamando API com:", dados)
            return {"sucesso": True, "mensagem": "OK"}

    root = tk.Tk()
    app = CreateBoxScreen(root, api=DummyAPI())
    root.mainloop()
