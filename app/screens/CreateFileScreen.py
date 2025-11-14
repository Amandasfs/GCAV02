# File: app/screens/CreateFileScreen.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from utils.tipo_beneficio import TIPO_BENEFICIO_MAP

class CreateFileScreen:
    def __init__(self, root, api, dados_caixa, nb):
        self.root = tk.Toplevel(root)
        self.api = api
        self.dados_caixa = dados_caixa
        self.root.title("Cadastrar Arquivo")
        self.root.geometry("377x428")
        self.root.configure(bg="white")
        self.primary_color = "#044793"

        # --- TÍTULO ---
        lbl_titulo = tk.Label(
            self.root,
            text="CADASTRAR ARQUIVO",
            font=("System", 26, "bold"),
            fg=self.primary_color,
            bg="white"
        )
        lbl_titulo.place(x=47, y=23)

        # --- BOTÃO FECHAR ---
        try:
            img_close = Image.open("img/closeAzul.png").resize((26, 20), Image.LANCZOS)
            self.close_icon = ImageTk.PhotoImage(img_close)
            lbl_close = tk.Label(self.root, image=self.close_icon, bg="white", cursor="hand2")
            lbl_close.place(x=342, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())
        except:
            lbl_close = tk.Label(self.root, text="X", fg=self.primary_color, bg="white",
                                 font=("Arial", 16, "bold"), cursor="hand2")
            lbl_close.place(x=342, y=15)
            lbl_close.bind("<Button-1>", lambda e: self.handle_close())

        # --- CAMPOS BLOQUEADOS (caixa e nb) ---
        self.nb = ttk.Entry(self.root, font=("System", 12))
        self.nb.place(x=47, y=265, width=181, height=37)
        self.nb.insert(0, str(nb))
        self.nb.configure(state="disabled")

        self.num_caixa = ttk.Entry(self.root, font=("System", 12))
        self.num_caixa.place(x=234, y=314, width=97, height=37)
        self.num_caixa.insert(0, dados_caixa["codigo"])
        self.num_caixa.configure(state="disabled")

        # --- CAMPOS EDITÁVEIS ---
        self.nome_segurado = ttk.Entry(self.root, font=("System", 12))
        self.nome_segurado.place(x=47, y=84, width=284, height=37)
        self.nome_segurado.insert(0, "Segurado")

        self.cpf = ttk.Entry(self.root, font=("System", 12))
        self.cpf.place(x=47, y=134, width=284, height=37)
        self.cpf.insert(0, "CPF")

        lbl_tipo = tk.Label(
            self.root,
            text="Tipo de benefício:",
            fg=self.primary_color,
            bg="white",
            font=("System", 14)
        )
        lbl_tipo.place(x=47, y=184)

        # --- Entry para digitar código do benefício ---
        self.tipo_var = tk.StringVar()
        self.tipo_entry = ttk.Entry(self.root, textvariable=self.tipo_var, font=("System", 12))
        self.tipo_entry.place(x=47, y=211, width=117, height=37)
        self.tipo_entry.insert(0, "Código")
        self.tipo_entry.bind("<KeyRelease>", self.atualizar_view_tipo)

        # --- Campo somente leitura para descrição ---
        self.view_tipo = ttk.Entry(self.root, font=("System", 12))
        self.view_tipo.place(x=169, y=211, width=162, height=37)
        self.view_tipo.insert(0, "")
        self.view_tipo.configure(state="readonly")

        # --- OUTROS CAMPOS ---
        self.ol = ttk.Entry(self.root, font=("System", 12))
        self.ol.place(x=234, y=265, width=97, height=37)
        self.ol.insert(0, "OL")

        self.aps = ttk.Entry(self.root, font=("System", 12))
        self.aps.place(x=47, y=314, width=181, height=37)
        self.aps.insert(0, "APS")

        # --- BOTÃO CADASTRAR ---
        btn_cadastrar = tk.Button(
            self.root,
            text="CADASTRAR",
            font=("System", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            activebackground="#033d73",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.cadastrar_arquivo
        )
        btn_cadastrar.place(x=113, y=367, width=152, height=37)

    def atualizar_view_tipo(self, event=None):
        codigo = self.tipo_var.get().strip()
        descricao = TIPO_BENEFICIO_MAP.get(codigo, "")
        self.view_tipo.configure(state="normal")
        self.view_tipo.delete(0, tk.END)
        self.view_tipo.insert(0, descricao)
        self.view_tipo.configure(state="readonly")

    def cadastrar_arquivo(self):
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

        # --- Validações ---
        if not dados["Segurado"] or dados["Segurado"] == "Segurado":
            messagebox.showwarning("Aviso", "Informe o nome do segurado.")
            return
        if not dados["CPF"] or dados["CPF"] == "CPF":
            messagebox.showwarning("Aviso", "Informe o CPF.")
            return
        if not dados["Tipo Benefício"] or dados["Tipo Benefício"] not in TIPO_BENEFICIO_MAP:
            messagebox.showwarning("Aviso", "Informe um código de benefício válido.")
            return

        # --- Chamada à API ---
        try:
            resposta = self.api.criar_arquivo(dados)
            if resposta.get("sucesso"):
                messagebox.showinfo("Sucesso", "Arquivo cadastrado com sucesso!")
                self.handle_close()
            else:
                messagebox.showerror("Erro", f"Erro ao cadastrar arquivo:\n{resposta.get('mensagem')}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar com API:\n{e}")

    def handle_close(self):
        self.root.destroy()
