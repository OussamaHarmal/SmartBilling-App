from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, Double, TIMESTAMP, func, Boolean, ForeignKey

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    phone = Column(String)
    adresse = Column(String)
    ville = Column(String)
    company_name = Column(String)
    statut = Column(String) 
    activity = Column(String)  
    factures = relationship("Facture", back_populates="client")

class Facture(Base):
    __tablename__ = "facture"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    date = Column(TIMESTAMP)
    statut = Column(Boolean)
    type_paiment=Column(String)
    client = relationship("Client", back_populates="factures")
    items = relationship("FactureItem", back_populates="facture", cascade="all, delete")
    @property
    def total(self):
        return sum(item.total for item in self.items)

class FactureItem(Base):
    __tablename__ = "facture_items"

    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey("facture.id"))
    description = Column(Text)
    quantite = Column(Integer)
    unit_price = Column(Double)

    facture = relationship("Facture", back_populates="items")
    @property
    def total(self):
        return self.quantite * self.unit_price

from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)

    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
