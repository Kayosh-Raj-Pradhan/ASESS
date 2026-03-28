from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from asess.core.database import SessionLocal
from asess.core.security import SECRET_KEY, ALGORITHM
from asess.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

VALID_ROLES = ["superadmin", "admin", "doctor", "staff"]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# --- Role-based access checkers ---

def check_superadmin(current_user: User = Depends(get_current_user)):
    """Only superadmin can access."""
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin access required")
    return current_user

def check_admin(current_user: User = Depends(get_current_user)):
    """Admin or superadmin can access."""
    if current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def check_doctor(current_user: User = Depends(get_current_user)):
    """Doctor, admin, or superadmin can access."""
    if current_user.role not in ("doctor", "admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Doctor access required")
    return current_user

def check_staff_or_above(current_user: User = Depends(get_current_user)):
    """Any authenticated user with a valid role."""
    if current_user.role not in VALID_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user