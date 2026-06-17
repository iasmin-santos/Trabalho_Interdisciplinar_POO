class MainController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        
        self.conectar_eventos()
        self.atualizar_grid_itens()
        
        # Inicia pela tela de login
        if self.view.login_ui:
            self.view.login_ui.show()

    def conectar_eventos(self):
        # Login
        if self.view.login_ui:
            self.view.login_ui.btn_entrar.clicked.connect(self.acao_login)
            
        # Tela Principal
        if self.view.main_ui:
            self.view.main_ui.btn_perdi.clicked.connect(self.acao_perdi_item) 
            self.view.main_ui.btn_encontrei.clicked.connect(self.acao_encontrei_item) 

    def acao_login(self):
        # Simulação de clique no login
        print("Acesso liberado. Fechando login e abrindo interface principal...")
        self.view.login_ui.close()
        self.view.main_ui.show()

    def acao_perdi_item(self):
        self.dialog_perdido = self.view.carregar_ui('perdido.ui')
        if self.dialog_perdido:
            self.dialog_perdido.btn_cancelar.clicked.connect(self.dialog_perdido.close) 
            self.dialog_perdido.btn_cadastrar.clicked.connect(self.salvar_item_perdido) 
            self.dialog_perdido.exec() # <--- Faltava isso! 

    def acao_encontrei_item(self):
        # Abre o formulário de item encontrado sobre a janela principal
        self.dialog_encontrado = self.view.carregar_ui('cadastro.ui')
        if self.dialog_encontrado:
            self.dialog_encontrado.btn_cancelar.clicked.connect(self.dialog_encontrado.close) 
            self.dialog_encontrado.btn_cadastrar.clicked.connect(self.salvar_item_encontrado) 
            self.dialog_encontrado.exec()

    def salvar_item_perdido(self):
        print("Lógica para salvar item perdido acionada.")
        self.dialog_perdido.close()

    def salvar_item_encontrado(self):
        print("Lógica para salvar item achado acionada.")
        self.dialog_encontrado.close()

    def atualizar_grid_itens(self):
        itens = self.model.obter_ultimos_itens()
        if not itens:
            print("Nenhum item encontrado no banco para exibir.")
        else:
            print(f"Foram encontrados {len(itens)} itens para preencher o grid.")
            
