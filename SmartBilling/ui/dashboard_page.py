from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app.db import SessionLocal
from app.models import Client, Facture

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        self.session = SessionLocal()
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QTableWidget {
                background-color: white;
                border-radius: 12px;
                font-size: 14px;
                color: #374151;
                border: none;
            }
            QHeaderView::section {
                background-color: #10b981;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
            }
            QPushButton {
                background-color: #10b981;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)


        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title = QLabel("📊 Tableau de bord")
        title.setStyleSheet("font-size: 30px; font-weight: 600; color: #2c3e50;")
        main_layout.addWidget(title)

        # الكروت
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        cards_layout.addWidget(self.create_card("👥 Clients", self.get_client_count(), "#10b981"))
        cards_layout.addWidget(self.create_card("📄 Factures", self.get_facture_count(), "#3b82f6"))
        cards_layout.addWidget(self.create_card("💸 Impayé", self.get_unpaid_factures(), "#f97316"))
        main_layout.addLayout(cards_layout)

        # عنوان الجدول
        recent_label = QLabel("🧾 Derniére Facture")
        recent_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(recent_label)

        # جدول آخر الفواتير
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "Client", "Date", "Statut"])
        factures = self.session.query(Facture).order_by(Facture.date.desc()).limit(5).all()
        table.setRowCount(len(factures))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 12px;
                font-size: 14px;
                color: #374151;
            }
            QHeaderView::section {
                background-color: #10b981;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
            }
        """)

        for row, f in enumerate(factures):
            table.setItem(row, 0, QTableWidgetItem(str(f.id)))
            table.setItem(row, 1, QTableWidgetItem(f.client.full_name if f.client else ""))
            table.setItem(row, 2, QTableWidgetItem(str(f.date.date())))
            table.setItem(row, 3, QTableWidgetItem("✅ Payé" if f.statut else "❌ Impayé"))

        main_layout.addWidget(table)

       

        self.setLayout(main_layout)

    def create_card(self, title, value, color):
        card = QWidget()
        card.setStyleSheet(f"""
            background-color: white;
            border-radius: 16px;
            padding: 20px;
            color: #374151;
            border: 2px solid {color};
        """)
        layout = QVBoxLayout()
        label_icon = QLabel(title.split()[0])
        label_icon.setFont(QFont("Arial", 24))
        label_text = QLabel(" ".join(title.split()[1:]))
        label_text.setStyleSheet("font-size: 16px; color: #6b7280;")
        label_value = QLabel(str(value))
        label_value.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        layout.addWidget(label_icon)
        layout.addWidget(label_value)
        layout.addWidget(label_text)
        card.setLayout(layout)
        return card

    def get_client_count(self):
        return self.session.query(Client).count()

    def get_facture_count(self):
        return self.session.query(Facture).count()

    def get_unpaid_factures(self):
        return self.session.query(Facture).filter(Facture.statut == False).count()
