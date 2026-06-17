import os
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QObject

class MainView(QObject):
    def __init__(self):
        super().__init__()
        self.loader = QUiLoader()
        
        # Carrega as interfaces base
        self.login_ui = self.carregar_ui('loginIfEncontra.ui')
        self.main_ui = self.carregar_ui('DesignIfEncontra.ui')

    def carregar_ui(self, nome_arquivo):
        # Busca o arquivo UI na pasta atual ou em uma subpasta 'ui'
        caminho_ui = os.path.join(os.path.dirname(__file__), nome_arquivo)
        if not os.path.exists(caminho_ui):
            caminho_ui = os.path.join(os.path.dirname(__file__), 'ui', nome_arquivo)
            
        arquivo_ui = QFile(caminho_ui)
        if not arquivo_ui.open(QFile.ReadOnly):
            print(f"Erro ao carregar {caminho_ui}")
            return None

        # Carrega a janela diretamente do arquivo .ui
        ui = self.loader.load(arquivo_ui, None)
        arquivo_ui.close()
        return ui