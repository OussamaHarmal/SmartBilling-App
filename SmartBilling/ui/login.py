# ui/login.py
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from app.auth import check_login

class LoginPage(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.setWindowTitle("🔐 Connexion")
        self.resize(400, 250)
        self.on_login_success = on_login_success
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f8;
                font-family: 'Segoe UI';
                font-size: 14px;
            }

            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #fff;
                color:black;
            }

            QLineEdit:focus {
                border: 1px solid #0078d7;
                background-color: #fefefe;
            }

            QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #005a9e;
            }

            QLabel {
                margin-top: 8px;
                font-weight: bold;
                color:black;
            }
        """)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Se connecter")
        self.login_button.clicked.connect(self.handle_login)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Identifiant:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Mot de passe:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # التأكد من أن البيانات ليست فارغة
        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer votre identifiant et mot de passe.")
            return
        
        # التحقق من الدخول
        role = check_login(username, password)
        
        if role:
            self.on_login_success(role)
            self.close()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects.")
