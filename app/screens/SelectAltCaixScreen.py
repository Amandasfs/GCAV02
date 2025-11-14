# File: app/screens/SelectAltCaixScreen.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from screens.UpdateBoxScreen import UpdateBoxScreen  # tela de alteração da caixa


class SelectAltCaixScreen:
    def __init__(self, root, api):
        self.root = root
        self.api = api
        self.root.title("Alterar Caixa")
        self.root.geometry("600x400")
        self.root.configure(bg="white")

        self.primary_color = "#044793"

        # --- LABEL TÍTULO ---
        lbl_titulo = tk.Label(
            root,
            text="ALTERAR CAIXA",
            font=("System", 26, "bold"),
            fg=self.primary_color,
            bg="white"
        )
        lbl_titulo.place(x=47, y=14)

        # --- SUBTÍTULO ---
        lbl_subtitulo = tk.Label(
            root,
            text="Digite o número da caixa que será alterada",
            font=("System", 14),
            fg=self.primary_color,
            bg="white"
        )
        lbl_subtitulo.place(x=33, y=51)

        # --- CAMPO DE TEXTO ---
        estilo_entry = ttk.Style()
        estilo_entry.configure("TEntry", padding=5, relief="flat")

        self.num_caixa = ttk.Entry(root, font=("System", 12))
        self.num_caixa.place(x=47, y=76, width=89, height=37)

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
            command=self.verificar_caixa
        )
        self.btn_alterar.place(x=148, y=76, width=95, height=37)

        # --- BOTÃO FECHAR ---
        try:
            img_close = Image.open("img/closeAzul.png").resize((21, 20), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)
            lbl_close = tk.Label(root, image=self.close_icon, bg="white", cursor="hand2")
            lbl_close.place(x=263, y=14)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())
        except:
            lbl_close = tk.Label(root, text="X", fg=self.primary_color, bg="white",
                                 font=("Arial", 14, "bold"), cursor="hand2")
            lbl_close.place(x=263, y=14)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

    # --- Função de verificação ---
    def verificar_caixa(self):
        caixa_num = self.num_caixa.get().strip()
        if not caixa_num:
            messagebox.showwarning("Aviso", "Por favor, insira o número da caixa.")
            return

        try:
            resposta = self.api.obter_caixa(caixa_num)  # método da API para obter caixa
            if resposta.get("sucesso") and resposta.get("caixa"):
                # abre a tela de alteração passando os dados da caixa
                UpdateBoxScreen(self.root, self.api, resposta["caixa"])
            else:
                messagebox.showerror("Erro", f"Caixa {caixa_num} não encontrada.")
                self.handle_close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar com API:\n{e}")
            self.handle_close()

    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    # aqui você precisaria passar uma instância da API real
    api = None
    app = SelectAltCaixScreen(root, api)
    root.mainloop()
