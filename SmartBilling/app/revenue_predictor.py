import pandas as pd
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor
from catboost import CatBoostRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from app.db import engine
import numpy as np

# 🟠 1. Chargement des données enrichies depuis la BDD
def extract_monthly_features():
    query = """
        SELECT 
            DATE_TRUNC('month', f.date) AS month,
            COUNT(DISTINCT f.id) AS nb_factures,
            COUNT(DISTINCT f.client_id) AS nb_clients,
            SUM(i.quantite) AS total_qte,
            AVG(i.quantite) AS moyenne_qte,
            AVG(i.unit_price) AS moyenne_prix_unit,
            COUNT(i.id) AS total_items,
            SUM(i.quantite * i.unit_price) AS revenu_total
        FROM facture f
        JOIN facture_items i ON f.id = i.facture_id
        WHERE f.statut = true
        GROUP BY month
        ORDER BY month
    """
    df = pd.read_sql(query, engine)
    return df

# 🟡 2. Feature Engineering: lag + indicateurs temporels
def prepare_features(df, show_corr=True):
    if df.empty:
        return pd.DataFrame(), None, None

    df['month'] = pd.to_datetime(df['month'])
    df = df.sort_values('month')

    # Lag features (mois précédent)
    df['revenu_prev'] = df['revenu_total'].shift(1)
    df['qte_prev'] = df['total_qte'].shift(1)
    df['prix_unit_prev'] = df['moyenne_prix_unit'].shift(1)
    df['nb_factures_prev'] = df['nb_factures'].shift(1)
    df['nb_clients_prev'] = df['nb_clients'].shift(1)

    # Nouvelles features
    df['revenu_diff'] = df['revenu_total'] - df['revenu_prev']
    df['revenu_ratio'] = df['revenu_total'] / df['revenu_prev']
    df['rolling_mean_3'] = df['revenu_total'].rolling(window=3).mean()
    df['is_quarter_end'] = df['month'].dt.month.isin([3, 6, 9, 12]).astype(int)

    # Nettoyage
    df_clean = df.dropna()

    # Features à utiliser
    feature_cols = [
        'revenu_prev',
        'qte_prev',
        'prix_unit_prev',
        'nb_factures_prev',
        'nb_clients_prev',
        'revenu_diff',
        'revenu_ratio',
        'rolling_mean_3',
        'is_quarter_end'
    ]

    X = df_clean[feature_cols].astype(float)
    y = df_clean['revenu_total'].astype(float)

    if show_corr:
        corr_matrix = df_clean[feature_cols + ['revenu_total']].corr()
        print("\n📊 Corrélation avec le revenu actuel:")
        print(corr_matrix['revenu_total'].drop('revenu_total').sort_values(ascending=False))

    return df_clean, X, y

# 🟢 3. Entraînement + Évaluation des modèles
def train_and_evaluate_models(X, y):
    # Split temporel : dernier 3 mois pour test
    X_train, X_test = X.iloc[:-3], X.iloc[-3:]
    y_train, y_test = y.iloc[:-3], y.iloc[-3:]

    models = {
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
        'CatBoost': CatBoostRegressor(iterations=200, learning_rate=0.09, depth=14, random_state=42, verbose=0),
        'XGBoost': XGBRegressor(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.5,
            colsample_bytree=0.5,
            random_state=42
        )
    }

    evaluations = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        evaluations[name] = {
            'model': model,
            'y_pred_train': y_pred_train,
            'y_pred_test': y_pred_test,
            'mae_train': mean_absolute_error(y_train, y_pred_train),
            'mae_test': mean_absolute_error(y_test, y_pred_test),
            'r2_train': r2_score(y_train, y_pred_train),
            'r2_test': r2_score(y_test, y_pred_test)
        }

    return evaluations

# 🔮 4. Prédiction du mois suivant
def predict_next_month(best_model_info, last_features):
    try:
        model = best_model_info['model']
        
        # Convertir en array numpy
        if isinstance(last_features, pd.Series):
            input_data = last_features.values.reshape(1, -1)
        else:
            input_data = np.array(last_features).reshape(1, -1)
        
        # Convertir en float pour éviter les erreurs
        input_data = input_data.astype(float)
        
        # Remplacer les valeurs problématiques
        input_data = np.nan_to_num(input_data, nan=0.0)
        
        prediction = model.predict(input_data)[0]
        
        # Pas de valeurs négatives
        if prediction < 0:
            prediction = 0
            
        return prediction
        
    except Exception as e:
        print(f"❌ Erreur prédiction: {e}")
        return None

# 🔵 5. Sélection du meilleur modèle (basé sur R² test)
def get_best_model(evaluations):
    best_model = None
    best_r2 = float('-inf')
    for name, info in evaluations.items():
        if info['r2_test'] > best_r2:
            best_model = (name, info)
            best_r2 = info['r2_test']
    return best_model

# 🧠 6. Fonction principale à appeler depuis l'interface
def run_revenue_prediction():
    df = extract_monthly_features()
    prepared_df, X, y = prepare_features(df, show_corr=True)

    if prepared_df.empty:
        return pd.DataFrame(), {}, None

    evaluations = train_and_evaluate_models(X, y)
    best_model = get_best_model(evaluations)

    return prepared_df, evaluations, best_model