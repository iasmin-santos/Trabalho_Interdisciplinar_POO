import shutil
import os
import time
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QMessageBox, QListWidgetItem, QFileDialog, QPushButton
from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtGui import QCursor, QPixmap
from views.item_card import ItemCardWidget
from views.admin_view import AdminView

class MainController(QObject):  
    """
    Controlador principal do sistema aplicando o padrão estrutural MVC,
    conectando diretamente a visualização (MainView) aos modelos de dados.
    """
    def __init__(self, view, item_model, usuario_model):
        super().__init__()  
        
        # Atributos de instância encapsulando as camadas do MVC 
        self.view = view
        self.item_model = item_model
        self.usuario_model = usuario_model

        
        # Variáveis de controle de sessão e janelas flutuantes
        self.foto_selecionada_path = None
        self.dialog_cadastro = None
        self.dialog_perdido = None
        self.dialog_encontrado = None
        self.admin_view = None

        # Inicialização das rotinas e conexões de eventos
        self.conectar_eventos()
        self.atualizar_grid_itens()
        
        # Inicializa o fluxo de exibição da interface gráfica
        if self.view.login_ui:
            self.view.login_ui.show()

    def conectar_eventos(self):
        """Mapeia os cliques dos botões da View para os métodos do Controller."""
      # --- LOGIN ---
        if self.view.login_ui:
            # Tenta localizar qualquer botão de login gerado pelo XML
            btn_orig = (self.view.login_ui.findChild(QPushButton, "btn_entrar") or 
                        self.view.login_ui.findChild(QPushButton, "btn_entrar_admin") or 
                        getattr(self.view.login_ui, "btn_entrar", None))
            
            if btn_orig and btn_orig.parentWidget():
                parent = btn_orig.parentWidget()
                
                # Esconde o botão original do XML para não haver sobreposição
                btn_orig.hide()
                
                from PySide6.QtWidgets import QVBoxLayout
                
                # Aproveita o layout existente do container ou cria um novo
                layout = parent.layout()
                if not layout:
                    layout = QVBoxLayout(parent)
                
                # Instancia os dois novos botões dinamicamente no mesmo container
                self.btn_entrar_usr = QPushButton("Entrar como Usuário")
                self.btn_entrar_adm = QPushButton("Acesso Administrativo (Servidor)")
                
                # Estilização verde consistente
                estilo_btn = """
                    QPushButton {
                        background-color: #278c43;
                        color: white;
                        font-weight: bold;
                        border-radius: 6px;
                        padding: 10px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #1e6b33;
                    }
                """
                
                self.btn_entrar_usr.setStyleSheet(estilo_btn)
                self.btn_entrar_adm.setStyleSheet(estilo_btn.replace("#278c43", "#1e5c2b").replace("#1e6b33", "#143e1d"))
                
                # Adiciona ambos os botões ao layout vertical
                layout.addWidget(self.btn_entrar_usr)
                layout.addWidget(self.btn_entrar_adm)
                
                # Conecta os novos botões aos métodos correspondentes
                self.btn_entrar_usr.clicked.connect(self.acao_login)
                self.btn_entrar_adm.clicked.connect(self.acao_login_admin)

        # --- CADASTRO NOVO USUÁRIO ---
        if self.view.login_ui and hasattr(self.view.login_ui, 'label_registro'):
            label = self.view.login_ui.label_registro

            texto_html = (
                '<html><body><p align="center">'
                'Não tem conta ainda? '
                '<a href="#cadastrar" style="color: #278c43; font-weight: bold; text-decoration: none;">'
                'Cadastre-se aqui</a>'
                '</p></body></html>'
            )
            label.setText(texto_html)

            label.setOpenExternalLinks(False)
            label.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
            label.setCursor(QCursor(Qt.PointingHandCursor))
            label.linkActivated.connect(self.acao_abrir_cadastro_usuario)
            
        # --- TELA PRINCIPAL (Ações e Barra de Busca) ---
        if self.view.main_ui:
            self.view.main_ui.btn_perdi.clicked.connect(self.acao_perdi_item) 
            self.view.main_ui.btn_encontrei.clicked.connect(self.acao_encontrei_item)
                        
            # Cria o botão dinamicamente e tenta achar um layout pai na tela principal
            # (ou você pode adicioná-lo em um container específico da sua main_ui)
            self.btn_painel_admin = QPushButton("Painel Administrativo", self.view.main_ui)
            
            # Estilo verde consistente com o restante do projeto
            self.btn_painel_admin.setStyleSheet("""
                QPushButton {
                    background-color: #1e5c2b;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #143e1d;
                }
            """)
            
            # Conecta o clique do botão criado agora mesmo ao seu método de abrir o painel
            self.btn_painel_admin.clicked.connect(self.abrir_painel_admin)
            
            # Posiciona o botão de forma visível na tela principal (ajuste x e y conforme sua preferência)
            self.btn_painel_admin.setGeometry(350, 210, 250, 40) 
            # ---------------------------------------------------------
            
            if hasattr(self.view.main_ui, 'lineEdit_busca'):
                self.view.main_ui.lineEdit_busca.textChanged.connect(self.filtrar_itens)

    def acao_login(self):
        """Autenticação de usuário comum."""
        ui = self.view.login_ui
        if not ui:
            return

        email = ui.lineEdit_email.text().strip()
        senha = ui.lineEdit_senha.text()

        if not email or not senha:
            QMessageBox.warning(ui, "Aviso", "Por favor, preencha o e-mail e a senha.")
            return

        usuario_valido = self.usuario_model.verificar_login(email, senha)

        if usuario_valido:
            print("[CONTROLLER]: Login efetuado com sucesso! Abrindo tela principal...")
            ui.close()
            self.view.main_ui.show()
        else: 
            print("[CONTROLLER]: Acesso negado. Credenciais incorretas.")
            QMessageBox.critical(ui, "Erro de Acesso", "E-mail ou senha incorretos.")

    def acao_login_admin(self):
        """Valida as credenciais de administrador na tela de login principal antes de abrir o painel."""
        ui = self.view.login_ui
        if not ui:
            return

        # Captura o e-mail e a senha preenchidos nos campos da tela de login
        email = ui.lineEdit_email.text().strip()
        senha = ui.lineEdit_senha.text()

        if not email or not senha:
            QMessageBox.warning(ui, "Aviso", "Por favor, preencha o e-mail e a senha para o acesso administrativo.")
            return

        # Consulta o banco para verificar se é um funcionário válido
        # (Certifique-se de chamar o método através da instância do seu banco ou modelo de usuário)
        admin_valido = self.usuario_model.verificar_login_admin(email, senha) 
        # Nota: Se estiver a chamar direto pelo objeto database, ajuste para self.db.verificar_login_admin(email, senha)

        if admin_valido:
            print("[CONTROLLER]: Acesso administrativo autorizado com sucesso!")
            ui.close()
            self.view.main_ui.show()

            if self.admin_view is not None:
                self.admin_view.close()
                
                # 3. Atualiza os itens da tela principal para o admin ver tudo certinho
                self.atualizar_grid_itens()
        
        else:
            print("[CONTROLLER]: Acesso administrativo negado. Credenciais inválidas ou sem privilégios.")
            QMessageBox.critical(
                ui, 
                "Acesso Negado", 
                "E-mail ou senha incorretos, ou você não possui permissões de administrador (funcionário)."
            )

    def acao_perdi_item(self):
        """Instancia a tela de itens perdidos e injeta os filtros de eventos via POO."""
        self.dialog_perdido = self.view.carregar_ui('perdido.ui')
        if self.dialog_perdido:
            self.foto_selecionada_path = None
            self.dialog_perdido.btn_cancelar.clicked.connect(self.dialog_perdido.close) 
            self.dialog_perdido.btn_cadastrar.clicked.connect(self.salvar_item_perdido) 
            
            if hasattr(self.dialog_perdido, 'label_foto'):
                label = self.dialog_perdido.label_foto
                label.setAttribute(Qt.WA_TransparentForMouseEvents, False)
                label.setCursor(QCursor(Qt.PointingHandCursor))
                label.installEventFilter(self)
                label.setProperty("janela_mae", self.dialog_perdido)

            self.dialog_perdido.exec()

    def acao_encontrei_item(self):
        """Instancia a tela de itens achados e injeta os filtros de eventos via POO."""
        self.dialog_encontrado = self.view.carregar_ui('cadastro.ui')
        if self.dialog_encontrado:
            self.foto_selecionada_path = None
            self.dialog_encontrado.btn_cancelar.clicked.connect(self.dialog_encontrado.close) 
            self.dialog_encontrado.btn_cadastrar.clicked.connect(self.salvar_item_encontrado) 
            
            if hasattr(self.dialog_encontrado, 'label_foto'):
                label = self.dialog_encontrado.label_foto
                label.setAttribute(Qt.WA_TransparentForMouseEvents, False)
                label.setCursor(QCursor(Qt.PointingHandCursor))
                label.installEventFilter(self)
                label.setProperty("janela_mae", self.dialog_encontrado)

            self.dialog_encontrado.exec()

    def _processar_copia_foto(self):
        caminho_foto_banco = None
        if self.foto_selecionada_path and os.path.exists(self.foto_selecionada_path):
            try:
                if not os.path.exists("fotos_itens"):
                    os.makedirs("fotos_itens")
                
                nome_arquivo = f"{int(time.time())}_{os.path.basename(self.foto_selecionada_path)}"
                destino = os.path.join("fotos_itens", nome_arquivo)
                
                shutil.copy(self.foto_selecionada_path, destino)
                caminho_foto_banco = destino
            except Exception as e:
                print(f"Erro ao processar imagem de forma encapsulada: {e}")
        return caminho_foto_banco

    def salvar_item_perdido(self):
        """Captura os dados da interface, instancia o domínio e delega a inserção."""
        ui = self.dialog_perdido
        if not ui:
            return

        titulo = ui.txt_nome_item.text().strip() if hasattr(ui, 'txt_nome_item') else ""
        detalhes = ui.txt_descricao.toPlainText().strip() if hasattr(ui, 'txt_descricao') else ""
        local_item = ui.txt_local.text().strip() if hasattr(ui, 'txt_local') else "Não especificado"
        hora_perda = ui.timeEdit.time().toString("HH:mm") if hasattr(ui, 'timeEdit') else ""

        if not titulo:
            QMessageBox.warning(ui, "Aviso", "Por favor, preencha o campo Nome do Item.")
            return

        descricao_completa = f"{detalhes}\n(Hora provável da perda: {hora_perda})" if hora_perda else detalhes
        caminho_foto_banco = self._processar_copia_foto()

        try:
            from models.item import ItemPerdido
            item_perdido = ItemPerdido(
                titulo=titulo,
                descricao=descricao_completa,
                local=local_item if local_item else "Campus",
                foto_path=caminho_foto_banco,
                status='Ativo',
                id_usuario=None
            )
            item_perdido.validar()
        except Exception as erro_validacao:
            QMessageBox.warning(ui, "Erro de Validação", str(erro_validacao))
            return

        if self.item_model.cadastrar_item(item_perdido.to_dict()):
            QMessageBox.information(ui, "Sucesso", "Item cadastrado como perdido com sucesso!")
            ui.close()
            self.atualizar_grid_itens()
        else:
            QMessageBox.critical(ui, "Erro", "Erro ao salvar no banco de dados.")

    def salvar_item_encontrado(self):
        """Agrupa os dados, instancia a classe ItemAchado e envia ao modelo."""
        ui = self.dialog_encontrado
        if not ui:
            return

        quem_encontrou = ui.txt_nome_encontrou.text().strip() if hasattr(ui, 'txt_nome_encontrou') else "Anônimo"
        categoria = ui.txt_categoria.text().strip() if hasattr(ui, 'txt_categoria') else ""
        local_item = ui.txt_local.text().strip() if hasattr(ui, 'txt_local') else ""
        data_achado = ui.dateEdit.date().toString("dd/MM/yyyy") if hasattr(ui, 'dateEdit') else ""
        hora_achado = ui.timeEdit.time().toString("HH:mm") if hasattr(ui, 'timeEdit') else ""

        if not categoria:
            QMessageBox.warning(ui, "Aviso", "Por favor, preencha o Tipo de Item / Categoria.")
            return

        if not local_item:
            QMessageBox.warning(ui, "Aviso", "Por favor, preencha o Local Onde Encontrou.")
            return

        descricao_completa = f"Encontrado por: {quem_encontrou}. Data: {data_achado} às {hora_achado}."
        caminho_foto_banco = self._processar_copia_foto()

        try:
            from models.item import ItemAchado
            item_achado = ItemAchado(
                titulo=categoria,
                descricao=descricao_completa,
                local=local_item,
                foto_path=caminho_foto_banco,
                status='Ativo',
                id_usuario=None
            )
            item_achado.validar()
        except Exception as erro_validacao:
            QMessageBox.warning(ui, "Erro de Validação", str(erro_validacao))
            return

        if self.item_model.cadastrar_item(item_achado.to_dict()):
            QMessageBox.information(ui, "Sucesso", "Item cadastrado com sucesso!")
            ui.close()
            self.atualizar_grid_itens()
        else:
            QMessageBox.critical(ui, "Erro", "Erro ao salvar o item encontrado no banco de dados.")

    def clique_na_foto(self, event):
        """Mapeia o clique físico no componente de imagem via propriedades polimórficas."""
        label_clicado = self.sender() if self.sender() else None
        
        if not label_clicado and self.dialog_perdido:
            if hasattr(self.dialog_perdido, 'label_foto') and self.dialog_perdido.label_foto.underMouse():
                label_clicado = self.dialog_perdido.label_foto
        if not label_clicado and self.dialog_encontrado:
            if hasattr(self.dialog_encontrado, 'label_foto') and self.dialog_encontrado.label_foto.underMouse():
                label_clicado = self.dialog_encontrado.label_foto

        if label_clicado:
            janela_pai = label_clicado.property("janela_mae")
            self.abrir_seletor_arquivos(janela_pai, label_clicado)
 
    def abrir_seletor_arquivos(self, janela_atual, label_alvo):
        """Encapsula a chamada nativa do gerenciador de arquivos do sistema operacional."""
        arquivo, _ = QFileDialog.getOpenFileName(
            janela_atual,
            "Selecionar Foto do Item",
            "",
            "Imagens (*.png *.jpg *.jpeg)"
        )
        if arquivo:
            self.definir_foto_no_label(arquivo, label_alvo)

    def selecionar_foto(self, janela_atual, label_alvo):
        """Interface redundante mantida para compatibilidade interna do fluxo."""
        self.abrir_seletor_arquivos(janela_atual, label_alvo)

    def evento_arrastar_entrar(self, event):
        """Manipulação polimórfica de eventos Drag and Drop."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def evento_soltar_foto(self, event, label_alvo):
        """Manipulação polimórfica de recepção de arquivos externos via Drop."""
        urls = event.mimeData().urls()
        if urls:
            arquivo = urls[0].toLocalFile()
            if arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.definir_foto_no_label(arquivo, label_alvo)
                event.acceptProposedAction()

    def definir_foto_no_label(self, arquivo_path, label_alvo):
        """Aplica o tratamento e redimensionamento da imagem de forma encapsulada."""
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
        """Intercepta nativamente eventos do Qt."""
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if watched.objectName() == "label_foto":
                janela_pai = watched.property("janela_mae")
                self.abrir_seletor_arquivos(janela_pai, watched)
                return True  
        return super().eventFilter(watched, event)

    def atualizar_grid_itens(self, itens=None):
        """Carrega e renderiza os cards de itens dinamicamente na interface."""
        try:
            if itens is None:
                itens = self.item_model.obter_todos_itens()

            from PySide6.QtWidgets import QListWidget
            
            lista_widget = self.view.findChild(QListWidget)
            if not lista_widget and hasattr(self.view, 'main_ui'):
                lista_widget = self.view.main_ui.findChild(QListWidget)

            if lista_widget:
                lista_widget.clear() 
                
                for item in itens:
                    item_container = QListWidgetItem(lista_widget)
                    card = ItemCardWidget(item)
                    item_container.setSizeHint(card.sizeHint())
                    lista_widget.setItemWidget(item_container, card)
                print(f"Grid updated successfully! {len(itens)} cards loaded.")
            else:
                print("Aviso: Nenhum componente QListWidget foi localizado na interface gráfica.")
        except Exception as e:
            print(f"Erro crítico ao renderizar os cards na tela: {e}")

    def filtrar_itens(self):
        """Mapeia em tempo real a busca na interface e aplica filtros no banco."""
        if not self.view.main_ui or not hasattr(self.view.main_ui, 'lineEdit_busca'):
            return

        texto_busca = self.view.main_ui.lineEdit_busca.text().strip()
        
        if not texto_busca:
            itens_filtrados = self.item_model.obter_todos_itens()
        else:
            itens_filtrados = self.item_model.buscar_itens_por_filtro(texto_busca)
        
        self.atualizar_grid_itens(itens_filtrados)
        
    def acao_abrir_cadastro_usuario(self):
        """Instancia o formulário e configura dinamicamente as alternâncias visuais."""
        self.dialog_cadastro = self.view.carregar_ui('cadastroUsuario.ui')
        if self.dialog_cadastro:
            self.dialog_cadastro.rad_aluno.toggled.connect(self.alternar_campos_formulario)
            self.dialog_cadastro.rad_funcionario.toggled.connect(self.alternar_campos_formulario)
            
            self.dialog_cadastro.rad_aluno.setChecked(True)
            self.alternar_campos_formulario()
            self.dialog_cadastro.btn_cadastrar.clicked.connect(self.salvar_novo_usuario)
            self.dialog_cadastro.exec()

    def alternar_campos_formulario(self):
        """Gerencia o estado dos componentes visuais com base no tipo selecionado."""
        if not self.dialog_cadastro:
            return
            
        is_aluno = self.dialog_cadastro.rad_aluno.isChecked()
        
        self.dialog_cadastro.txt_curso.setEnabled(is_aluno)
        self.dialog_cadastro.txt_semestre.setEnabled(is_aluno)
        self.dialog_cadastro.txt_ra.setEnabled(is_aluno)
        self.dialog_cadastro.txt_cargo.setEnabled(not is_aluno)
        
        if is_aluno:
            self.dialog_cadastro.txt_cargo.clear()
        else:
            self.dialog_cadastro.txt_curso.clear()
            self.dialog_cadastro.txt_semestre.clear()
            self.dialog_cadastro.txt_ra.clear()

    def salvar_novo_usuario(self):
        """Captura os dados da interface, instancia o domínio (Aluno/Funcionário) e valida."""
        ui = self.dialog_cadastro
        if not ui:
            return
        
        nome = ui.txt_nome.text().strip()
        email = ui.txt_email.text().strip()
        senha = ui.txt_senha.text()
        nascimento = ui.date_nascimento.date().toString("yyyy-MM-dd")
        tipo = "aluno" if ui.rad_aluno.isChecked() else "funcionario"
        periodo = "Integral" if ui.rad_integral.isChecked() else "Noturno"

        if not nome or not email or not senha:
            QMessageBox.warning(ui, "Aviso", "Preencha os campos obrigatórios (Nome, E-mail e Senha).")
            return

        try:
            from models.usuario import Aluno, Funcionario
            
            if tipo == "aluno":
                semestre_texto = ui.txt_semestre.text().strip()
                semestre_valor = int(semestre_texto) if semestre_texto.isdigit() else 1
                
                usuario_objeto = Aluno(
                    nome=nome,
                    email=email,
                    senha=senha,
                    data_nascimento=nascimento,
                    ra=ui.txt_ra.text().strip(),
                    curso=ui.txt_curso.text().strip(),
                    periodo=periodo,
                    semestre=semestre_valor
                )
            else:
                usuario_objeto = Funcionario(
                    nome=nome,
                    email=email,
                    senha=senha,
                    data_nascimento=nascimento,
                    cargo=ui.txt_cargo.text().strip()
                )
                
            # Executa o método obrigatório de validação do diagrama
            usuario_objeto.validar()
            
        except Exception as erro_validacao:
            QMessageBox.warning(ui, "Erro de Validação", str(erro_validacao))
            return

        # Envia o objeto estruturado para o modelo de persistência
        if self.usuario_model.cadastrar_usuario(usuario_objeto.to_dict()):
            QMessageBox.information(ui, "Sucesso", "Usuário cadastrado com sucesso!")
            ui.close()
        else:
            QMessageBox.critical(ui, "Erro", "Não foi possível realizar o cadastro no banco de dados.")

    def abrir_painel_admin(self):
        """Abre a janela de administração e conecta os botões"""
        try:
            if self.admin_view is None:
                # Verifique se o AdminView precisa de parâmetros (como self.db ou self.item_model)
                self.admin_view = AdminView(self.item_model) 
                
                # Conecta o botão de cadastrar item se já o adicionou
                if hasattr(self.admin_view, 'btn_cadastrar_item'):
                    self.admin_view.btn_cadastrar_item.clicked.connect(self.abrir_formulario_cadastro_item)
                
            self.admin_view.show()
            self.admin_view.raise_()
            self.admin_view.activateWindow()
            
        except Exception as e:
            print(f"[ERRO] Falha ao abrir AdminView: {e}")
            # ADICIONE ISTO para ver o erro na tela e não apenas no terminal:
            QMessageBox.critical(None, "Erro Crítico", f"Não foi possível abrir o painel admin:\n{e}")

    def abrir_formulario_cadastro_item(self):
        """Abre a janela de cadastro de item para o administrador."""
        print("[CONTROLLER]: Administrador acionou o cadastro de novo item.")
        
        # Como o admin pode querer registrar um item achado ou perdido, 
        # podemos chamar a função que abre a sua janela de cadastro existente.
        # Procure no seu código como você abre o diálogo de cadastro para os alunos 
        # e chame aqui. Exemplo genérico:
        
        if hasattr(self, 'abrir_dialogo_encontrado'):
            self.abrir_dialogo_encontrado()
        else:
            QMessageBox.information(
                self.admin_view, 
                "Cadastrar Item", 
                "Aqui será aberto o formulário de cadastro de itens para o administrador."
            )