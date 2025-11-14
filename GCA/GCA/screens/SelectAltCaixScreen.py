import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class SelectAltCaixScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Alterar Caixa")
        self.root.geometry("600x400")
        self.root.configure(bg="white")

        # Cor principal
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

        # --- LABEL SUBTÍTULO ---
        lbl_subtitulo = tk.Label(
            root,
            text="Selecione a caixa que será alterada",
            font=("System", 14),
            fg=self.primary_color,
            bg="white"
        )
        lbl_subtitulo.place(x=33, y=51)

        # --- CAMPO DE TEXTO (Caixa) ---
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
            command=self.verificar_arquivo
        )
        self.btn_alterar.place(x=148, y=76, width=95, height=37)

        # --- BOTÃO DE FECHAR (ícone imagem) ---
        try:
            img_close = Image.open("img/closeAzul.png")
            img_close = img_close.resize((21, 20), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)

            lbl_close = tk.Label(
                root,
                image=self.close_icon,
                bg="white",
                cursor="hand2"
            )
            lbl_close.place(x=263, y=14)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

        except Exception as e:
            print("Erro ao carregar imagem:", e)
            lbl_close = tk.Label(
                root,
                text="X",
                fg=self.primary_color,
                bg="white",
                font=("Arial", 14, "bold"),
                cursor="hand2"
            )
            lbl_close.place(x=263, y=14)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

    # --- FUNÇÕES DE AÇÃO ---
    def verificar_arquivo(self):
        caixa = self.num_caixa.get().strip()
        if caixa:
            messagebox.showinfo("Alterar Caixa", f"Caixa {caixa} selecionada para alteração!")
        else:
            messagebox.showwarning("Aviso", "Por favor, insira o número da caixa.")

    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SelectAltCaixScreen(root)
    root.mainloop()
