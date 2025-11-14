# File: app/screens/UpdateBoxScreen.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class UpdateBoxScreen:
    def __init__(self, root, api, dados_caixa):
        self.root = tk.Toplevel(root)
        self.api = api
        self.dados_caixa = dados_caixa
        self.root.title("Alterar Caixa")
        self.root.geometry("381x419")
        self.root.configure(bg="white")
        self.primary_color = "#044793"

        # --- TÍTULO ---
        lbl_titulo = tk.Label(
            self.root,
            text="ALTERAR CAIXA",
            font=("System", 26, "bold"),
            fg=self.primary_color,
            bg="white"
        )
        lbl_titulo.place(x=47, y=23)

        # --- BOTÃO FECHAR ---
        try:
            img_close = Image.open("img/closeAzul.png").resize((30, 26), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)
            lbl_close = tk.Label(self.root, image=self.close_icon, bg="white", cursor="hand2")
            lbl_close.place(x=342, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())
        except:
            lbl_close = tk.Label(self.root, text="X", fg=self.primary_color, bg="white",
                                 font=("Arial", 16, "bold"), cursor="hand2")
            lbl_close.place(x=342, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

        # --- CAMPOS ---
        self.cod_caixa = ttk.Entry(self.root, font=("System", 12))
        self.cod_caixa.place(x=47, y=84, width=181, height=37)

        self.bloco = ttk.Entry(self.root, font=("System", 12))
        self.bloco.place(x=234, y=84, width=97, height=37)

        self.rua = ttk.Entry(self.root, font=("System", 12))
        self.rua.place(x=47, y=134, width=181, height=37)

        self.prateleira = ttk.Entry(self.root, font=("System", 12))
        self.prateleira.place(x=234, y=134, width=97, height=37)

        self.andar_var = tk.StringVar()
        self.andar_select = ttk.Combobox(
            self.root,
            textvariable=self.andar_var,
            values=["SEGUNDO", "TERCEIRO"],
            font=("System", 12),
            state="readonly"
        )
        self.andar_select.place(x=47, y=184, width=284, height=37)

        # --- BOTÃO ATUALIZAR ---
        btn_atualizar = tk.Button(
            self.root,
            text="ATUALIZAR",
            font=("System", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            activebackground="#033d73",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.atualizar_caixa
        )
        btn_atualizar.place(x=113, y=368, width=152, height=37)

        # --- POPULA CAMPOS COM OS DADOS DA CAIXA ---
        self.popular_campos()

    def popular_campos(self):
        """Preenche os campos com os dados da caixa recebida da API"""
        c = self.dados_caixa
        self.cod_caixa.insert(0, c.get("codigo", ""))
        self.bloco.insert(0, c.get("bloco", ""))
        self.rua.insert(0, c.get("rua", ""))
        self.prateleira.insert(0, c.get("prateleira", ""))
        self.andar_var.set(c.get("andar", ""))

    # --- Função atualizar ---
    def atualizar_caixa(self):
        dados = {
            "codigo": self.cod_caixa.get(),
            "bloco": self.bloco.get(),
            "rua": self.rua.get(),
            "prateleira": self.prateleira.get(),
            "andar": self.andar_var.get()
        }

        if not dados["codigo"]:
            messagebox.showwarning("Aviso", "Informe o código da caixa.")
            return

        try:
            resposta = self.api.atualizar_caixa(dados)  # método da API para atualizar
            if resposta.get("sucesso"):
                messagebox.showinfo("Sucesso", "Caixa atualizada com sucesso!")
                self.handle_close()
            else:
                messagebox.showerror("Erro", f"Erro ao atualizar caixa:\n{resposta.get('mensagem')}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar com API:\n{e}")

    # --- Fechar janela ---
    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    api = None  # substituir pela instância real da API
    dados_exemplo = {
        "codigo": "001",
        "bloco": "A",
        "rua": "Rua 1",
        "prateleira": "2",
        "andar": "SEGUNDO"
    }
    app = UpdateBoxScreen(root, api, dados_exemplo)
    root.mainloop()
