from app.db import SessionLocal
from app.models import User
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    from app.db import engine, Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    if db.query(User).count() == 0:
        users = [
            User(username="admin", password_hash=hash_password("admin123"), role="admin"),
            User(username="compte", password_hash=hash_password("compte123"), role="comptable"),
            User(username="com", password_hash=hash_password("com123"), role="commercial")
        ]
        db.add_all(users)
        db.commit()
    db.close()
from werkzeug.security import check_password_hash

def check_login(username, password):
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    db.close()

    if not user:
        print(f"User '{username}' not found.")
        return None  # إذا لم يتم العثور على المستخدم
    
    # التحقق من كلمة المرور المشفرة باستخدام hashlib
    if user.password_hash == hash_password(password):
        return user.role  # إذا كانت كلمة المرور صحيحة، الرجاع الدور
    else:
        print("Incorrect password.")
        return None  # إذا كانت كلمة المرور غير صحيحة