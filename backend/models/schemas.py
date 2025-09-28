from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Annotated, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

# Simplified ObjectId handling for Pydantic v2
PyObjectId = Annotated[str, Field(description="MongoDB ObjectId as string")]

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    points: int = Field(default=100)  # Starting points

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserInDB(UserResponse):
    hashed_password: str

# Establishment Models
class Location(BaseModel):
    latitude: float
    longitude: float
    address: str

class Establishment(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    category: str
    location: Location
    image_url: Optional[str] = None
    is_active: bool = True
    distance: Optional[float] = None  # Distance in miles from user location

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Order Models
class OrderItem(BaseModel):
    name: str
    quantity: int
    price: float
    notes: Optional[str] = None

class OrderCreate(BaseModel):
    establishment_id: str
    items: List[OrderItem]
    delivery_location: Location
    special_instructions: Optional[str] = None
    delivery_points: int

class OrderUpdate(BaseModel):
    status: OrderStatus
    deliverer_id: Optional[str] = None
    completion_image_url: Optional[str] = None

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    customer_id: str
    deliverer_id: Optional[str] = None
    establishment_id: str
    items: List[OrderItem]
    delivery_location: Location
    special_instructions: Optional[str] = None
    delivery_points: int
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completion_image_url: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None