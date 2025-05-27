from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QDateEdit,
    QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from app.db import SessionLocal
from app.models import Facture

class PageStatistiques(QWidget):
    def __init__(self):
        super().__init__()
        self.session = SessionLocal()

        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Segoe UI';
            }
            QLabel {
                font-size: 15px;
                color: Black;
            }
            QComboBox, QDateEdit {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
                color : Black
            }
            QComboBox QAbstractItemView {
                background-color: #3aea6d;
                color: black;
                selection-background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(20, 20, 20, 20)
        self.layout_principal.setSpacing(15)

        titre = QLabel("📊 Statistiques de facturation")
        titre.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout_principal.addWidget(titre)

        # Filtres
        filtres_layout = QHBoxLayout()

        self.filtre_ville = QComboBox()
        self.filtre_ville.addItem("Toutes")

        self.filtre_statut = QComboBox()
        self.filtre_statut.addItems(["Tous", "Payée", "Impayée"])

        self.date_debut = QDateEdit(calendarPopup=True)
        self.date_debut.setDisplayFormat("yyyy-MM-dd")
        self.date_debut.setDate(QDate(2023, 1, 1))

        self.date_fin = QDateEdit(calendarPopup=True)
        self.date_fin.setDisplayFormat("yyyy-MM-dd")
        self.date_fin.setDate(QDate.currentDate())

        
        calendar_style = """
        QCalendarWidget QWidget {
            background-color: #1e1e1e;
            color: white;
        }
        QCalendarWidget QAbstractItemView {
            selection-background-color: #2563eb;
            selection-color: white;
            font-size: 14px;
        }
        """
        self.date_debut.calendarWidget().setStyleSheet(calendar_style)
        self.date_fin.calendarWidget().setStyleSheet(calendar_style)

        filtres_layout.addWidget(QLabel("📍 Ville:"))
        filtres_layout.addWidget(self.filtre_ville)
        filtres_layout.addWidget(QLabel("💳 Statut:"))
        filtres_layout.addWidget(self.filtre_statut)
        filtres_layout.addWidget(QLabel("🗓️ De:"))
        filtres_layout.addWidget(self.date_debut)
        filtres_layout.addWidget(QLabel("🗓️ à:"))
        filtres_layout.addWidget(self.date_fin)

        self.layout_principal.addLayout(filtres_layout)

        
        self.bouton_export = QPushButton("📤 Exporter en PDF")
        self.layout_principal.addWidget(self.bouton_export, alignment=Qt.AlignmentFlag.AlignRight)

        
        self.figure = Figure(facecolor="#f9fafb")
        self.canvas = FigureCanvas(self.figure)
        self.layout_principal.addWidget(self.canvas)

        
        self.bouton_export.clicked.connect(self.exporter_en_pdf)
        self.filtre_ville.currentIndexChanged.connect(self.mettre_a_jour_graphique)
        self.filtre_statut.currentIndexChanged.connect(self.mettre_a_jour_graphique)
        self.date_debut.dateChanged.connect(self.mettre_a_jour_graphique)
        self.date_fin.dateChanged.connect(self.mettre_a_jour_graphique)

        self.charger_donnees()
        self.mettre_a_jour_graphique()

    def charger_donnees(self):
        factures = self.session.query(Facture).all()
        data = []

        for f in factures:
            client = f.client
            montant = sum(item.quantite * item.unit_price for item in f.items)
            data.append({
                "date": pd.to_datetime(f.date),
                "ville": client.ville if client else "Inconnu",
                "statut": "Payée" if f.statut else "Impayée",
                "montant": montant
            })

        self.df = pd.DataFrame(data)

        
        villes = sorted(set(self.df["ville"]))
        self.filtre_ville.addItems(villes)

    def mettre_a_jour_graphique(self):
        df = self.df.copy()

        ville = self.filtre_ville.currentText()
        if ville != "Toutes":
            df = df[df["ville"] == ville]

        debut = pd.Timestamp(self.date_debut.date().toString("yyyy-MM-dd"))
        fin = pd.Timestamp(self.date_fin.date().toString("yyyy-MM-dd"))
        df = df[(df["date"] >= debut) & (df["date"] <= fin)]

        
        df_revenu = df.copy()
        statut = self.filtre_statut.currentText()
        if statut != "Tous":
            df_revenu = df_revenu[df_revenu["statut"] == statut]

        self.figure.clear()
        axe1 = self.figure.add_subplot(121)
        axe2 = self.figure.add_subplot(122)

        if not df.empty:
            df_revenu["mois"] = df_revenu["date"].dt.to_period("M").astype(str)
            revenus = df_revenu.groupby("mois")["montant"].sum()

            axe1.bar(revenus.index, revenus.values, color="#3b82f6")
            axe1.set_title("💰 Revenus mensuels")
            axe1.tick_params(axis='x', rotation=45)

            repartition = df["statut"].value_counts()
            axe2.pie(repartition, labels=repartition.index, autopct='%1.1f%%', colors=["#10b981", "#ef4444"])
            axe2.set_title("📊 Répartition des statuts")
        else:
            axe1.text(0.5, 0.5, "Aucune donnée", ha='center', va='center')
            axe2.text(0.5, 0.5, "Aucune donnée", ha='center', va='center')

        self.canvas.draw()

    def exporter_en_pdf(self):
        if self.df.empty:
            QMessageBox.warning(self, "Aucune donnée", "Impossible d’exporter un graphique vide.")
            return

        chemin, _ = QFileDialog.getSaveFileName(self, "Exporter en PDF", "", "Fichiers PDF (*.pdf)")
        if chemin:
            try:
                self.figure.savefig(chemin)
                QMessageBox.information(self, "✅ Export réussi", f"PDF enregistré dans :\n{chemin}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
