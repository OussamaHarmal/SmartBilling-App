from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QPushButton,
                             QListWidget, QListWidgetItem, QStackedWidget, QApplication,)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from ui.dashboard_page import DashboardPage
from ui.client_from import ClientForm
from ui.facture_form import FactureWindow
from ui.stats_page import PageStatistiques
from ui.predict_window import PredictWindow
from ui.clustering_window import ClientClusteringWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de gestion - panneau de contrôle")
        self.setGeometry(100, 100, 1280, 720)

        
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setStyleSheet("background-color: white;")

        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #fcf9f7; 
                color: black;
                font-size: 18px;
                font-weight : Bold;
                padding: 20px 0;
                border: none;
            }

            QListWidget::item {
                padding: 12px 20px;
                border-radius: 8px;
                margin: 6px 10px;
                color: black;
            }

            QListWidget::item:hover {
                background-color: #374151;
                color: #d1d5db;
            }

            QListWidget::item:selected {
                background-color: #10b981; 
                color: white;
                font-weight: bold;
            }
        """)




        home_item = QListWidgetItem("  🏠  ACCUEIL")
        clients_item = QListWidgetItem("  👥  CLIENTS")
        factures_item = QListWidgetItem("  🧾  FACTURES")
        
        
        self.sidebar.addItem(home_item)
        self.sidebar.addItem(clients_item)
        self.sidebar.addItem(factures_item)
        self.sidebar.addItem(QListWidgetItem("📈 Statistique"))


        
        self.pages = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.client_page = ClientForm()
        self.facture_page = FactureWindow()

        self.pages.addWidget(self.dashboard_page)  
        self.pages.addWidget(self.client_page)     
        self.pages.addWidget(self.facture_page)    
        self.stats_page = PageStatistiques()
        self.pages.addWidget(self.stats_page)

        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)

        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)
        self.stats_page.layout().addWidget(self.create_predict_button())
        self.stats_page.layout().addWidget(self.create_clusterig_button())
        
        
    def create_clusterig_button(self):
        btn_analyse_clients = QPushButton("Analyser Clients")
        btn_analyse_clients.clicked.connect(self.open_client_clustering)
        return btn_analyse_clients
    
    def open_client_clustering(self):
        self.client_window = ClientClusteringWindow()
        self.client_window.show()
        
    def create_predict_button(self):
        btn = QPushButton("prediction")
        btn.clicked.connect(self.open_predict_window)
        return btn

    # الميثود الجديدة:
    def open_predict_window(self):
        self.predict_window = PredictWindow()
        self.predict_window.show()
