from .db import SessionLocal
from .models import Client
from .db import get_connection
import pandas as pd


def add_client(data):
    db = SessionLocal()
    try:
        new_client = Client(
            full_name=data["full_name"],
            email=data.get("email"),
            phone=data.get("phone"),
            adresse=data.get("adresse"),
            ville=data.get("ville"),
            company_name=data.get("company_name"),
            statut=data.get("status"),
            activity=data.get("activity")
        )
        db.add(new_client)
        db.commit()
    finally:
        db.close()

def get_all_clients():
    db = SessionLocal()
    try:
        return db.query(Client).all()
    finally:
        db.close()

def delete_client(client_id):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if client:
            db.delete(client)
            db.commit()
            return True
        return False
    finally:
        db.close()

def update_client_by_id(client_id, updated_data):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return False
        
        for key, value in updated_data.items():
            setattr(client, key, value)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print("Error updating client:", e)
        return False
    finally:
        db.close()





def get_filtered_clients(city=None, status=None, activity_type=None):
    conn = get_connection()
    query = "SELECT * FROM clients WHERE 1=1"
    params = []

    if city and city != "toutes ville":
        query += " AND ville = %s"
        params.append(city)

    if status and status != "toutes statut":
        query += " AND status = %s"
        params.append(status)

    if activity_type and activity_type != "toutes activity":
        query += " AND activity_type = %s"
        params.append(activity_type)

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df
