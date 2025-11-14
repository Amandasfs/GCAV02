# File: app/screens/HomeScreen.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk

from screens.CreateBoxScreen import CreateBoxScreen
from screens.SelectCadArqScreen import SelectCadArqScreen
from screens.SelectAltArqScreen import SelectAltArqScreen
from screens.SelectAltCaixScreen import SelectAltCaixScreen

# Map de tipo de benefício (numerico para texto)
TIPO_BENEFICIO_MAP = {
    1: "Aposentadoria",
    2: "Pensão",
    3: "Auxílio",
    4: "Outros"
}


class HomeScreen:
    def __init__(self, root, api):
        self.root = root
        self.api = api

        # Remove barra do sistema
        self.root.overrideredirect(True)

        # Cor do fundo
        self.root.configure(bg="#044793")

        # Maximiza automaticamente
        self.root.state("zoomed")

        # Movimentação
        self.offset_x = 0
        self.offset_y = 0
        self.root.bind("<Button-1>", self._get_pos)
        self.root.bind("<B1-Motion>", self._move_window)

        # Canvas para gradiente
        self.canvas_bg = tk.Canvas(self.root, highlightthickness=0, bd=0)
        self.canvas_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.canvas_bg.bind("<Configure>", self._redesenhar_gradiente)

        # Frame principal
        self.frame_principal = tk.Frame(self.canvas_bg, bg="#044793")
        self.canvas_bg.create_window(0, 0, anchor="nw", window=self.frame_principal)
        self.frame_principal.pack(fill="both", expand=True)

        # ================= CABEÇALHO =====================
        header = tk.Frame(self.frame_principal, bg="#0B305A", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        self.logo = self._carregar_imagem("img/logoBranco.png", (150, 55))
        if self.logo:
            tk.Label(header, image=self.logo, bg="#0B305A").pack(side="left", padx=20)

        tk.Label(
            header,
            text="GCA MOGI DAS CRUZES",
            fg="white",
            bg="#0B305A",
            font=("Arial", 24, "bold")
        ).pack(side="left")

        self.close_img = self._carregar_imagem("img/closeBranco.png", (30, 30))
        close_btn = tk.Label(header, image=self.close_img, bg="#0B305A", cursor="hand2")
        close_btn.pack(side="right", padx=20)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        # ================= ÁREA DE BUSCA =====================
        busca_frame = tk.Frame(self.frame_principal, bg="#044793", pady=10)
        busca_frame.pack(fill="x", padx=25, pady=(20, 10))

        tk.Label(
            busca_frame,
            text="Faça uma busca por...",
            bg="#044793",
            fg="white",
            font=("Arial", 18, "italic")
        ).pack(anchor="w", pady=(0, 10))

        filtros_frame = tk.Frame(busca_frame, bg="#044793")
        filtros_frame.pack(fill="x")

        self.filtro = ttk.Combobox(
            filtros_frame,
            values=["Servidor", "Caixa", "Arquivo"],
            font=("Arial", 12)
        )
        self.filtro.set("Escolha um filtro")
        self.filtro.pack(side="left", padx=5, ipadx=10, ipady=5, fill="x", expand=True)

        self.busca_entry = ttk.Entry(filtros_frame, font=("Arial", 12))
        self.busca_entry.pack(side="left", padx=5, ipadx=10, ipady=5, fill="x", expand=True)

        ttk.Button(filtros_frame, text="BUSCAR", width=12, command=self.buscar).pack(side="left", padx=5)
        ttk.Button(filtros_frame, text="BUSCAR TODAS", width=15, command=self.buscar_todas).pack(side="left", padx=5)

        # ========== CORPO PRINCIPAL (TABELA + PAINEL) ==========
        corpo = tk.Frame(self.frame_principal, bg="#044793")
        corpo.pack(fill="both", expand=True, padx=10, pady=15)

        # TABELA inicial
        colunas = ["Coluna 1", "Coluna 2", "Coluna 3",
                   "Coluna 4", "Caixa", "Andar", "Bloco",
                   "Rua", "Prateleira"]
        self.tabela = ttk.Treeview(corpo, columns=colunas, show="headings")
        for c in colunas:
            self.tabela.heading(c, text=c)
            self.tabela.column(c, anchor="center", stretch=True)

        tabela_scroll = ttk.Scrollbar(corpo, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscroll=tabela_scroll.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        tabela_scroll.pack(side="left", fill="y")

        # Painel lateral
        painel = tk.Frame(corpo, bg="#0B305A", width=240)
        painel.pack(side="right", fill="y", padx=10)
        painel.pack_propagate(False)

        self._add_painel_item(painel, "img/caixa/caixaADD.png", "CADASTRAR CAIXA", self.abrir_create_box)
        self._add_painel_item(painel, "img/caixa/caixaALT.png", "ALTERAR CAIXA", self.abrir_update_box)
        self._add_painel_item(painel, "img/arquivo/arquivoADD.png", "CADASTRAR ARQUIVO", self.abrir_select_box_create_file)
        self._add_painel_item(painel, "img/arquivo/arquivoALT.png", "ALTERAR ARQUIVO", self.abrir_update_file)
        self._add_painel_item(painel, "img/relatorio.png", "RELATÓRIO")

    # ================== FUNÇÕES DE BUSCA ==========================
    def buscar(self):
        filtro = self.filtro.get()
        termo = self.busca_entry.get().strip()

        if filtro == "Servidor":
            resultados = self.api.buscar_por_cpf_ou_nome(termo)
            colunas = ["Nome", "Arquivos", "Tipo", "Caixa", "Andar", "Bloco", "Corredor", "Prateleira"]
            self._preencher_tabela(resultados, colunas, map_tipo=True)

        elif filtro == "Arquivo":
            resultados = self.api.buscar_arquivo(termo)
            colunas = ["Segurado", "Tipo", "Caixa", "Andar", "Bloco", "Corredor", "Prateleira"]
            self._preencher_tabela(resultados, colunas, map_tipo=True)

        elif filtro == "Caixa":
            resultados = self.api.buscar_caixa(termo)
            colunas = ["NB Inicial", "NB Final", "Bloco", "Andar", "Corredor", "Prateleira"]
            self._preencher_tabela(resultados, colunas)

        else:
            messagebox.showwarning("Aviso", "Escolha um filtro válido.")

    def buscar_todas(self):
        resultados = self.api.buscar_todas_caixas()
        resultados = sorted(resultados, key=lambda x: int(x.get("codigo", 0)))
        colunas = ["Caixa", "NB Inicial", "NB Final", "Bloco", "Andar", "Corredor", "Prateleira"]
        self._preencher_tabela(resultados, colunas)

    def _preencher_tabela(self, resultados, colunas, map_tipo=False):
        self.tabela["columns"] = colunas
        for c in colunas:
            self.tabela.heading(c, text=c)
            self.tabela.column(c, anchor="center", stretch=True)

        self.tabela.delete(*self.tabela.get_children())
        for r in resultados:
            valores = []
            for c in colunas:
                key = c.lower().replace(" ", "_")
                val = r.get(key, "")
                if map_tipo and c.lower() == "tipo":
                    val = TIPO_BENEFICIO_MAP.get(val, val)
                valores.append(val)
            self.tabela.insert("", "end", values=valores)

    # ================== RESTANTE DO CÓDIGO ==========================
    def _get_pos(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def _move_window(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def _carregar_imagem(self, caminho, tamanho):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            caminho_completo = os.path.join(base_path, caminho)
            img = Image.open(caminho_completo).resize(tamanho, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"[ERRO] {caminho}: {e}")
            return None

    def _add_painel_item(self, painel, img_path, texto, comando=None):
        img = self._carregar_imagem(img_path, (55, 55))
        f = tk.Frame(painel, bg="#0B305A")
        f.pack(pady=12)
        if img:
            lbl = tk.Label(f, image=img, bg="#0B305A", cursor="hand2")
            lbl.image = img
            lbl.pack()
            if comando:
                lbl.bind("<Button-1>", lambda e: comando())
        tk.Label(f, text=texto, bg="#0B305A", fg="white", font=("Arial", 12, "bold")).pack()
        if comando:
            f.bind("<Button-1>", lambda e: comando())

    def _desenhar_gradiente(self, canvas, cor1, cor2):
        canvas.delete("gradiente")
        largura = canvas.winfo_width()
        altura = canvas.winfo_height()
        (r1, g1, b1) = self.root.winfo_rgb(cor1)
        (r2, g2, b2) = self.root.winfo_rgb(cor2)
        r_ratio = (r2 - r1) / altura
        g_ratio = (g2 - g1) / altura
        b_ratio = (b2 - b1) / altura
        for i in range(altura):
            nr = int(r1 + r_ratio * i)
            ng = int(g1 + g_ratio * i)
            nb = int(b1 + b_ratio * i)
            color = f'#{nr//256:02x}{ng//256:02x}{nb//256:02x}'
            canvas.create_line(0, i, largura, i, tags="gradiente", fill=color)

    def _redesenhar_gradiente(self, event):
        self._desenhar_gradiente(self.canvas_bg, "#044793", "#0277BD")

    def abrir_create_box(self):
        self._abrir_tela(CreateBoxScreen, api=self.api)

    def abrir_update_box(self):
        self._abrir_tela(SelectAltCaixScreen, api=self.api)

    def abrir_select_box_create_file(self):
        self._abrir_tela(SelectCadArqScreen, api=self.api)

    def abrir_update_file(self):
        self._abrir_tela(SelectAltArqScreen, api=self.api)

    def _abrir_tela(self, TelaClasse, **kwargs):
        nova = tk.Toplevel(self.root)
        TelaClasse(nova, **kwargs)
