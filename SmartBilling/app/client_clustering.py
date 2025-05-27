import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from app.db import engine

def cluster_clients():

    query = """
        SELECT f.client_id, 
               MAX(f.date) AS last_purchase, 
               COUNT(f.id) AS frequency,
               SUM(i.quantite * i.unit_price) AS monetary
        FROM facture f
        JOIN facture_items i ON f.id = i.facture_id
        WHERE f.statut = true
        GROUP BY f.client_id
    """
    df = pd.read_sql(query, engine)

    if df.empty:
        print("❌ Il n'y a pas suffisamment de données pour analyser les clients.")
        return pd.DataFrame()


    df['last_purchase'] = pd.to_datetime(df['last_purchase'])
    today = pd.to_datetime('today')
    df['recency'] = (today - df['last_purchase']).dt.days

    rfm_df = df[['client_id', 'recency', 'frequency', 'monetary']].copy()


    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_df[['recency', 'frequency', 'monetary']])


    kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
    rfm_df['cluster'] = kmeans.fit_predict(rfm_scaled)

    cluster_order = rfm_df.groupby('cluster')['monetary'].mean().sort_values()
    labels_map = {
        cluster_order.index[0]: "Actif",
        cluster_order.index[1]: "Inactif",
        cluster_order.index[2]: "Prospect",
        cluster_order.index[3]: "VIP"
    }
    rfm_df['type_client'] = rfm_df['cluster'].map(labels_map)


    return rfm_df[['client_id', 'recency', 'frequency', 'monetary', 'type_client']]
