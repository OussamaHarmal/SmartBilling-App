# 📄 app/init_db.py
from app.db import SessionLocal
from app.models import User

def init_db():
    from app.db import engine, Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    if db.query(User).count() == 0:
        users = [
            User(username="admin", password_hash=User().set_password("admin123"), role="admin"),
            User(username="compte", password_hash=User().set_password("compte123"), role="comptable"),
            User(username="com", password_hash=User().set_password("com123"), role="commercial")
        ]
        db.add_all(users)
        db.commit()
    db.close()
