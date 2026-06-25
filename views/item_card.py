from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os

class ItemCardWidget(QWidget):
    def __init__(self, item_model, parent=None):
        super().__init__(parent)
        self.item = item_model # Instância com (.titulo, .descricao, .foto_path, .local, etc.)
        self.init_ui()

    def init_ui(self):
        # Layout principal do Card
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Estilo do Card (Bordas arredondadas, fundo branco, sombra leve)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
        """)

        # 1. Imagem do Item (ou Placeholder)
        self.label_foto = QLabel()
        self.label_foto.setFixedSize(80, 80)
        self.label_foto.setStyleSheet("background-color: #f4f6f9; border-radius: 4px;")
        self.label_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Carrega a foto do item se houver caminho válido, senão usa padrão
        if hasattr(self.item, 'foto_path') and self.item.foto_path and os.path.exists(self.item.foto_path):
            pixmap = QPixmap(self.item.foto_path)
            if not pixmap.isNull():
                self.label_foto.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.label_foto.setText("Sem Foto")
        else:
            self.label_foto.setText("Sem Foto")
            
        layout.addWidget(self.label_foto)

        # 2. Informações Textuais (Vertical)
        info_layout = QVBoxLayout()
        
        # ALTERAÇÃO AQUI: Mudamos de self.item.nome para self.item.titulo
        self.label_nome = QLabel(f"<b>{self.item.titulo}</b>")
        self.label_nome.setStyleSheet("font-size: 14px; color: #333;")
        
        self.label_desc = QLabel(self.item.descricao)
        self.label_desc.setStyleSheet("color: #666; font-size: 11px;")
        self.label_desc.setWordWrap(True)
        
        # Adicional: Mostra o local onde sumiu/foi achado
        local_texto = getattr(self.item, 'local', 'Não informado')
        self.label_local = QLabel(f"📍 Local: {local_texto}")
        self.label_local.setStyleSheet("color: #777; font-size: 11px;")
        
        # Configura o Status (PERDIDO ou ENCONTRADO)
        status_item = getattr(self.item, 'tipo_item', self.item.status)
        self.label_status = QLabel(f"Status: {status_item.upper()}")
        
        # Cor dinâmica para perdido/encontrado
        if status_item.lower() == 'perdido':
            self.label_status.setStyleSheet("color: #d9534f; font-weight: bold; font-size: 11px;")
        else:
            self.label_status.setStyleSheet("color: #5cb85c; font-weight: bold; font-size: 11px;")

        info_layout.addWidget(self.label_nome)
        info_layout.addWidget(self.label_desc)
        info_layout.addWidget(self.label_local)
        info_layout.addWidget(self.label_status)
        info_layout.addStretch()

        layout.addLayout(info_layout)
        layout.setStretchFactor(info_layout, 1)