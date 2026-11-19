import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt

class AdminView(QMainWindow):
    def __init__(self, item_model=None):
        super().__init__()
        self.item_model = item_model
        
        self.setWindowTitle("Painel Administrativo - Validação de Resgate (IFMG)")
        self.resize(900, 550)
        
        # Widget central principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal vertical
        layout_principal = QVBoxLayout(central_widget)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)
        
        # Título da seção
        titulo = QLabel("Painel de Validação de Itens Resgatados")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #278c43;")
        layout_principal.addWidget(titulo)
        
        # Tabela de itens
        self.tabela_itens = QTableWidget()
        self.tabela_itens.setColumnCount(5)
        self.tabela_itens.setHorizontalHeaderLabels(["ID", "Título / Categoria", "Local", "Status", "Descrição"])
        
        # Configura o redimensionamento das colunas para preencher a tela
        header = self.tabela_itens.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        layout_principal.addWidget(self.tabela_itens)
        
        # Layout horizontal para os botões de ação
        layout_botoes = QHBoxLayout()
        
        self.btn_atualizar = QPushButton("Atualizar Lista")
        self.btn_cadastrar_item = QPushButton("Cadastrar Novo Item") # <--- Adiciona esta linha
        self.btn_validar = QPushButton("Validar / Confirmar Resgate")
        self.btn_excluir_item = QPushButton("Excluir Item Selecionado")
        
        # Estilização padrão dos botões
        estilo_btn = """
            QPushButton {
                background-color: #278c43;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1e6b33;
            }
        """

        #Estilos individuais para cada botão
        self.btn_atualizar.setStyleSheet(estilo_btn.replace("#278c43", "#555555").replace("#1e6b33", "#333333"))
        
        estilo_btn_cadastrar = estilo_btn.replace("#278c43", "#2b6cb0").replace("#1e6b33", "#2c5282")
        self.btn_cadastrar_item.setStyleSheet(estilo_btn_cadastrar)
        
        self.btn_validar.setStyleSheet(estilo_btn)
        self.btn_excluir_item.setStyleSheet(estilo_btn.replace("#278c43", "#c53030").replace("#1e6b33", "#9b2c2c"))

        #Botões adicionados ao layout horizontal
        layout_botoes.addWidget(self.btn_atualizar)
        layout_botoes.addWidget(self.btn_cadastrar_item) 
        layout_botoes.addWidget(self.btn_excluir_item)
        layout_botoes.addStretch()
        layout_botoes.addWidget(self.btn_validar)

        layout_principal.addLayout(layout_botoes)
        
        
        # Conexões de eventos dos botões da interface
        self.btn_atualizar.clicked.connect(self.carregar_dados_tabela)
        self.btn_validar.clicked.connect(self.acao_validar_item)
        self.btn_excluir_item.clicked.connect(self.acao_excluir_item) 

        if self.item_model:
            self.carregar_dados_tabela()

            
    def set_item_model(self, item_model):
        """Injeta o modelo de itens para que a view possa buscar os dados"""
        self.item_model = item_model
        self.carregar_dados_tabela()

    def carregar_dados_tabela(self):
        """Busca os itens no banco de dados e preenche a tabela visualmente"""
        print(f"[DEBUG ADMIN] item_model atual: {self.item_model}")
        
        if not self.item_model:
            print("[DEBUG ADMIN] ERRO: item_model está Vazio ou None!")
            return
            
        try:
            itens = self.item_model.obter_todos_itens()
            print(f"[DEBUG ADMIN] Itens retornados do banco: {len(itens)}")
            self.tabela_itens.setRowCount(0)
            
            for row_idx, item in enumerate(itens):
                self.tabela_itens.insertRow(row_idx)
                
                # Inicializa a variável com vazio para evitar lixo de memória
                id_item = ""
                
                # Tratamento seguro se o item é um dicionário ou um objeto POO
                if isinstance(item, dict):
                    id_item = str(item.get('id_item') or item.get('id') or '')
                else:
                    val = getattr(item, 'id_item', None) or getattr(item, 'id', None)
                    if val is not None:
                        id_item = str(val)
                
                # Fallback definitivo: se ainda estiver vazio, usa a linha atual + 1
                if not id_item or id_item == "None":
                    id_item = str(row_idx + 1)
                
                titulo = str(item.get('titulo', '')) if isinstance(item, dict) else str(getattr(item, 'titulo', ''))
                local = str(item.get('local', '')) if isinstance(item, dict) else str(getattr(item, 'local', ''))
                status = str(item.get('status', '')) if isinstance(item, dict) else str(getattr(item, 'status', ''))
                descricao = str(item.get('descricao', '')) if isinstance(item, dict) else str(getattr(item, 'descricao', ''))
                
                self.tabela_itens.setItem(row_idx, 0, QTableWidgetItem(id_item))
                self.tabela_itens.setItem(row_idx, 1, QTableWidgetItem(titulo))
                self.tabela_itens.setItem(row_idx, 2, QTableWidgetItem(local))
                self.tabela_itens.setItem(row_idx, 3, QTableWidgetItem(status))
                self.tabela_itens.setItem(row_idx, 4, QTableWidgetItem(descricao))
                
        except Exception as e:
            print(f"[ERRO] Falha ao carregar dados na tabela admin: {e}")

    def acao_excluir_item(self):
        """Exclui o item selecionado na tabela"""
        linha_selecionada = self.tabela_itens.currentRow()
        if linha_selecionada < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um item na tabela para excluir.")
            return
            
        item_id_widget = self.tabela_itens.item(linha_selecionada, 0)
        if item_id_widget:
            id_item = item_id_widget.text()
            
            resposta = QMessageBox.question(
                self, "Confirmação", 
                f"Tem certeza que deseja excluir o item ID {id_item}?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if resposta == QMessageBox.Yes:
                try:
                    conn = self.item_model.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM itens WHERE id_item = ?", (id_item,))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Sucesso", "Item excluído com sucesso!")
                    self.carregar_dados_tabela()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Não foi possível excluir o item: {e}")

    def acao_validar_item(self):
        """Captura a linha selecionada e processa a validação do item"""
        linha_selecionada = self.tabela_itens.currentRow()
        if linha_selecionada < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um item na tabela para validar.")
            return
            
        item_id_widget = self.tabela_itens.item(linha_selecionada, 0)
        if item_id_widget:
            id_item = item_id_widget.text()
            # Aqui você pode chamar a lógica para atualizar o status no banco de dados
            QMessageBox.information(self, "Sucesso", f"Item ID {id_item} validado com sucesso!")
            # self.carregar_dados_tabela() # Atualiza a tabela após a ação