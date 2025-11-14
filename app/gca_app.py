# File: app/gca_app.py

import tkinter as tk
from tkinter import messagebox

from screens.Loading import LoadingScreen
from screens.HomeScreen import HomeScreen
from screens.CreateBoxScreen import CreateBoxScreen
from screens.SelectCadArqScreen import SelectCadArqScreen
from screens.CreateFileScreen import CreateFileScreen
from screens.SelectAltCaixScreen import SelectAltCaixScreen
from screens.UpdateBoxScreen import UpdateBoxScreen
from screens.SelectAltArqScreen import SelectAltArqScreen
from screens.UpdateFileScreen import UpdateFileScreen


class GCAApp:
    def __init__(self, root):
        # Recebe o root criado no main.py
        self.root = root
        self.root.withdraw()  # Esconde a janela principal inicialmente
        
        # TODO: inicializar sua API aqui quando estiver pronta
        # self.api = MinhaAPI()

        # Tela de loading
        self.loading_root = tk.Toplevel(self.root)
        self.loading = LoadingScreen(self.loading_root)

        # Depois de 2s abre a home
        self.loading_root.after(2000, self.show_home)

    # -------------------------------------------------
    #              TELA INICIAL (HOME)
    # -------------------------------------------------
    def show_home(self):
        self.loading_root.destroy()
        self.root.deiconify()

        self.home_screen = HomeScreen(self.root, api=self.api)

        # Conecta callbacks da home aos métodos do app
        self.home_screen.abrir_create_box = self.abrir_create_box
        self.home_screen.abrir_update_box = self.abrir_update_box
        self.home_screen.abrir_select_box_create_file = self.abrir_create_file_with_validation
        self.home_screen.abrir_update_file = self.abrir_update_file

    # -------------------------------------------------
    #              CRUD DE CAIXAS
    # -------------------------------------------------
    def abrir_create_box(self):
        root = tk.Toplevel(self.root)
        CreateBoxScreen(root, api=self.api)

    def abrir_update_box(self):
        root = tk.Toplevel(self.root)
        SelectAltCaixScreen(root, api=self.api)

    # -------------------------------------------------
    #              CRUD DE ARQUIVOS
    # -------------------------------------------------
    def abrir_create_file_with_validation(self, cod_caixa=None, nb=None):
        """
        Valida NB via API. Se o usuário não fornecer nada,
        abre a tela de seleção primeiro.
        """
        if cod_caixa and nb:
            try:
                nb_int = int(nb)
            except ValueError:
                messagebox.showerror("Erro", "NB inválido!")
                return

            # consulta backend
            caixa_valida = self.api.verificar_nb_na_caixa(cod_caixa, nb_int)

            if caixa_valida:
                root = tk.Toplevel(self.root)
                CreateFileScreen(root, api=self.api)
            else:
                messagebox.showerror(
                    "Erro",
                    "Este arquivo não pertence a essa caixa ou não existe."
                )
        else:
            root = tk.Toplevel(self.root)
            SelectCadArqScreen(root, api=self.api)

    def abrir_update_file(self):
        root = tk.Toplevel(self.root)
        SelectAltArqScreen(root, api=self.api)


if __name__ == "__main__":
    root = tk.Tk()
    GCAApp(root)
    root.mainloop()
