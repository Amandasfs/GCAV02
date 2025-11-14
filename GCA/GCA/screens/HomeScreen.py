import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

# Importa suas telas de cadastro/alteração
from screens.CreateBoxScreen import CreateBoxScreen
from screens.SelectCadArqScreen import SelectCadArqScreen
from screens.SelectAltArqScreen import SelectAltArqScreen
from screens.SelectAltCaixScreen import SelectAltCaixScreen


class HomeScreen:
    def __init__(self, root, api):
        self.root = root
        self.api = api  # API do GCAApp
        self.root.overrideredirect(True)  # remove toolbar do sistema
        self.root.configure(bg="#044793")

        # Centraliza a janela e ocupa boa parte da tela
        w_tela = self.root.winfo_screenwidth()
        h_tela = self.root.winfo_screenheight()
        largura = int(w_tela * 0.85)
        altura = int(h_tela * 0.85)
        x = (w_tela - largura) // 2
        y = (h_tela - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")

        # Cria gradiente de fundo
        self.canvas_bg = tk.Canvas(self.root, highlightthickness=0)
        self.canvas_bg.pack(fill="both", expand=True)
        self._desenhar_gradiente(self.canvas_bg, "#044793", "#0277BD")

        # Frame principal
        self.frame_principal = tk.Frame(self.canvas_bg, bg="#044793", padx=20, pady=20)
        self.canvas_bg.create_window((0, 0), window=self.frame_principal, anchor="nw")

        # CABEÇALHO
        header = tk.Frame(self.frame_principal, bg="#0B305A", pady=10)
        header.pack(fill="x", pady=(0, 15))

        self.logo = self._carregar_imagem("img/logoBranco.png", (120, 45))
        if self.logo:
            tk.Label(header, image=self.logo, bg="#0B305A").pack(side="left", padx=(15, 10))

        tk.Label(
            header,
            text="GCA MOGI DAS CRUZES",
            fg="white",
            bg="#0B305A",
            font=("Arial", 24, "bold")
        ).pack(side="left")

        self.close_img = self._carregar_imagem("img/closeBranco.png", (25, 25))
        close_btn = tk.Label(header, image=self.close_img, bg="#0B305A", cursor="hand2")
        close_btn.pack(side="right", padx=15)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        # ÁREA DE BUSCA
        busca_frame = tk.Frame(self.frame_principal, bg="#044793", pady=10)
        busca_frame.pack(fill="x", padx=20, pady=(10, 15))

        tk.Label(
            busca_frame,
            text="Faça uma busca por...",
            bg="#044793",
            fg="white",
            font=("Arial", 18, "italic")
        ).pack(anchor="w", pady=(0, 10))

        filtros_frame = tk.Frame(busca_frame, bg="#044793")
        filtros_frame.pack(fill="x")

        self.filtro = ttk.Combobox(filtros_frame, values=["Servidor", "Caixa", "Arquivo"], font=("Arial", 12))
        self.filtro.set("Escolha um filtro")
        self.filtro.pack(side="left", padx=5, ipadx=10, ipady=5, fill="x", expand=True)

        self.busca_entry = ttk.Entry(filtros_frame, font=("Arial", 12))
        self.busca_entry.pack(side="left", padx=5, ipadx=10, ipady=5, fill="x", expand=True)

        ttk.Button(filtros_frame, text="BUSCAR", width=12).pack(side="left", padx=5)
        ttk.Button(filtros_frame, text="BUSCAR TODAS", width=15).pack(side="left", padx=5)

        # ÁREA PRINCIPAL (Tabela + Painel lateral)
        corpo = tk.Frame(self.frame_principal, bg="#044793", pady=10)
        corpo.pack(fill="both", expand=True, padx=10, pady=(10, 20))

        # TABELA
        colunas = ["Coluna 1", "Coluna 2", "Coluna 3", "Coluna 4", "Caixa", "Andar", "Bloco", "Rua", "Prateleira"]
        self.tabela = ttk.Treeview(corpo, columns=colunas, show="headings")
        for c in colunas:
            self.tabela.heading(c, text=c)
            self.tabela.column(c, width=100, anchor="center")
        self.tabela.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # PAINEL LATERAL
        painel = tk.Frame(corpo, bg="#0B305A", width=200, pady=15, padx=10)
        painel.pack(side="right", fill="y")

        # Integração dos fluxos de tela usando callbacks do GCAApp
        self._add_painel_item(painel, "img/caixa/caixaADD.png", "CADASTRAR CAIXA", self.abrir_create_box)
        self._add_painel_item(painel, "img/caixa/caixaALT.png", "ALTERAR CAIXA", self.abrir_update_box)
        self._add_painel_item(painel, "img/arquivo/arquivoADD.png", "CADASTRAR ARQUIVO", self.abrir_select_box_create_file)
        self._add_painel_item(painel, "img/arquivo/arquivoALT.png", "ALTERAR ARQUIVO", self.abrir_update_file)
        self._add_painel_item(painel, "img/relatorio.png", "RELATÓRIO")  # opcional

        # Responsividade: atualizar gradiente ao redimensionar
        self.canvas_bg.bind("<Configure>", self._redesenhar_gradiente)

    # Função corrigida para carregar imagem
    def _carregar_imagem(self, caminho, tamanho):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            caminho_completo = os.path.join(base_path, caminho)
            img = Image.open(caminho_completo)
            img = img.resize(tamanho, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Erro ao carregar {caminho_completo}: {e}")
            return None

    def _add_painel_item(self, painel, img_path, texto, comando=None):
        img = self._carregar_imagem(img_path, (50, 50))
        frame_item = tk.Frame(painel, bg="#0B305A")
        frame_item.pack(pady=10)
        if img:
            lbl = tk.Label(frame_item, image=img, bg="#0B305A", cursor="hand2")
            lbl.image = img
            lbl.pack()
            if comando:
                lbl.bind("<Button-1>", lambda e: comando())
        tk.Label(frame_item, text=texto, bg="#0B305A", fg="white", font=("Arial", 11, "bold")).pack()
        if comando:
            frame_item.bind("<Button-1>", lambda e: comando())

    def _desenhar_gradiente(self, canvas, cor1, cor2):
        canvas.delete("gradiente")
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        (r1, g1, b1) = self.root.winfo_rgb(cor1)
        (r2, g2, b2) = self.root.winfo_rgb(cor2)
        r_ratio = float(r2 - r1) / altura
        g_ratio = float(g2 - g1) / altura
        b_ratio = float(b2 - b1) / altura
        for i in range(altura):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            cor = f'#{nr//256:02x}{ng//256:02x}{nb//256:02x}'
            canvas.create_line(0, i, largura, i, tags=("gradiente",), fill=cor)

    def _redesenhar_gradiente(self, event):
        self._desenhar_gradiente(self.canvas_bg, "#044793", "#0277BD")

    # --- Integração dos fluxos com o backend ---
    def abrir_create_box(self):
        self._abrir_tela(CreateBoxScreen, api=self.api)

    def abrir_update_box(self):
        self._abrir_tela(SelectAltCaixScreen, api=self.api)

    def abrir_select_box_create_file(self):
        self._abrir_tela(SelectCadArqScreen, api=self.api)

    def abrir_update_file(self):
        self._abrir_tela(SelectAltArqScreen, api=self.api)

    def _abrir_tela(self, TelaClasse, **kwargs):
        nova_janela = tk.Toplevel(self.root)
        TelaClasse(nova_janela, **kwargs)
