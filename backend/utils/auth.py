from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from decouple import config
from models.schemas import TokenData, UserInDB
from utils.database import get_database
import re

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings - Use environment variables directly
import os

# Load from environment or use defaults
SECRET_KEY = os.environ.get("SECRET_KEY", "oAjF8gG618uiqvAOft0o_J3_antPMd_mjjxrpk7cKXlK2a2x58-lu4r2LC0cM3U1")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # Truncate password if longer than 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def validate_temple_email(email: str) -> bool:
    """Validate that the email is a temple.edu email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@temple\.edu$'
    return bool(re.match(pattern, email))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_email(email: str):
    """Get user from database by email"""
    db = await get_database()
    user = await db.users.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return UserInDB(**user)
    return None

async def authenticate_user(email: str, password: str):
    """Authenticate user with email and password"""
    user = await get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"DEBUG: Received token: {credentials.credentials[:50]}...")  # Only show first 50 chars
        print(f"DEBUG: SECRET_KEY configured: {SECRET_KEY[:10]}...")  # Only show first 10 chars
        print(f"DEBUG: ALGORITHM: {ALGORITHM}")
        
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG: Decoded payload: {payload}")
        
        email: str = payload.get("sub")
        if email is None:
            print("DEBUG: No 'sub' field in token payload")
            raise credentials_exception
        
        print(f"DEBUG: Email from token: {email}")
        token_data = TokenData(email=email)
    except JWTError as e:
        print(f"DEBUG: JWT decode error: {e}")
        raise credentials_exception
    
    user = await get_user_by_email(email=token_data.email)
    if user is None:
        print(f"DEBUG: User not found in database: {token_data.email}")
        raise credentials_exception
    
    print(f"DEBUG: User authenticated successfully: {user.email}")
    return user