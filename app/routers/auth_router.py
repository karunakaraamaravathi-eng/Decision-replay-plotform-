from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, AuditLog
from app.schemas import UserCreate, UserLogin, UserResponse, Token, TokenVerifyResponse, PasswordChange
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    # Validate role
    if user_in.role not in settings.VALID_ROLES:
        user_in.role = "Employee"

    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        department=user_in.department or "Engineering"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Audit log
    audit = AuditLog(
        user_id=new_user.id,
        action="REGISTER",
        entity_type="User",
        entity_id=new_user.id,
        details=f"User registered with role: {new_user.role}"
    )
    db.add(audit)
    db.commit()

    return new_user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with JSON payload and return JWT bearer token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled."
        )

    # Generate JWT
    token_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "full_name": user.full_name
    }
    access_token = create_access_token(data=token_payload)

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="LOGIN",
        entity_type="User",
        entity_id=user.id,
        details="User successfully logged in"
    )
    db.add(audit)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email
    }

@router.post("/token", response_model=Token, include_in_schema=True)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 standard form-data login endpoint for Swagger UI Authorize integration."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled."
        )

    token_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "full_name": user.full_name
    }
    access_token = create_access_token(data=token_payload)

    audit = AuditLog(
        user_id=user.id,
        action="SWAGGER_AUTH",
        entity_type="User",
        entity_id=user.id,
        details="Authenticated via OAuth2 Password Form"
    )
    db.add(audit)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return currently authenticated user profile."""
    return current_user

@router.get("/verify-token", response_model=TokenVerifyResponse)
def verify_token(current_user: User = Depends(get_current_user)):
    """Verify if active JWT bearer token is valid and return associated user context."""
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "full_name": current_user.full_name
    }

@router.post("/change-password")
def change_password(
    pwd_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Allow logged in user to update their account password securely."""
    if not verify_password(pwd_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password verification failed."
        )

    current_user.hashed_password = hash_password(pwd_data.new_password)
    db.commit()

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="PASSWORD_CHANGE",
        entity_type="User",
        entity_id=current_user.id,
        details="User password changed successfully"
    )
    db.add(audit)
    db.commit()

    return {"message": "Password updated successfully"}

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Log out current user (records audit log)."""
    audit = AuditLog(
        user_id=current_user.id,
        action="LOGOUT",
        entity_type="User",
        entity_id=current_user.id,
        details="User logged out"
    )
    db.add(audit)
    db.commit()
    return {"message": "Logged out successfully"}
