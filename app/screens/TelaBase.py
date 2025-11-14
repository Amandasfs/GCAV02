# app/screens/TelaBase.py
import tkinter as tk
from PIL import Image, ImageTk

class TelaBase(tk.Toplevel):
    def __init__(self, master, title="Tela", width=600, height=400):
        super().__init__(master)
        self.master = master
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg="white")
        self.primary_color = "#044793"

        self._criar_botao_fechar()

    def _criar_botao_fechar(self):
        try:
            img_close = Image.open("img/closeAzul.png").resize((20, 26), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)
            lbl_close = tk.Label(self, image=self.close_icon, bg="white", cursor="hand2")
            lbl_close.place(x=self.winfo_width()-50, y=10)
            lbl_close.bind("<Button-1>", lambda e: self.destroy())
        except Exception:
            lbl_close = tk.Label(self, text="X", fg=self.primary_color, bg="white",
                                 font=("System", 16, "bold"), cursor="hand2")
            lbl_close.place(x=self.winfo_width()-50, y=10)
            lbl_close.bind("<Button-1>", lambda e: self.destroy())
