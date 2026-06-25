import shutil
import os
import time
from PySide6.QtWidgets import QMessageBox, QListWidgetItem, QFileDialog
from PySide6.QtCore import Qt, QObject, QEvent

class MainController(QObject):  # <-- Altere aqui para herdar de QObject
    def __init__(self, view, item_model, usuario_model):
        super().__init__()  # <-- OBRIGATÓRIO: Inicializa o QObject interno do Qt
        self.view = view
        self.item_model = item_model
        self.usuario_model = usuario_model
        
        self.dialog_perdido = None
        self.dialog_encontrado = None
        self.foto_selecionada_path = None
        
        # Mantém self.model referenciando usuario_model para o cadastro funcionar
        self.model = self.usuario_model 

        # Variável temporária para armazenar a foto selecionada na sessão atual
        self.foto_selecionada_path = None
        
        # Inicializa as variáveis dos diálogos/janelas
        self.dialog_cadastro = None
        self.dialog_perdido = None
        self.dialog_encontrado = None

        # Configura as ações e conexões de eventos
        self.conectar_eventos()

        # Atualiza a listagem de itens puxando os dados reais do SQLite ao iniciar
        self.atualizar_grid_itens()
        
        # Inicia pela tela de login
        if self.view.login_ui:
            self.view.login_ui.show()

    def conectar_eventos(self):
        # Login
        if self.view.login_ui:
            self.view.login_ui.btn_entrar.clicked.connect(self.acao_login)

        # Cadastro Novo Usuário 
        if self.view.login_ui and hasattr(self.view.login_ui, 'label_registro'):
            label = self.view.login_ui.label_registro

            # Isso força o sinal 'linkActivated' do PySide6 a funcionar!
            texto_html = (
                '<html><body><p align="center">'
                'Não tem conta ainda? '
                '<a href="#cadastrar" style="color: #278c43; font-weight: bold; text-decoration: none;">'
                'Cadastre-se aqui</a>'
                '</p></body></html>'
            )
            label.setText(texto_html)

            # Garante que o Qt trate o clique internamente no Python em vez de abrir o navegador
            label.setOpenExternalLinks(False)
            label.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
            
            # Altera o cursor para a "mãozinha" de clique
            from PySide6.QtGui import QCursor
            label.setCursor(QCursor(Qt.PointingHandCursor))

            # Conecta o sinal que agora vai disparar de verdade
            label.linkActivated.connect(self.acao_abrir_cadastro_usuario)
            
        # Tela Principal (Ações e Barra de Busca)
        if self.view.main_ui:
            self.view.main_ui.btn_perdi.clicked.connect(self.acao_perdi_item) 
            self.view.main_ui.btn_encontrei.clicked.connect(self.acao_encontrei_item)
            
            # Conecta em tempo real o ato de digitar na barra de busca ao filtro com o banco
            if hasattr(self.view.main_ui, 'lineEdit_busca'):
                self.view.main_ui.lineEdit_busca.textChanged.connect(self.filtrar_itens)

    def acao_login(self):
        ui = self.view.login_ui
        if not ui:
            return

        # 1. Coleta os dados usando os nomes reais do seu arquivo .ui
        email = ui.lineEdit_email.text().strip()
        senha = ui.lineEdit_senha.text()

        # 2. Validação básica de campos vazios
        if not email or not senha:
            QMessageBox.warning(ui, "Aviso", "Por favor, preencha o e-mail e a senha.")
            return

        # 3. Chama a função de autenticação do seu UsuarioModel
        usuario_valido = self.usuario_model.verificar_login(email, senha)

        if usuario_valido:
            print("Acesso liberado de verdade! Abrindo interface principal...")
            ui.close()
            self.view.main_ui.show()
        else: 
            print("Acesso negado. Verifique suas credenciais.")
            QMessageBox.critical(ui, "Erro de Acesso", "E-mail ou senha incorretos.")

    def acao_perdi_item(self):
        self.dialog_perdido = self.view.carregar_ui('perdido.ui')
        if self.dialog_perdido:
            self.foto_selecionada_path = None
            self.dialog_perdido.btn_cancelar.clicked.connect(self.dialog_perdido.close) 
            self.dialog_perdido.btn_cadastrar.clicked.connect(self.salvar_item_perdido) 
            
            # --- FILTRO DE EVENTOS NATIVO (PERDIDO) ---
            if hasattr(self.dialog_perdido, 'label_foto'):
                label = self.dialog_perdido.label_foto
                label.setAttribute(Qt.WA_TransparentForMouseEvents, False)
                
                from PySide6.QtGui import QCursor
                label.setCursor(QCursor(Qt.PointingHandCursor))
                
                # Diz ao Qt para monitorizar este label
                label.installEventFilter(self)
                label.setProperty("janela_mae", self.dialog_perdido)

            self.dialog_perdido.exec()

    def acao_encontrei_item(self):
        self.dialog_encontrado = self.view.carregar_ui('cadastro.ui')
        if self.dialog_encontrado:
            self.foto_selecionada_path = None
            self.dialog_encontrado.btn_cancelar.clicked.connect(self.dialog_encontrado.close) 
            self.dialog_encontrado.btn_cadastrar.clicked.connect(self.salvar_item_encontrado) 
            
            # --- FILTRO DE EVENTOS NATIVO (ACHADO) ---
            if hasattr(self.dialog_encontrado, 'label_foto'):
                label = self.dialog_encontrado.label_foto
                label.setAttribute(Qt.WA_TransparentForMouseEvents, False)
                
                from PySide6.QtGui import QCursor
                label.setCursor(QCursor(Qt.PointingHandCursor))
                
                label.installEventFilter(self)
                label.setProperty("janela_mae", self.dialog_encontrado)

            self.dialog_encontrado.exec()

    def salvar_item_perdido(self):
        """Captura todas as informações preenchidas na interface 'perdido.ui'."""
        ui = self.dialog_perdido
        if not ui:
            return

        # Coleta de dados com fallbacks de segurança
        titulo = ui.txt_nome_item.text().strip() if hasattr(ui, 'txt_nome_item') else ""
        detalhes = ui.txt_descricao.toPlainText().strip() if hasattr(ui, 'txt_descricao') else ""
        local_item = ui.txt_local.text().strip() if hasattr(ui, 'txt_local') else "Não especificado"
        
        # Coleta campos de data/hora se existirem na sua tela de perdido
        hora_perda = ui.timeEdit.time().toString("HH:mm") if hasattr(ui, 'timeEdit') else ""

        if not titulo:
            QMessageBox.warning(ui, "Aviso", "Por favor, preencha o campo Nome do Item.")
            return

        # Monta uma descrição rica com tudo o que foi digitado
        descricao_completa = f"{detalhes}\n(Hora provável da perda: {hora_perda})" if hora_perda else detalhes

        dados_item = {
            'titulo': titulo,
            'descricao': descricao_completa,
            'local': local_item if local_item else "Campus",
            'tipo_item': 'Perdido', # Primeira letra maiúscula por causa do CHECK do banco
            'status': 'Ativo',
            'id_usuario': None # Pode vincular o ID do usuário logado aqui no futuro
        }

        # --- PROCESSO DE CÓPIA DA FOTO ---
        caminho_foto_banco = None
        if self.foto_selecionada_path and os.path.exists(self.foto_selecionada_path):
            try:
                # GARANTE QUE A PASTA EXISTE ANTES DE COPIAR!
                if not os.path.exists("fotos_itens"):
                    os.makedirs("fotos_itens")
                
                nome_arquivo = f"{int(time.time())}_{os.path.basename(self.foto_selecionada_path)}"
                destino = os.path.join("fotos_itens", nome_arquivo)
                
                shutil.copy(self.foto_selecionada_path, destino)
                caminho_foto_banco = destino
            except Exception as e:
                print(f"Erro ao processar imagem: {e}")

        # Adicione o 'foto_path' ao seu dicionário de dados do item:
        dados_item = {
            'titulo': titulo, # ou titulo
            'descricao': descricao_completa,
            'local': local_item,
            'tipo_item': 'Achado', # ou 'Perdido'
            'status': 'Ativo',
            'foto_path': caminho_foto_banco, # <- INJETADO NO BANCO AQUI
            'id_usuario': None
        }

        if self.item_model.cadastrar_item(dados_item):
            QMessageBox.information(ui, "Sucesso", "Item cadastrado como perdido com sucesso!")
            ui.close()
            self.atualizar_grid_itens()
        else:
            QMessageBox.critical(ui, "Erro", "Erro ao salvar no banco de dados.")

    def salvar_item_encontrado(self):
        """Captura absolutamente tudo preenchido na interface de Achados ('cadastro.ui')."""
        ui = self.dialog_encontrado
        if not ui:
            return

        # Captura os dados baseado na sua imagem
        quem_encontrou = ui.txt_nome_encontrou.text().strip() if hasattr(ui, 'txt_nome_encontrou') else "Anônimo"
        categoria = ui.txt_categoria.text().strip() if hasattr(ui, 'txt_categoria') else ""
        local_item = ui.txt_local.text().strip() if hasattr(ui, 'txt_local') else ""
        
        # Captura a Data e a Hora selecionadas nos seletores do Qt
        data_achado = ui.dateEdit.date().toString("dd/MM/yyyy") if hasattr(ui, 'dateEdit') else ""
        hora_achado = ui.timeEdit.time().toString("HH:mm") if hasattr(ui, 'timeEdit') else ""

        if not categoria:
            QMessageBox.warning(ui, "Aviso", "Por favor, preencha o Tipo de Item / Categoria.")
            return

        if not local_item:
            QMessageBox.warning(ui, "Aviso", "Por favor, preencha o Local Onde Encontrou.")
            return

        # Compõe o campo descrição unificando tudo que a pessoa preencheu
        descricao_completa = (
            f"Encontrado por: {quem_encontrou}. "
            f"Data: {data_achado} às {hora_achado}."
        )

        dados_item = {
            'titulo': categoria,
            'descricao': descricao_completa,
            'local': local_item,
            'tipo_item': 'Achado', # Respeitando o CHECK ('Achado')
            'status': 'Ativo',
            'id_usuario': None
        }

        # --- PROCESSO DE CÓPIA DA FOTO ---
        caminho_foto_banco = None
        if self.foto_selecionada_path and os.path.exists(self.foto_selecionada_path):
            try:
                # GARANTE QUE A PASTA EXISTE ANTES DE COPIAR!
                if not os.path.exists("fotos_itens"):
                    os.makedirs("fotos_itens")
                
                nome_arquivo = f"{int(time.time())}_{os.path.basename(self.foto_selecionada_path)}"
                destino = os.path.join("fotos_itens", nome_arquivo)
                
                shutil.copy(self.foto_selecionada_path, destino)
                caminho_foto_banco = destino
            except Exception as e:
                print(f"Erro ao processar imagem: {e}")

        # Adicione o 'foto_path' ao seu dicionário de dados do item:
        dados_item = {
            'titulo': categoria, # ou titulo
            'descricao': descricao_completa,
            'local': local_item,
            'tipo_item': 'Achado', # ou 'Perdido'
            'status': 'Ativo',
            'foto_path': caminho_foto_banco, # <- INJETADO NO BANCO AQUI
            'id_usuario': None
        }

        if self.item_model.cadastrar_item(dados_item):
            QMessageBox.information(ui, "Sucesso", "Item cadastrado com sucesso!")
            ui.close()
            self.atualizar_grid_itens()
        else:
            QMessageBox.critical(ui, "Erro", "Erro ao salvar o item encontrado no banco de dados.")

    def clique_na_foto(self, event):
        """Função nativa que responde ao clique do mouse recebendo o evento corretamente."""
        # Recupera quem foi o QLabel clicado
        label_clicado = self.sender() if self.sender() else None
        
        # Se o sender do Qt falhar, tentamos identificar pelo objeto ativo
        if not label_clicado and hasattr(self, 'dialog_perdido') and self.dialog_perdido:
            if hasattr(self.dialog_perdido, 'label_foto') and self.dialog_perdido.label_foto.underMouse():
                label_clicado = self.dialog_perdido.label_foto
        if not label_clicado and hasattr(self, 'dialog_encontrado') and self.dialog_encontrado:
            if hasattr(self.dialog_encontrado, 'label_foto') and self.dialog_encontrado.label_foto.underMouse():
                label_clicado = self.dialog_encontrado.label_foto

        if label_clicado:
            # Puxa a janela mãe correspondente
            janela_pai = label_clicado.property("janela_mae")
            
            # Executa a abertura forçada da janela de arquivos
            self.abrir_seletor_arquivos(janela_pai, label_clicado)

    def abrir_seletor_arquivos(self, janela_atual, label_alvo):
        """Abre a janela de seleção de ficheiros e renderiza a imagem."""
        from PySide6.QtGui import QPixmap
        
        arquivo, _ = QFileDialog.getOpenFileName(
            janela_atual,
            "Selecionar Foto do Item",
            "",
            "Imagens (*.png *.jpg *.jpeg)"
        )
        
        if arquivo:
            self.foto_selecionada_path = arquivo
            print(f"Ficheiro escolhido: {arquivo}")
            
            pixmap = QPixmap(arquivo)
            pixmap_redimensionado = pixmap.scaled(
                label_alvo.width(), 
                label_alvo.height(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            label_alvo.setPixmap(pixmap_redimensionado)
            label_alvo.setAlignment(Qt.AlignCenter)

    def selecionar_foto(self, janela_atual, label_alvo):
        """Abre a janela nativa de arquivos do Windows."""
        arquivo, _ = QFileDialog.getOpenFileName(
            janela_atual,
            "Selecionar Foto do Item",
            "",
            "Imagens (*.png *.jpg *.jpeg)"
        )
        
        if arquivo:
            self.foto_selecionada_path = arquivo
            print(f"Foto detectada com sucesso: {arquivo}")
            
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(arquivo)
            pixmap_redimensionado = pixmap.scaled(
                label_alvo.width(), 
                label_alvo.height(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            label_alvo.setPixmap(pixmap_redimensionado)
            label_alvo.setAlignment(Qt.AlignCenter)

    def evento_arrastar_entrar(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def evento_soltar_foto(self, event, label_alvo):
        urls = event.mimeData().urls()
        if urls:
            arquivo = urls[0].toLocalFile()
            if arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.definir_foto_no_label(arquivo, label_alvo)
                event.acceptProposedAction()

    def definir_foto_no_label(self, arquivo_path, label_alvo):
        from PySide6.QtGui import QPixmap
        self.foto_selecionada_path = arquivo_path
        
        pixmap = QPixmap(arquivo_path)
        pixmap_redimensionado = pixmap.scaled(
            label_alvo.width(), 
            label_alvo.height(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        label_alvo.setPixmap(pixmap_redimensionado)
        label_alvo.setAlignment(Qt.AlignCenter)

    def eventFilter(self, watched, event):
        """Interceta nativamente o clique do rato no QLabel da foto."""
        # Se o evento for um clique com o botão esquerdo do rato
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if watched.objectName() == "label_foto":
                print("Clique intercetado com sucesso no QLabel!")
                
                janela_pai = watched.property("janela_mae")
                self.abrir_seletor_arquivos(janela_pai, watched)
                return True  # Indica ao Qt que o evento foi resolvido aqui
                
        return super().eventFilter(watched, event)
        
    def atualizar_grid_itens(self, itens=None):
        """Atualiza a lista principal importando o Card corretamente da pasta views."""
        try:
            if itens is None:
                itens = self.item_model.obter_todos_itens()

            from PySide6.QtWidgets import QListWidget, QListWidgetItem
            
            # Localiza o componente de lista na tela de forma dinâmica
            lista_widget = self.view.findChild(QListWidget)
            if not lista_widget and hasattr(self.view, 'main_ui'):
                lista_widget = self.view.main_ui.findChild(QListWidget)

            if lista_widget:
                lista_widget.clear()  # Limpa a tela para recarregar
                
                # --- CORREÇÃO DO IMPORT: Aponta para a pasta views ---
                from views.item_card import ItemCardWidget
                
                for item in itens:
                    item_container = QListWidgetItem(lista_widget)
                    
                    # Cria o card passando o objeto com as propriedades corrigidas
                    card = ItemCardWidget(item)
                    
                    # Define o tamanho correto e injeta na lista
                    item_container.setSizeHint(card.sizeHint())
                    lista_widget.setItemWidget(item_container, card)
                
                print(f"Grid atualizado com sucesso! {len(itens)} cards carregados.")
            else:
                print("Aviso: Nenhum componente QListWidget foi localizado na interface gráfica.")

        except Exception as e:
            print(f"Erro crítico ao renderizar os cards na tela: {e}")

    def filtrar_itens(self):
        """Lê em tempo real a barra de busca e faz o filtro direto nas colunas do banco."""
        if not self.view.main_ui or not hasattr(self.view.main_ui, 'lineEdit_busca'):
            return

        texto_busca = self.view.main_ui.lineEdit_busca.text().strip()
        
        # Se o usuário apagar o que digitou, recarrega todos os itens originais do banco
        if not texto_busca:
            itens_filtrados = self.item_model.obter_todos_itens()
        else:
            # Caso contrário, executa a query 'LIKE %termo%' estruturada no ItemModel
            itens_filtrados = self.item_model.buscar_itens_por_filtro(texto_busca)
        
        # Atualiza a interface gráfica (os cards do seu QListWidget)
        self.atualizar_grid_itens(itens_filtrados)
        
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
