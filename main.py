import sys
from PySide6.QtWidgets import QApplication
from models.database import Database
from models.item_model import ItemModel
from views.main_view import MainView
from controllers.main_controller import MainController

def main():
    app = QApplication(sys.argv)

    db = Database()
    item_model = ItemModel(db)
    view = MainView()
    
    # O controller passa a gerenciar as exibições
    controller = MainController(view, item_model)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()