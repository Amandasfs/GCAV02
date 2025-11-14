# app/screens/SelectCadArqScreen.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from screens.CreateFileScreen import CreateFileScreen

class SelectCadArqScreen(tk.Toplevel):
    def __init__(self, master, api):
        super().__init__(master)
        self.api = api
        self.title("Cadastrar Arquivo")
        self.geometry("600x400")
        self.configure(bg="white")
        self.primary_color = "#044793"

        lbl_titulo = tk.Label(self, text="Em qual caixa deseja cadastrar o arquivo?",
                              font=("System", 18, "bold"), fg=self.primary_color, bg="white")
        lbl_titulo.place(x=14, y=12)

        lbl_subtitulo = tk.Label(self, text="Selecione a caixa em que deseja cadastrar o arquivo",
                                 font=("System", 14), fg=self.primary_color, bg="white")
        lbl_subtitulo.place(x=26, y=40)

        self.cod_caixa = ttk.Entry(self, font=("System", 12))
        self.cod_caixa.place(x=26, y=86, width=129, height=40)
        self.cod_caixa.insert(0, "Código da Caixa")

        self.nb_field = ttk.Entry(self, font=("System", 12))
        self.nb_field.place(x=162, y=86, width=129, height=40)
        self.nb_field.insert(0, "XXX.XXX.XXX-X")

        btn_adicionar = tk.Button(self, text="ADICIONAR", font=("System", 12, "bold"),
                                  bg=self.primary_color, fg="white",
                                  activebackground="#033d73", activeforeground="white",
                                  bd=0, relief="flat", cursor="hand2",
                                  command=self.adicionar_arquivo)
        btn_adicionar.place(x=300, y=86, width=95, height=37)

        self._criar_botao_fechar()

    def adicionar_arquivo(self):
        cod_caixa = self.cod_caixa.get().strip()
        nb = self.nb_field.get().strip()

        if not cod_caixa or cod_caixa == "Código da Caixa":
            messagebox.showwarning("Aviso", "Informe o código da caixa.")
            return
        if not nb or nb == "XXX.XXX.XXX-X":
            messagebox.showwarning("Aviso", "Informe o NB do arquivo.")
            return

        try:
            # Consulta API para verificar a caixa e NB
            caixa = self.api.buscar_caixa(cod_caixa)
            if not caixa:
                messagebox.showerror("Erro", "Caixa não encontrada.")
                return

            nb_int = int(nb.replace(".", "").replace("-", ""))  # Ajuste se necessário
            nb_inicial = int(caixa["nb_inicial"])
            nb_final = int(caixa["nb_final"])

            if nb_int < nb_inicial or nb_int > nb_final:
                messagebox.showerror("Erro", "Este arquivo não pertence a essa caixa.")
                self.destroy()
                return

            # Abre tela de cadastro de arquivo passando dados da caixa e NB
            CreateFileScreen(self, api=self.api, dados_caixa=caixa, nb=nb_int)
            self.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar a caixa:\n{e}")

    def _criar_botao_fechar(self):
        try:
            img_close = Image.open("img/closeAzul.png").resize((20, 26), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)
            lbl_close = tk.Label(self, image=self.close_icon, bg="white", cursor="hand2")
            lbl_close.place(x=410, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.destroy())
        except:
            lbl_close = tk.Label(self, text="X", fg=self.primary_color, bg="white",
                                 font=("System", 16, "bold"), cursor="hand2")
            lbl_close.place(x=410, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.destroy())
