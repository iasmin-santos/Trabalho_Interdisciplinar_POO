import os
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QObject
from PySide6.QtGui import QPixmap 


class MainView(QObject):
    def __init__(self):
        super().__init__()
        self.loader = QUiLoader()
        
        # Carrega as interfaces base
        self.login_ui = self.carregar_ui('loginIfEncontra.ui')
        self.main_ui = self.carregar_ui('DesignIfEncontra.ui')

        # Configura a imagem do logo após carregar a interface de login
        if self.login_ui:
            self.configurar_logo()

    def carregar_ui(self, nome_arquivo):
        caminho_ui = os.path.join(os.path.dirname(__file__), nome_arquivo)
        if not os.path.exists(caminho_ui):
            caminho_ui = os.path.join(os.path.dirname(__file__), 'ui', nome_arquivo)
            
        arquivo_ui = QFile(caminho_ui)
        if not arquivo_ui.open(QFile.ReadOnly):
            print(f"Erro ao carregar {caminho_ui}")
            return None

        ui = self.loader.load(arquivo_ui, None)
        arquivo_ui.close()
        return ui

    def configurar_logo(self):

        caminho_imagem = os.path.join(os.path.dirname(__file__), 'logo_ifmg.png')

        if os.path.exists(caminho_imagem):
            pixmap = QPixmap(caminho_imagem)
            # Acessa o QLabel pelo nome definido no Qt Designer
            self.login_ui.label_logo_placeholder.setPixmap(pixmap)
        else:
            print(f"Erro: A imagem não foi encontrada em {caminho_imagem}")