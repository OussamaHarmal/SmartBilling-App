from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QHeaderView, QTextEdit, QDateEdit,
    QDialog, QFormLayout,QSizePolicy,
)
import platform
import os
from app.models import Facture
from sqlalchemy.orm import joinedload
from PyQt6.QtCore import Qt, QDate,QModelIndex
from PyQt6.QtGui import QAction
from datetime import datetime
from sqlalchemy.orm import Session
from app.facture_manger import (
    add_facture, get_all_factures, delete_facture, get_facture_by_id,update_facture_statut
)
from app.client_manager import get_all_clients
from app.db import SessionLocal
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class ModifierFactureDialog(QDialog):
    def __init__(self, parent=None, facture=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion de Facture")
        self.setMinimumSize(600, 500)
        self.facture = facture
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout()

        
        form_layout = QFormLayout()

        self.client_combo = QComboBox()
        self.client_combo.setObjectName("client_combo")
        clients = get_all_clients()
        for client in clients:
            self.client_combo.addItem(client.full_name, client.id)

        self.date_edit = QDateEdit()
        self.date_edit.setObjectName("date_edit")
        self.date_edit.setDisplayFormat("yyyy-MM-dd")

        self.statut_combo = QComboBox()
        self.statut_combo.setObjectName("statut_combo")
        self.statut_combo.addItems(["Impayé", "Payé"])

        self.type_combo = QComboBox()
        self.type_combo.setObjectName("type_combo")
        self.type_combo.addItems(["espece", "cheque", "virement"])

        form_layout.addRow("Client:", self.client_combo)
        form_layout.addRow("Date:", self.date_edit)
        form_layout.addRow("Statut:", self.statut_combo)
        form_layout.addRow("Type de paiement:", self.type_combo)

        layout.addLayout(form_layout)

        # جدول العناصر
        self.items_table = QTableWidget()
        self.items_table.setObjectName("items_table")
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Description", "Quantité", "Prix_Unitaire", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.itemChanged.connect(self.update_row_total)
        self.description_options = ["Reliure spirale", "Scan de documents", "Brochures", "Livraison locale", "Papier photo","Impression couleur A4","Conception graphique","Plastification","Flyers A5","Service express"]
        

        # أزرار إدارة العناصر
        items_buttons = QHBoxLayout()
        add_item_btn = QPushButton("Ajouter Element")
        add_item_btn.setObjectName("add_item_btn")
        add_item_btn.clicked.connect(self.add_item_row)

        remove_item_btn = QPushButton("Supprimer Element")
        remove_item_btn.setObjectName("remove_item_btn")
        remove_item_btn.clicked.connect(self.remove_item_row)

        items_buttons.addWidget(add_item_btn)
        items_buttons.addWidget(remove_item_btn)

        layout.addWidget(QLabel("Element de Facture:"))
        layout.addWidget(self.items_table)
        layout.addLayout(items_buttons)

        # الملاحظات
        self.notes_edit = QTextEdit()
        self.notes_edit.setObjectName("notes_edit")
        layout.addWidget(QLabel("Remarque:"))
        layout.addWidget(self.notes_edit)

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Sauvegarde Modification")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        if self.facture:
            self.load_facture_data()

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2f;
                color: #f0f0f0;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QLabel {
                color: White;
                font-weight: bold;
                background-color: #1e1e2f;
            }

            QComboBox, QDateEdit, QLineEdit, QTextEdit {
                background-color: #2e2e3e;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 4px;
            }

            QTableWidget#items_table {
                background-color: #2c2c3c;
                gridline-color: #444;
                color: #ffffff;
                border-radius: 8px;
            }

            QHeaderView::section {
                background-color: #3c3c4c;
                color: #ffffff;
                padding: 4px;
                border: none;
            }

            QPushButton {
                background-color: #3e3e5e;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
            }

            QPushButton:hover {
                background-color: #505070;
            }

            QPushButton#save_btn {
                background-color: #28a745;
            }

            QPushButton#save_btn:hover {
                background-color: #218838;
            }

            QPushButton#cancel_btn {
                background-color: #dc3545;
            }

            QPushButton#cancel_btn:hover {
                background-color: #c82333;
            }
        """)

    def load_facture_data(self):
        
        self.client_combo.setCurrentIndex(self.client_combo.findData(self.facture.client_id))
        self.date_edit.setDate(QDate.fromString(self.facture.date, "yyyy-MM-dd"))
        self.statut_combo.setCurrentIndex(1 if self.facture.statut else 0)
        self.type_combo.setCurrentText(self.facture.type_paiment)

        for item in self.facture.items:
            self.add_item_row(item)

    def add_item_row(self, item=None):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

        
        desc_combo = QComboBox()
        desc_combo.addItems(self.description_options)
        if item:
            index = desc_combo.findText(item.description)
            if index >= 0:
                desc_combo.setCurrentIndex(index)
        self.items_table.setCellWidget(row, 0, desc_combo)

        
        qty_item = QTableWidgetItem(str(item.quantite) if item else "1")
        self.items_table.setItem(row, 1, qty_item)

        
        price_item = QTableWidgetItem(str(item.unit_price) if item else "0")
        self.items_table.setItem(row, 2, price_item)

        
        total = float(qty_item.text()) * float(price_item.text())
        total_item = QTableWidgetItem(f"{total:.2f}")
        total_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.items_table.setItem(row, 3, total_item)

        self.items_table.setRowHeight(row, 30)  


    def update_row_total(self, item):
        try:
            if item is None or item.column() == 3:
                return

            row = item.row()

            quantity_item = self.items_table.item(row, 1)
            unit_price_item = self.items_table.item(row, 2)

            quantity_text = quantity_item.text().replace(",", ".") if quantity_item and quantity_item.text() else "0"
            unit_price_text = unit_price_item.text().replace(",", ".") if unit_price_item and unit_price_item.text() else "0"

            try:
                quantity = float(quantity_text)
            except ValueError:
                quantity = 0

            try:
                unit_price = float(unit_price_text)
            except ValueError:
                unit_price = 0

            total = quantity * unit_price

            total_item = QTableWidgetItem(f"{total:.2f}")
            total_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

            self.items_table.blockSignals(True)
            self.items_table.setItem(row, 3, total_item)
            self.items_table.blockSignals(False)

        except Exception as e:
            print(f"❌ Erreur lors du calcul du total: {e}")


    
    def remove_item_row(self):
        
        current_row = self.items_table.currentRow()
        if current_row >= 0:
            self.items_table.removeRow(current_row)

    def get_facture_data(self):
        data = {
            "client_id": self.client_combo.currentData(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "statut": self.statut_combo.currentIndex() == 1,
            "type_paiment": self.type_combo.currentText(),
            "items": []
        }

        for row in range(self.items_table.rowCount()):
            try:
                desc_widget = self.items_table.cellWidget(row, 0)
                description = desc_widget.currentText() if desc_widget else ""

                qty_text = self.items_table.item(row, 1).text().replace(",", ".")
                unit_price_text = self.items_table.item(row, 2).text().replace(",", ".")

                quantity = float(qty_text) if qty_text else 0
                unit_price = float(unit_price_text) if unit_price_text else 0

                item = {
                    "description": description,
                    "quantite": quantity,
                    "unit_price": unit_price
                }
                data["items"].append(item)
            except Exception as e:
                print(f"Erreur dans la ligne {row}: {e}")
                # Tu peux afficher un QMessageBox ici si tu veux informer l'utilisateur

        return data


class FactureWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de gestion des factures")
        self.setGeometry(100, 100, 1000, 700)
        self.setup_ui()
        self.apply_inline_styles()
        self.load_factures()
    def apply_inline_styles(self):
        self.setStyleSheet(
             """
            QWidget {
                background-color: #f1f5f9;
                font-family: "Segoe UI";
                font-size: 14px;
            }
            
            QLabel{
                color : Black
            }
            
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                color : Black
            }
            QPushButton {
                padding: 10px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
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
            QPushButton#search {
                background-color: #8b5cf6;
                color: white;
            }
            QPushButton#search:hover {
                background-color: #7c3aed;
            }
            QPushButton#toggle_btn {
                background-color: #facc15;
                color: black;
            }
            QPushButton#toggle_btn:hover {
                background-color: #eab308;
            }

            QPushButton#details_btn {
                background-color: #0ea5e9;
                color: white;
            }
            QPushButton#details_btn:hover {
                background-color: #0284c7;
            }

            QPushButton#pdf_btn {
                background-color: #a855f7;
                color: white;
            }
            QPushButton#pdf_btn:hover {
                background-color: #9333ea;
            }
            
            QPushButton#send {
                background-color: Black;
                color: white;
            }
            QPushButton#pdf_btn:hover {
                background-color: #9333ea;
            }

            QTableWidget {
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                background-color: white;
                font-size: 13px;
                color: Black
            }
            QHeaderView::section {
                background-color: #10b981;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QScrollArea {
                border: none;
            }
            
            QComboBox QAbstractItemView {
                background-color: #10b981;
                color: #333333;
                selection-background-color: #A5D6A7;
                selection-color: black;
                border: 1px solid #aaa;
                border-radius: 10%;
            }
            
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        
        search_filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche par nom..")
        self.search_input.textChanged.connect(self.filter_factures)
        search_filter_layout.addWidget(self.search_input)
        
        self.statut_filter = QComboBox()
        self.statut_filter.addItem("Toutes Factures")
        self.statut_filter.addItem("Payéé")
        self.statut_filter.addItem("Impayée")
        self.statut_filter.currentIndexChanged.connect(self.filter_factures)
        search_filter_layout.addWidget(QLabel("Classifier par statut"))
        search_filter_layout.addWidget(self.statut_filter)
        
        self.type_filter = QComboBox()
        self.type_filter.addItem("toutes les paiement : ")
        self.type_filter.addItem("Espèce")
        self.type_filter.addItem("Chèque")
        self.type_filter.addItem("Virement")
        self.type_filter.currentIndexChanged.connect(self.filter_factures)
        search_filter_layout.addWidget(QLabel("Classifier Par paiement :"))
        search_filter_layout.addWidget(self.type_filter)
        
        layout.addLayout(search_filter_layout)
        
        # جدول الفواتير
        self.factures_table = QTableWidget()
        self.factures_table.setColumnCount(7)
        self.factures_table.setHorizontalHeaderLabels([
            "ID", "Client", "Date", "Statut", "Type Paiement", "Changer de type", "procédures"
        ])
        self.factures_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.factures_table.verticalHeader().setDefaultSectionSize(40)

        self.factures_table.doubleClicked.connect(self.show_facture_details)
        
        layout.addWidget(self.factures_table)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Ajouter Facture")
        self.add_btn.clicked.connect(self.add_facture)
        self.add_btn.setObjectName("add")
        
        self.edit_btn = QPushButton("Modifier Facture")
        self.edit_btn.clicked.connect(self.edit_facture)
        self.edit_btn.setObjectName("update")
        
        self.delete_btn = QPushButton("Supprimer Facture")
        self.delete_btn.clicked.connect(self.delete_facture)
        self.delete_btn.setObjectName("delete")
        
        self.pdf_btn = QPushButton("Generer PDF")
        self.pdf_btn.clicked.connect(self.generate_pdf)
        self.pdf_btn.setObjectName("pdf_btn")
        
        self.email_btn = QPushButton("Envoyer Email")
        self.email_btn.clicked.connect(self.send_email)
        self.email_btn.setObjectName("send")
        
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.pdf_btn)
        buttons_layout.addWidget(self.email_btn)
        
        layout.addLayout(buttons_layout)
        central_widget.setLayout(layout)
    
    

    def load_factures(self):
        session = SessionLocal()
        try:
            self.all_factures = session.query(Facture).options(joinedload(Facture.client)).all()
        finally:
            session.close()
        self.display_factures(self.all_factures)

    
    def filter_factures(self):
        search_text = self.search_input.text().lower()
        statut_filter = self.statut_filter.currentIndex()
        type_filter = self.type_filter.currentText()

        filtered = []
        for facture in self.all_factures:  
            client_name = facture.client.full_name.lower()
            matches_search = search_text in client_name

            matches_statut = True
            if statut_filter == 1:
                matches_statut = facture.statut
            elif statut_filter == 2:
                matches_statut = not facture.statut

            matches_type = (type_filter == "toutes les paiement" or facture.type_paiment == type_filter)

            if matches_search and matches_statut and matches_type:
                filtered.append(facture)

        self.display_factures(filtered)

    
    def display_factures(self, factures):
       
        self.factures_table.setRowCount(0)

        for row, f in enumerate(factures):
            self.factures_table.insertRow(row)

            items = [
                str(f.id),
                f.client.full_name,
                f.date.strftime("%Y-%m-%d"),
                "Payéé" if f.statut else "Impayée",
                f.type_paiment
            ]

            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                if col == 3:  
                    item.setForeground(Qt.GlobalColor.green if f.statut else Qt.GlobalColor.red)
                self.factures_table.setItem(row, col, item)

            
            toggle_btn = QPushButton("Chnager Statut")
            toggle_btn.setObjectName("toggle_btn")
            toggle_btn.setProperty("facture_id", f.id)
            toggle_btn.clicked.connect(self.toggle_statut)
            self.factures_table.setCellWidget(row, 5, toggle_btn)

            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)

            
            details_btn = QPushButton("Details")
            details_btn.setObjectName("details_btn")
            details_btn.setProperty("facture_id", f.id)
            details_btn.clicked.connect(lambda _, fid=f.id: self.show_facture_details_by_id(fid))
            actions_layout.addWidget(details_btn)

           
            pdf_btn = QPushButton("PDF")
            pdf_btn.setObjectName("pdf_btn")
            pdf_btn.setProperty("facture_id", f.id)
            pdf_btn.clicked.connect(lambda _, fid=f.id: self.generate_pdf(fid))
            actions_layout.addWidget(pdf_btn)

            self.factures_table.setCellWidget(row, 6, actions_widget)
            
            
    def show_facture_details_by_id(self, facture_id: int):
        facture = get_facture_by_id(facture_id)
        if facture:
            self._display_facture_dialog(facture)
        else:
            QMessageBox.warning(self, "Erreur", "Facture introuvable.")

    def _display_facture_dialog(self, facture):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Détails de la facture #{facture.id}")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Informations de la facture
        info_layout = QFormLayout()
        info_layout.addRow("Client :", QLabel(facture.client.full_name))
        info_layout.addRow("Date :", QLabel(facture.date.strftime("%d/%m/%Y")))
        info_layout.addRow("Statut :", QLabel("Payée" if facture.statut else "Impayée"))
        info_layout.addRow("Type de paiement :", QLabel(facture.type_paiment))

        layout.addLayout(info_layout)

        # Tableau des éléments
        items_table = QTableWidget()
        items_table.setColumnCount(4)
        items_table.setHorizontalHeaderLabels(["Description", "Quantité", "Prix unitaire", "Total"])
        items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        total = 0
        for item in facture.items:
            row = items_table.rowCount()
            items_table.insertRow(row)

            items_table.setItem(row, 0, QTableWidgetItem(item.description))
            items_table.setItem(row, 1, QTableWidgetItem(str(item.quantite)))
            items_table.setItem(row, 2, QTableWidgetItem(f"{item.unit_price:.2f}"))

            item_total = item.quantite * item.unit_price
            items_table.setItem(row, 3, QTableWidgetItem(f"{item_total:.2f}"))

            total += item_total

        layout.addWidget(QLabel("Articles de la facture :"))
        layout.addWidget(items_table)
        layout.addWidget(QLabel(f"<b>Montant total : {total:.2f} MAD</b>"))

        dialog.setLayout(layout)
        dialog.exec()

    def add_facture(self):
        """Ajouter une nouvelle facture"""
        dialog = ModifierFactureDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            facture_data = dialog.get_facture_data()
            try:
                add_facture(facture_data)
                self.load_factures()
                QMessageBox.information(self, "Ajout réussi", "Facture ajoutée avec succès.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Échec de l'ajout de la facture : {str(e)}")

    def edit_facture(self):
        """Modifier une facture existante"""
        selected_row = self.factures_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une facture à modifier.")
            return

        facture_id = int(self.factures_table.item(selected_row, 0).text())
        facture = get_facture_by_id(facture_id)

        if facture:
            dialog = ModifierFactureDialog(self, facture)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                facture_data = dialog.get_facture_data()
                QMessageBox.information(self, "Modification", "Cette fonctionnalité sera développée prochainement.")
                self.load_factures()

    def delete_facture(self):
        """Supprimer une facture"""
        selected_row = self.factures_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une facture à supprimer.")
            return

        facture_id = int(self.factures_table.item(selected_row, 0).text())

        reply = QMessageBox.question(
            self, "Confirmation de suppression",
            "Êtes-vous sûr de vouloir supprimer cette facture ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if delete_facture(facture_id):
                self.load_factures()
                QMessageBox.information(self, "Supprimé", "Facture supprimée avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", "Échec de la suppression de la facture.")
    
    def toggle_statut(self):
        
        btn = self.sender()
        facture_id = btn.property("facture_id")

        facture = get_facture_by_id(facture_id)
        if facture:
            new_statut = not facture.statut

            success = update_facture_statut(facture_id, new_statut)
            if success:
                QMessageBox.information(self, "Mise à jour", "Statut mis à jour avec succès.")
                self.load_factures()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de mettre à jour le statut.")

    def on_details_button_clicked(self):
        index = self.factures_table.currentIndex()
        if index.isValid():
            self.show_facture_details(index)
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une facture à afficher.")

    def show_facture_details(self, index: QModelIndex):
        facture_id = int(self.factures_table.item(index.row(), 0).text())
        facture = get_facture_by_id(facture_id)
        if not facture:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Détails de la facture #{facture_id}")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        
        info_layout = QFormLayout()
        info_layout.addRow("Client :", QLabel(facture.client.full_name))
        info_layout.addRow("Date :", QLabel(facture.date.strftime("%d/%m/%Y")))
        info_layout.addRow("Statut :", QLabel("Payée" if facture.statut else "Impayée"))
        info_layout.addRow("Type de paiement :", QLabel(facture.type_paiment))

        layout.addLayout(info_layout)

        
        items_table = QTableWidget()
        items_table.setColumnCount(4)
        items_table.setHorizontalHeaderLabels(["Description", "Quantité", "Prix unitaire", "Total"])
        items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        total = 0
        for item in facture.items:
            row = items_table.rowCount()
            items_table.insertRow(row)

            items_table.setItem(row, 0, QTableWidgetItem(item.description))
            items_table.setItem(row, 1, QTableWidgetItem(str(item.quantite)))
            items_table.setItem(row, 2, QTableWidgetItem(f"{item.unit_price:.2f}"))

            item_total = item.quantite * item.unit_price
            items_table.setItem(row, 3, QTableWidgetItem(f"{item_total:.2f}"))

            total += item_total

        layout.addWidget(QLabel("Articles de la facture :"))
        layout.addWidget(items_table)
        layout.addWidget(QLabel(f"Veuillez sélectionner une facture pour générer le PDF."))

        dialog.setLayout(layout)
        dialog.exec()

    
    def generate_pdf(self, facture_id=None):
        
        if not facture_id:
            selected_row = self.factures_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Attention",  "Veuillez sélectionner une facture pour générer le PDF.")
                return
            facture_id = int(self.factures_table.item(selected_row, 0).text())
        
        facture = get_facture_by_id(facture_id)
        if not facture:
            return
        

        if not os.path.exists("invoices"):
            os.makedirs("invoices")
        
        file_name = f"invoices/facture_{facture_id}.pdf"
        
        doc = SimpleDocTemplate(file_name, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # محتوى PDF
        elements = []
        
        # عنوان الفاتورة
        title = Paragraph(f" NUM FACTURE: {facture_id}", styles['Title'])
        elements.append(title)
        
        # معلومات الفاتورة
        info = [
            f"NOM CLIENT: {facture.client.full_name}",
            f"DATE: {facture.date}",
            f"STATUT: {'PAYEE' if facture.statut else ' NON PAYEE'}",
            f"TYPE DE PAIEMENT: {facture.type_paiment}"
        ]
        
        for line in info:
            elements.append(Paragraph(line, styles['Normal']))
            elements.append(Spacer(1, 10))
        
        elements.append(Spacer(1, 20))
        
        # جدول العناصر
        items_data = [["DESCRIPTION", "QUANTITE", "PRIX UNITAIRE", "TOTAL"]]
        total = 0
        
        for item in facture.items:
            item_total = item.quantite * item.unit_price
            total += item_total
            items_data.append([
                item.description,
                str(item.quantite),
                f"{item.unit_price:.2f}",
                f"{item_total:.2f}"
            ])
        
        items_table = Table(items_data)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.green),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        # الإجمالي
        total_text = Paragraph(f"<b> LE PRIX TOTAL EST: {total:.2f} DIRHAM</b>", styles['Normal'])
        elements.append(total_text)
        
        # إنشاء ملف PDF
        doc.build(elements)
        QMessageBox.information(self,  "PDF généré", f"Le fichier PDF a été créé : {file_name}")
        if platform.system() == "Windows":
            path=r"C:\Users\dell\Desktop\SmartBilling"
            file_name=os.path.join(path,file_name)
            os.startfile(file_name)
    
    def send_email(self):

            selected_row = self.factures_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Attention", "Veuillez sélectionner une facture à envoyer.")
                return

            facture_id = int(self.factures_table.item(selected_row, 0).text())
            facture = get_facture_by_id(facture_id)

            if not facture or not facture.client.email:
                QMessageBox.warning(self, "Attention", "Le client n'a pas d'adresse e-mail.")
                return

            pdf_path = f"invoices/facture_{facture_id}.pdf"
            if not os.path.exists(pdf_path):
                self.generate_pdf(facture_id)

            sender_email = "your_email"
            sender_password = "wpbh sota wgvn lcwb glw9"
            smtp_server = "smtp.gmail.com"
            smtp_port = 587

            receiver_email = facture.client.email

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = f"Facture N° {facture_id}"

            body = f"""
                Bonjour,

                Veuillez trouver ci-joint la facture N° {facture_id} datée du {facture.date}.

                Cordialement,
                L'équipe comptabilité.
                """
            msg.attach(MIMEText(body, 'plain'))

            with open(pdf_path, "rb") as file:
                part = MIMEApplication(file.read(), Name=os.path.basename(pdf_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
                msg.attach(part)

            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()
                QMessageBox.information(self,  "Envoyé", f"La facture a été envoyée à {receiver_email}")
            except Exception as e:
                QMessageBox.critical(self,"Erreur", f"Échec de l'envoi de l'e-mail : {str(e)}")
