from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import plotly.graph_objs as go
import pandas as pd
from app.revenue_predictor import run_revenue_prediction, predict_next_month
import tempfile
import os


class PredictWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔮 Prédiction des Revenus (Interactive)")
        self.setMinimumSize(1000, 600)

        self.temp_file = None  # Pour garder le chemin temporaire

        layout = QVBoxLayout()

        self.result_label = QLabel("⬇️ Cliquez sur 'Prédire' pour voir les résultats.")
        layout.addWidget(self.result_label)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        self.predict_btn = QPushButton("🔁 Prédire les revenus")
        self.predict_btn.clicked.connect(self.run_prediction)
        layout.addWidget(self.predict_btn)

        self.export_btn = QPushButton("📤 Exporter le graphe (HTML)")
        self.export_btn.clicked.connect(self.export_graph)
        layout.addWidget(self.export_btn)

        self.setLayout(layout)

    def run_prediction(self):
        df, evaluations, best_model_info = run_revenue_prediction()

        if df.empty:
            self.result_label.setText("❌ Aucune donnée.")
            return

        # Prédiction du mois suivant
        next_month_prediction = None
        if best_model_info:
            try:
                last_features = df.iloc[-1][[
                    'revenu_prev', 'qte_prev', 'prix_unit_prev',
                    'nb_factures_prev', 'nb_clients_prev',
                    'revenu_diff', 'revenu_ratio', 'rolling_mean_3', 'is_quarter_end'
                ]]
                next_month_prediction = predict_next_month(best_model_info[1], last_features)
            except Exception as e:
                print(f"Erreur prédiction: {e}")

        fig = go.Figure()

        # Données réelles
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['revenu_total'],
            mode='lines+markers',
            name='📌 Revenu Réel',
            line=dict(color='#00d4ff', width=3),
            hovertemplate='Mois: %{x}<br>Revenu réel: %{y:.2f}<extra></extra>'
        ))

        result_text = "📊 Résultats des modèles :<br>"
        colors = ['#ff6b6b', '#ffa500', '#9b59b6', '#3498db']
        color_idx = 0

        for model_name, info in evaluations.items():
            y_pred = info['y_pred_test']
            mae = info['mae_test']
            r2 = info['r2_test']
            months = df['month'][-len(y_pred):]

            fig.add_trace(go.Scatter(
                x=months,
                y=y_pred,
                mode='lines+markers',
                name=f"{model_name} (R²: {r2:.2f})",
                line=dict(color=colors[color_idx % len(colors)], width=2),
                hovertemplate='Mois: %{x}<br>Prédiction: %{y:.2f}<extra></extra>'
            ))

            result_text += f"🔹 {model_name}: MAE = {mae:.2f}, R² = {r2:.2f}<br>"
            color_idx += 1

        if best_model_info:
            best_name, best_info = best_model_info
            result_text += f"<br>✅ <b>Meilleur modèle</b>: {best_name} (R² = {best_info['r2_test']:.2f})"

            if best_info['r2_test'] < 0.3:
                result_text += "<br>⚠️ <i>Attention : les performances sont faibles. Résultats à interpréter avec prudence.</i>"

        if next_month_prediction:
            last_month = df['month'].iloc[-1]
            next_month = last_month + pd.DateOffset(months=1)

            fig.add_trace(go.Scatter(
                x=[next_month],
                y=[next_month_prediction],
                mode='markers',
                name='🔮 Prédiction Future',
                marker=dict(size=15, color='#00ff88', symbol='star'),
                hovertemplate='Prédiction: %{y:.2f} MAD<extra></extra>'
            ))

            # Annotation
            fig.add_annotation(
                x=next_month,
                y=next_month_prediction,
                text=f"{next_month_prediction:.0f} MAD",
                showarrow=True,
                arrowhead=2,
                font=dict(color='white'),
                bgcolor='#00ff88'
            )

            result_text += f"<br>🔮 <b>Prédiction prochaine</b>: {next_month_prediction:.2f} MAD"

        self.result_label.setText(result_text)

        # Configuration du layout du graphe
        fig.update_layout(
            width=1000,
            height=550,
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#1e1e1e',
            font=dict(color='white'),
            legend=dict(x=0, y=1.1, orientation='h'),
            title='📈 Prédictions vs Réel',
            xaxis=dict(title='Mois'),
            yaxis=dict(title='Revenu')
        )

        # Enregistrer le graphe dans un fichier temporaire
        if self.temp_file:
            os.unlink(self.temp_file)  # Supprimer l'ancien fichier

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        fig.write_html(temp_file.name)
        self.temp_file = temp_file.name
        self.web_view.load(QUrl.fromLocalFile(temp_file.name))

    def export_graph(self):
        if self.temp_file:
            file_name, _ = QFileDialog.getSaveFileName(self, "Enregistrer le graphe", "", "HTML Files (*.html)")
            if file_name:
                with open(self.temp_file, 'rb') as src, open(file_name, 'wb') as dst:
                    dst.write(src.read())

    def closeEvent(self, event):
        if self.temp_file and os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        super().closeEvent(event)
