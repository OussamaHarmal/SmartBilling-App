import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from app.auth import init_db
from ui.login import LoginPage
from ui.main_window import MainWindow
from ui.facture_form import FactureWindow
from ui.client_from import ClientForm

def main():
    app = QApplication(sys.argv)

    
    init_db()

    
    def on_login(role):
        if role == 'admin':
            login.win = MainWindow()
        elif role == 'comptable':
            login.win = FactureWindow()
        elif role == 'commercial':
            login.win = ClientForm()
        else:
            QMessageBox.critical(None, "Erreur", "Rôle inconnu.")
            return

        login.win.show()
        login.close()

    login = LoginPage(on_login)
    login.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
