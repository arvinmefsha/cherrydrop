from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from models.schemas import Establishment, UserResponse
from utils.auth import get_current_user
from utils.database import get_database
import math

router = APIRouter()

# Hardcoded establishments near Temple University campus
TEMPLE_ESTABLISHMENTS = [
    {
        "name": "Subway",
        "category": "Fast Food",
        "location": {
            "latitude": 39.9811,
            "longitude": -75.1540,
            "address": "1838 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "https://picsum.photos/300/200?random=1",
        "is_active": True
    },
    {
        "name": "Chipotle Mexican Grill",
        "category": "Fast Casual",
        "location": {
            "latitude": 39.9805,
            "longitude": -75.1545,
            "address": "1840 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "https://picsum.photos/300/200?random=2",
        "is_active": True
    },
    {
        "name": "Wawa",
        "category": "Convenience Store",
        "location": {
            "latitude": 39.9820,
            "longitude": -75.1535,
            "address": "1835 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "https://picsum.photos/300/200?random=3",
        "is_active": True
    },
    {
        "name": "McDonald's",
        "category": "Fast Food",
        "location": {
            "latitude": 39.9790,
            "longitude": -75.1550,
            "address": "1801 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "https://picsum.photos/300/200?random=4",
        "is_active": True
    },
    {
        "name": "Starbucks",
        "category": "Coffee",
        "location": {
            "latitude": 39.9815,
            "longitude": -75.1525,
            "address": "1900 N 12th St, Philadelphia, PA 19122"
        },
        "image_url": "https://picsum.photos/300/200?random=5",
        "is_active": True
    },
    {
        "name": "Dunkin'",
        "category": "Coffee",
        "location": {
            "latitude": 39.9800,
            "longitude": -75.1560,
            "address": "1700 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "https://picsum.photos/300/200?random=6",
        "is_active": True
    },
    {
        "name": "Halal Guys",
        "category": "Mediterranean",
        "location": {
            "latitude": 39.9825,
            "longitude": -75.1530,
            "address": "1850 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "https://picsum.photos/300/200?random=7",
        "is_active": True
    },
    {
        "name": "Popeyes Louisiana Kitchen",
        "category": "Fast Food",
        "location": {
            "latitude": 39.9785,
            "longitude": -75.1555,
            "address": "1750 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "https://picsum.photos/300/200?random=8",
        "is_active": True
    }
]

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula (in miles)"""
    R = 3959  # Earth's radius in miles
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

@router.get("/", response_model=List[Establishment])
async def get_establishments(
    lat: Optional[float] = None, 
    lon: Optional[float] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all establishments, optionally sorted by distance"""
    db = await get_database()
    
    # Check if establishments exist in database, if not, populate them
    count = await db.establishments.count_documents({})
    if count == 0:
        await db.establishments.insert_many(TEMPLE_ESTABLISHMENTS)
    
    # Get establishments from database
    establishments = []
    async for est in db.establishments.find({"is_active": True}):
        est["_id"] = str(est["_id"])  # Convert ObjectId to string
        establishments.append(Establishment(**est))
    
    # Sort by distance if coordinates provided
    if lat is not None and lon is not None:
        for est in establishments:
            est.distance = calculate_distance(
                lat, lon, 
                est.location.latitude, 
                est.location.longitude
            )
        establishments.sort(key=lambda x: getattr(x, 'distance', 0))
    
    return establishments

@router.get("/search")
async def search_establishments(
    query: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Search establishments by name or category"""
    db = await get_database()
    
    # Search query
    search_filter = {
        "$and": [
            {"is_active": True},
            {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"category": {"$regex": query, "$options": "i"}}
                ]
            }
        ]
    }
    
    establishments = []
    async for est in db.establishments.find(search_filter):
        est["_id"] = str(est["_id"])  # Convert ObjectId to string
        establishments.append(Establishment(**est))
    
    # Sort by distance if coordinates provided
    if lat is not None and lon is not None:
        for est in establishments:
            est.distance = calculate_distance(
                lat, lon,
                est.location.latitude,
                est.location.longitude
            )
        establishments.sort(key=lambda x: getattr(x, 'distance', 0))
    
    return establishments

@router.get("/{establishment_id}", response_model=Establishment)
async def get_establishment(
    establishment_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get specific establishment by ID"""
    from bson import ObjectId
    
    if not ObjectId.is_valid(establishment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid establishment ID format"
        )
    
    db = await get_database()
    establishment = await db.establishments.find_one({"_id": ObjectId(establishment_id)})
    
    if not establishment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Establishment not found"
        )
    
    establishment["_id"] = str(establishment["_id"])  # Convert ObjectId to string
    return Establishment(**establishment)