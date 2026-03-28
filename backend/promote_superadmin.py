"""Run this inside the backend container to promote a user to superadmin.
Usage: docker exec -it asess-backend python promote_superadmin.py
"""
from asess.core.database import SessionLocal
from asess.models.user import User

def promote():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "kayoshrajpradhan@gmail.com").first()
        if not user:
            print("ERROR: User with email kayoshrajpradhan@gmail.com not found!")
            return
        
        old_role = user.role
        user.role = "superadmin"
        db.commit()
        print(f"SUCCESS: {user.full_name or user.username} ({user.email})")
        print(f"  Role changed: {old_role} -> superadmin")
    finally:
        db.close()

if __name__ == "__main__":
    promote()
