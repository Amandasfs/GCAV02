# File: app/screens/UpdateFileScreen.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from utils.tipo_beneficio import TIPO_BENEFICIO_MAP  # seu mapa de benefícios

class UpdateFileScreen:
    def __init__(self, root, api, dados_arquivo):
        """
        dados_arquivo deve ser um dict com:
        {
            "Segurado": "",
            "CPF": "",
            "Tipo Benefício": "01",
            "NB": "",
            "OL": "",
            "APS": "",
            "Nº Caixa": ""
        }
        """
        self.root = tk.Toplevel(root)
        self.api = api
        self.dados_arquivo = dados_arquivo
        self.primary_color = "#044793"

        self.root.title("Alterar Arquivo")
        self.root.geometry("381x419")
        self.root.configure(bg="white")

        # --- TÍTULO ---
        lbl_titulo = tk.Label(
            self.root,
            text="ALTERAR ARQUIVO",
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

        # --- CAMPOS EDITÁVEIS ---
        self.nome_segurado = ttk.Entry(self.root, font=("System", 12))
        self.nome_segurado.place(x=47, y=84, width=284, height=37)
        self.nome_segurado.insert(0, dados_arquivo.get("Segurado", ""))

        self.cpf = ttk.Entry(self.root, font=("System", 12))
        self.cpf.place(x=47, y=134, width=284, height=37)
        self.cpf.insert(0, dados_arquivo.get("CPF", ""))

        lbl_tipo = tk.Label(
            self.root,
            text="Tipo de benefício:",
            fg=self.primary_color,
            bg="white",
            font=("System", 14)
        )
        lbl_tipo.place(x=47, y=184)

        # --- CHOICEBOX TIPO BENEFÍCIO ---
        self.tipo_var = tk.StringVar()
        self.tipo_select = ttk.Combobox(
            self.root,
            textvariable=self.tipo_var,
            values=list(TIPO_BENEFICIO_MAP.keys()),
            font=("System", 12),
            state="readonly"
        )
        self.tipo_select.place(x=47, y=211, width=117, height=37)
        self.tipo_select.bind("<<ComboboxSelected>>", self.atualizar_view_tipo)

        # Seleciona o tipo atual
        tipo_atual = dados_arquivo.get("Tipo Benefício", "")
        self.tipo_var.set(tipo_atual)

        # --- Campo readonly com descrição ---
        self.view_tipo = ttk.Entry(self.root, font=("System", 12))
        self.view_tipo.place(x=169, y=211, width=162, height=37)
        self.view_tipo.configure(state="readonly")
        self.atualizar_view_tipo()

        # --- NB e OL ---
        self.nb = ttk.Entry(self.root, font=("System", 12))
        self.nb.place(x=47, y=265, width=181, height=37)
        self.nb.insert(0, dados_arquivo.get("NB", ""))
        self.nb.configure(state="disabled")  # não editável

        self.ol = ttk.Entry(self.root, font=("System", 12))
        self.ol.place(x=234, y=265, width=97, height=37)
        self.ol.insert(0, dados_arquivo.get("OL", ""))

        # --- APS e Nº Caixa ---
        self.aps = ttk.Entry(self.root, font=("System", 12))
        self.aps.place(x=47, y=314, width=181, height=37)
        self.aps.insert(0, dados_arquivo.get("APS", ""))

        self.num_caixa = ttk.Entry(self.root, font=("System", 12))
        self.num_caixa.place(x=234, y=314, width=97, height=37)
        self.num_caixa.insert(0, dados_arquivo.get("Nº Caixa", ""))
        self.num_caixa.configure(state="disabled")  # não editável

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
            command=self.atualizar_arquivo
        )
        btn_atualizar.place(x=113, y=368, width=152, height=37)

    def atualizar_view_tipo(self, event=None):
        """Atualiza o campo readonly com a descrição do benefício"""
        tipo = self.tipo_var.get()
        self.view_tipo.configure(state="normal")
        self.view_tipo.delete(0, tk.END)
        self.view_tipo.insert(0, TIPO_BENEFICIO_MAP.get(tipo, ""))
        self.view_tipo.configure(state="readonly")

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

        # --- Envia atualização para API ---
        try:
            resposta = self.api.atualizar_arquivo(dados)
            if resposta.get("sucesso"):
                messagebox.showinfo("Sucesso", "Arquivo atualizado com sucesso!")
                self.handle_close()
            else:
                messagebox.showerror("Erro", f"Erro ao atualizar arquivo:\n{resposta.get('mensagem')}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar com API:\n{e}")

    def handle_close(self):
        self.root.destroy()


if __name__ == "__main__":
    class DummyAPI:
        def atualizar_arquivo(self, dados):
            print("Atualizando:", dados)
            return {"sucesso": True}

    root = tk.Tk()
    dados_exemplo = {
        "Segurado": "João Silva",
        "CPF": "123.456.789-00",
        "Tipo Benefício": "01",
        "NB": "123.456.789-00",
        "OL": "001",
        "APS": "1001",
        "Nº Caixa": "111"
    }
    app = UpdateFileScreen(root, DummyAPI(), dados_exemplo)
    root.mainloop()
