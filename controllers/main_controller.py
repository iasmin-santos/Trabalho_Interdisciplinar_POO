from PySide6.QtWidgets import QMessageBox

class MainController:
    def __init__(self, view, item_model, usuario_model):
        self.view = view
        self.item_model = item_model       # Guarda o modelo dos Itens
        self.usuario_model = usuario_model # Guarda o modelo dos Usuários
        
        # Define self.model como o usuario_model para que a função salvar_novo_usuario() continue funcionando sem alterações
        self.model = self.usuario_model 
        
        # Inicializa a variável do diálogo de cadastro de usuário
        self.dialog_cadastro = None

        # Configura as ações e conexões de eventos
        self.conectar_eventos()

        # Atualiza a listagem de itens na interface
        self.atualizar_grid_itens()
        
        # Inicia pela tela de login
        if self.view.login_ui:
            self.view.login_ui.show()

    def conectar_eventos(self):
        # Login
        if self.view.login_ui:
            self.view.login_ui.btn_entrar.clicked.connect(self.acao_login)

        # Cadastro Novo Usuário 
        # Cadastro Novo Usuário (Apenas liga o evento à função)
        if self.view.login_ui and hasattr(self.view.login_ui, 'label_registro'):
            self.view.login_ui.label_registro.linkActivated.connect(self.acao_abrir_cadastro_usuario)
            
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
        itens = self.item_model.obter_ultimos_itens()
        if not itens:
            print("Nenhum item encontrado no banco para exibir.")
        else:
            print(f"Foram encontrados {len(itens)} itens para preencher o grid.")
            
    def acao_abrir_cadastro_usuario(self):
        # Abre a janela de cadastro de usuário
        self.dialog_cadastro = self.view.carregar_ui('cadastroUsuario.ui')
        if self.dialog_cadastro:
            # Conecta os RadioButtons para alternar o estado dos campos (Aluno vs Funcionário)
            self.dialog_cadastro.rad_aluno.toggled.connect(self.alternar_campos_formulario)
            self.dialog_cadastro.rad_funcionario.toggled.connect(self.alternar_campos_formulario)
            
            # Deixa marcado 'Aluno' por padrão 
            self.dialog_cadastro.rad_aluno.setChecked(True)
            self.alternar_campos_formulario()

            # Conecta os botões da interface
            self.dialog_cadastro.btn_cadastrar.clicked.connect(self.salvar_novo_usuario)
            
            self.dialog_cadastro.exec()

    def alternar_campos_formulario(self):
        # Habilita ou desabilita campos dependendo do tipo de usuário selecionado
        if not self.dialog_cadastro:
            return
            
        is_aluno = self.dialog_cadastro.rad_aluno.isChecked()
        
        # Campos exclusivos de Aluno
        self.dialog_cadastro.txt_curso.setEnabled(is_aluno)
        self.dialog_cadastro.txt_semestre.setEnabled(is_aluno)
        self.dialog_cadastro.txt_ra.setEnabled(is_aluno)
        
        # Campos exclusivos de Funcionário
        self.dialog_cadastro.txt_cargo.setEnabled(not is_aluno)
        
        # Limpa os campos desabilitados para evitar lixo visual
        if is_aluno:
            self.dialog_cadastro.txt_cargo.clear()
        else:
            self.dialog_cadastro.txt_curso.clear()
            self.dialog_cadastro.txt_semestre.clear()
            self.dialog_cadastro.txt_ra.clear()

    def salvar_novo_usuario(self):
        # Coleta as strings, valida as informações básicas e salva no Model
        ui = self.dialog_cadastro
        if not ui:
            return
        
        # Validação de campos obrigatórios 
        if not ui.txt_nome.text().strip() or not ui.txt_email.text().strip() or not ui.txt_senha.text().strip():
            QMessageBox.warning(ui, "Aviso", "Preencha os campos obrigatórios (Nome, E-mail e Senha).")
            return

        # Define os parâmetros de Tipo e Período baseados nos RadioButtons
        tipo = "aluno" if ui.rad_aluno.isChecked() else "funcionario"
        periodo = "Integral" if ui.rad_integral.isChecked() else "Noturno"
        
        # Conversão segura para o Semestre
        semestre_texto = ui.txt_semestre.text().strip()
        semestre_valor = int(semestre_texto) if semestre_texto.isdigit() else None

        # Monta o dicionário estruturado para enviar ao Model
        dados_usuario = {
            'nome': ui.txt_nome.text().strip(),
            'email': ui.txt_email.text().strip(),
            'senha': ui.txt_senha.text(),  
            'nascimento': ui.date_nascimento.date().toString("yyyy-MM-dd"),
            'tipo_usuario': tipo,
            'ra': ui.txt_ra.text().strip() if tipo == "aluno" else None,
            'curso': ui.txt_curso.text().strip() if tipo == "aluno" else None,
            'periodo': periodo,
            'semestre': semestre_valor if tipo == "aluno" else None,
            'cargo': ui.txt_cargo.text().strip() if tipo == "funcionario" else None
        }

        # Envia os dados estruturados para o método cadastrar_usuario da classe Database
        sucesso = self.model.cadastrar_usuario(dados_usuario)
        
        if sucesso:
            QMessageBox.information(ui, "Sucesso", "Usuário cadastrado com sucesso!")
            ui.close()
        else:
            QMessageBox.critical(ui, "Erro", "Não foi possível realizar o cadastro no banco de dados.")
