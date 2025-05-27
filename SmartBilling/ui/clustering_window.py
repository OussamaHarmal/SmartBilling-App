from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox
from PyQt6.QtCore import Qt
from app.client_clustering import cluster_clients

class ClientClusteringWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 Analyse des Clients")
        self.resize(700, 500)

        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Segoe UI';
                color: #111827;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e5e7eb;
                font-size: 14px;
                gridline-color: #d1d5db;
            }
            QHeaderView::section {
                background-color: #e5e7eb;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #d1d5db;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.button = QPushButton("🔍 Afficher Analyse Client")
        self.button.clicked.connect(self.load_clusters)
        layout.addWidget(self.button)

        self.filter_box = QComboBox()
        self.filter_box.addItems(["Tous", "VIP", "Actif", "Inactif", "Prospect"])
        self.filter_box.currentIndexChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_box)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID الزبون",
            "Recency (أيام)",
            "Frequency (عدد الفواتير)",
            "Prix total",
            "Type client"
        ])
        layout.addWidget(self.table)

        self.df = None
        self.setLayout(layout)

    def load_clusters(self):
        self.df = cluster_clients()
        if self.df.empty:
            return
        self.apply_filter()

    def apply_filter(self):
        if self.df is None:
            return

        selected_type = self.filter_box.currentText()
        if selected_type == "Tous":
            filtered_df = self.df
        else:
            filtered_df = self.df[self.df['type_client'] == selected_type]

        self.table.setRowCount(len(filtered_df))

        for row in range(len(filtered_df)):
            self.table.setItem(row, 0, QTableWidgetItem(str(filtered_df.iloc[row]['client_id'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(filtered_df.iloc[row]['recency'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(filtered_df.iloc[row]['frequency'])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{filtered_df.iloc[row]['monetary']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(filtered_df.iloc[row]['type_client']))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
