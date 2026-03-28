from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from asess.core.database import SessionLocal
from asess.schemas.user import UserCreate, UserRead, UserUpdate, Token
from asess.services import user_service
from asess.models.user import User
from asess.core.security import create_tokens
from asess.core.dependencies import get_current_user, check_admin, check_superadmin
from typing import List

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user_in)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token, refresh_token = create_tokens(user.email, user.role)
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Return info for the currently authenticated user."""
    return current_user


# ===== Superadmin Endpoints (CRUD admins only) =====

@router.get("/superadmin/users", response_model=List[UserRead])
def superadmin_list_admins(
    current_user: User = Depends(check_superadmin),
    db: Session = Depends(get_db)
):
    """List admin users only (superadmin only)."""
    return db.query(User).filter(User.role == "admin").order_by(User.id).all()

@router.put("/superadmin/users/{user_id}", response_model=UserRead)
def superadmin_update_admin(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(check_superadmin),
    db: Session = Depends(get_db)
):
    """Update an admin user (superadmin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Superadmin can only manage admin users")
    
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/superadmin/users/{user_id}")
def superadmin_delete_admin(
    user_id: int,
    current_user: User = Depends(check_superadmin),
    db: Session = Depends(get_db)
):
    """Delete an admin user (superadmin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Superadmin can only delete admin users")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(user)
    db.commit()
    return {"detail": "Admin user deleted successfully"}


# ===== Admin Endpoints (CRUD doctors & staff) =====

@router.get("/admin/users", response_model=List[UserRead])
def list_all_users(
    admin: User = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """List users. Admin sees doctors, staff, and other admins (not superadmins)."""
    if admin.role == "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin should use /superadmin/users endpoint")
    # Admin sees doctors, staff, and other admins (not superadmins)
    return db.query(User).filter(User.role != "superadmin").order_by(User.id).all()

@router.put("/admin/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin: User = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Update a user's role or active status (admin only, doctors & staff)."""
    if admin.role == "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin should use /superadmin/users endpoint")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Admin can only manage doctors/staff, not other admins or superadmins
    if user.role not in ("doctor", "staff"):
        raise HTTPException(status_code=403, detail="You can only manage doctor and staff users")
    
    if user_update.role is not None:
        # Admin cannot promote to admin/superadmin
        if admin.role == "admin" and user_update.role not in ("doctor", "staff"):
            raise HTTPException(status_code=403, detail="You cannot assign admin or superadmin roles")
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only, doctors & staff)."""
    if admin.role == "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin should use /superadmin/users endpoint")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    if user.role not in ("doctor", "staff"):
        raise HTTPException(status_code=403, detail="You can only delete doctor and staff users")
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}
