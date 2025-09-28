from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta, datetime
from models.schemas import UserCreate, UserLogin, Token, UserResponse
from utils.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash, 
    validate_temple_email,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from utils.database import get_database
from bson import ObjectId

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    
    # Validate temple.edu email
    if not validate_temple_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be a valid temple.edu email address"
        )
    
    # Check if user already exists
    db = await get_database()
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Check if username is taken
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user_dict = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "points": 100,  # Starting points
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)  # Convert ObjectId to string
    
    return UserResponse(**user_dict)

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return JWT token"""
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Get user information by ID (for deliverer info, etc.)"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    db = await get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return UserResponse(**user)