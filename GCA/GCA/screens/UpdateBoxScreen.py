import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class UpdateBoxScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Alterar Caixa")
        self.root.geometry("381x419")
        self.root.configure(bg="white")

        self.primary_color = "#044793"

        # --- TÍTULO ---
        lbl_titulo = tk.Label(
            root,
            text="ALTERAR CAIXA",
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
        self.cod_caixa = ttk.Entry(root, font=("System", 12))
        self.cod_caixa.place(x=47, y=84, width=181, height=37)
        self.cod_caixa.insert(0, "Código da Caixa")

        self.bloco = ttk.Entry(root, font=("System", 12))
        self.bloco.place(x=234, y=84, width=97, height=37)
        self.bloco.insert(0, "Bloco")

        self.rua = ttk.Entry(root, font=("System", 12))
        self.rua.place(x=47, y=134, width=181, height=37)
        self.rua.insert(0, "Rua")

        self.prateleira = ttk.Entry(root, font=("System", 12))
        self.prateleira.place(x=234, y=134, width=97, height=37)
        self.prateleira.insert(0, "Prateleira")

        self.andar_var = tk.StringVar(value="Selecione Andar")
        self.andar_select = ttk.Combobox(
            root,
            textvariable=self.andar_var,
            values=["SEGUNDO", "TERCEIRO"],
            font=("System", 12),
            state="readonly"
        )
        self.andar_select.place(x=47, y=184, width=284, height=37)

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
            command=self.atualizar_caixa
        )
        btn_atualizar.place(x=113, y=368, width=152, height=37)

    # --- Função atualizar ---
    def atualizar_caixa(self):
        dados = {
            "Código": self.cod_caixa.get(),
            "Bloco": self.bloco.get(),
            "Rua": self.rua.get(),
            "Prateleira": self.prateleira.get(),
            "Andar": self.andar_var.get()
        }

        # Validação simples
        if not dados["Código"] or dados["Código"] == "Código da Caixa":
            messagebox.showwarning("Aviso", "Informe o código da caixa.")
            return

        info = "\n".join([f"{k}: {v}" for k, v in dados.items()])
        messagebox.showinfo("Caixa atualizada!", f"Informações da caixa atualizadas:\n\n{info}")

    # --- Fechar janela ---
    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = UpdateBoxScreen(root)
    root.mainloop()
