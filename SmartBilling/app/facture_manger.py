# facture_manager.py
from .db import SessionLocal
from .models import Facture, FactureItem


def add_facture(data):
    """
    Crée une nouvelle facture avec ses items associés.
    data: dict avec clés 'client_id', 'date', 'statut', 'type_paiment', 'items'
    """
    session = SessionLocal()
    try:
        items_data = data.pop("items", [])
        # Création de l'objet Facture
        facture = Facture(
            client_id=data.get("client_id"),
            date=data.get("date"),
            statut=data.get("statut"),
            type_paiment=data.get("type_paiment")
        )
        # Ajout des items via la relation
        for item in items_data:
            facture.items.append(
                FactureItem(
                    description=item["description"],
                    quantite=item["quantite"],
                    unit_price=item["unit_price"]
                )
            )
        session.add(facture)
        session.commit()
        session.refresh(facture)
        return facture
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_all_factures():
    """Récupère toutes les factures avec leurs items."""
    with SessionLocal() as session:
        factures = session.query(Facture).all()
        # Forcer le chargement des items
        for f in factures:
            _ = f.items
        return factures


def delete_facture(facture_id):
    """Supprime une facture et ses items (cascade)."""
    with SessionLocal() as session:
        f = session.query(Facture).filter(Facture.id == facture_id).first()
        if f:
            session.delete(f)
            session.commit()
            return True
        return False


from sqlalchemy.orm import joinedload

def get_facture_by_id(facture_id):
    """Retourne une facture avec client et items."""
    with SessionLocal() as session:
        f = session.query(Facture)\
            .options(joinedload(Facture.client), joinedload(Facture.items))\
            .filter(Facture.id == facture_id)\
            .first()
        return f

def update_facture(facture_id, updated_data):
    session = SessionLocal()
    try:
        facture = session.query(Facture).filter(Facture.id == facture_id).first()
        if not facture:
            return False

        # تحديث الحقول الرئيسية
        facture.client_id = updated_data["client_id"]
        facture.date = updated_data["date"]
        facture.statut = updated_data["statut"]
        facture.type_paiment = updated_data["type_paiment"]

        # مسح العناصر القديمة (اختياري حسب التصميم)
        session.query(FactureItem).filter(FactureItem.facture_id == facture_id).delete()

        # إضافة العناصر الجديدة
        for item_data in updated_data["items"]:
            item = FactureItem(
                facture_id=facture_id,
                description=item_data["description"],
                quantite=item_data["quantite"],
                unit_price=item_data["unit_price"]
            )
            session.add(item)

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
        
def update_facture_statut(facture_id, new_statut):
    session = SessionLocal()
    try:
        facture = session.query(Facture).get(facture_id)
        if facture:
            facture.statut = new_statut
            session.commit()
            return True
    except Exception as e:
        print("Error updating statut:", e)
    finally:
        session.close()
    return False
