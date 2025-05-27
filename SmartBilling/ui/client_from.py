from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QHeaderView
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import re
import pandas as pd
from app.client_manager import add_client, get_all_clients, delete_client, update_client_by_id


class ClientForm(QWidget):
    def __init__(self):
        super().__init__()
        self.df = pd.DataFrame()
        self.setWindowTitle("Gestion des clients")
        self.setWindowIcon(QIcon(":/icons/client.png"))
        self.resize(1200, 700)

        self.selected_client_id = None
        self.init_ui()
        self.load_clients()
        self.apply_styles()

    def init_ui(self):
        self.full_name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        self.city_input = QComboBox()
        self.city_input.addItems(["Agadir", "Casablanca", "Rabat", "Fès", "Marrakech", "Tanger", "Oujda", "Tétouan",
            "Nador", "Khouribga", "El Jadida", "Safi", "Meknès", "Mohammedia", "Beni Mellal",
            "Settat", "Kénitra", "Errachidia", "Laâyoune", "Dakhla", "Taza", "Berkane",
            "Ouarzazate", "Al Hoceima", "Guelmim", "Taroudant", "Oued Zem", "Azrou",
            "Ifrane", "Taourirt", "Midelt"])
        self.status_input = QComboBox()
        self.status_input.addItems(["Actif", "Inactif", "Prospect", "VIP"])
        self.activity_input = QComboBox()
        self.activity_input.addItems(["Informatique", "Construction", "Commerce", "Éducation", "Santé"])

        form_layout = QVBoxLayout()
        for label, widget in [
            ("Nom complet", self.full_name_input),
            ("Email", self.email_input),
            ("Téléphone", self.phone_input),
            ("Adresse", self.address_input),
            ("Ville", self.city_input),
            ("Statut", self.status_input),
            ("Activité", self.activity_input)
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(widget)
            form_layout.addLayout(row)

        self.add_btn = QPushButton("➕ Ajouter")
        self.update_btn = QPushButton("✏️ Modifier")
        self.delete_btn = QPushButton("🗑️ Supprimer")

        self.add_btn.clicked.connect(self.add_client)
        self.add_btn.setObjectName("add")
        self.update_btn.clicked.connect(self.update_client)
        self.update_btn.setObjectName("update")
        self.delete_btn.clicked.connect(self.delete_client)
        self.delete_btn.setObjectName("delete")

        btn_layout = QHBoxLayout()
        for btn in [self.add_btn, self.update_btn, self.delete_btn]:
            btn_layout.addWidget(btn)
        form_layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Email", "Téléphone", "Adresse", "Ville", "Statut"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(self.load_client_from_table)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QLabel { font-weight: bold; color: black; }
            QLineEdit, QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #e0e0e0;
            }
            QComboBox QAbstractItemView {
                background-color: #3aea6d;
                color: black;
                selection-background-color: #f0f0f0;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #ccc;
                padding: 6px 12px;
                border-radius: 6px;
                color: black;
            }
            QPushButton#add {
                background-color: #22c55e;
                color: white;
            }
            QPushButton#add:hover {
                background-color: #16a34a;
            }
            QPushButton#delete {
                background-color: #ef4444;
                color: white;
            }
            QPushButton#delete:hover {
                background-color: #dc2626;
            }
            QPushButton#update {
                background-color: #3b82f6;
                color: white;
            }
            QPushButton#update:hover {
                background-color: #2563eb;
            }
            QTableWidget {
                background-color: white;
                color: black;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #3aea6d;
                color: white;
                border: 1px solid #ccc;
                padding: 4px;
            }
        """)

    def load_clients(self):
        clients = get_all_clients()
        self.table.setRowCount(0)
        for row_idx, client in enumerate(clients):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate([
                client.id, client.full_name, client.email,
                client.phone, client.adresse, client.ville, client.statut
            ]):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def load_client_from_table(self, row, col):
        self.selected_client_id = int(self.table.item(row, 0).text())
        self.full_name_input.setText(self.table.item(row, 1).text())
        self.email_input.setText(self.table.item(row, 2).text())
        self.phone_input.setText(self.table.item(row, 3).text())
        self.address_input.setText(self.table.item(row, 4).text())
        self.city_input.setCurrentText(self.table.item(row, 5).text())
        self.status_input.setCurrentText(self.table.item(row, 6).text())

    def add_client(self):
        name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()
        city = self.city_input.currentText()
        status = self.status_input.currentText()
        activity = self.activity_input.currentText()

        if not name or not email or not phone:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir les champs obligatoires.")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Erreur", "Adresse e-mail invalide.")
            return

        add_client(name, email, phone, address, city, status, activity)
        self.load_clients()
        QMessageBox.information(self, "Succès", "Client ajouté avec succès.")

    def update_client(self):
        if not self.selected_client_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un client dans le tableau.")
            return

        update_client_by_id(
            self.selected_client_id,
            self.full_name_input.text(),
            self.email_input.text(),
            self.phone_input.text(),
            self.address_input.text(),
            self.city_input.currentText(),
            self.status_input.currentText(),
            self.activity_input.currentText()
        )
        self.load_clients()
        QMessageBox.information(self, "Succès", "Informations mises à jour avec succès.")

    def delete_client(self):
        if not self.selected_client_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un client dans le tableau.")
            return

        delete_client(self.selected_client_id)
        self.load_clients()
        QMessageBox.information(self, "Supprimé", "Client supprimé avec succès.")
