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
        "name": "Honey Truck",
        "category": "Food Truck",
        "location": {
            "latitude": 39.9805,
            "longitude": -75.1545,
            "address": "12 th &, W Norris St, Philadelphia, PA 19122"
        },
        "image_url": "http://localhost:3000/images/honeytruck.jpeg",
        "is_active": True,
        "menu_items": [
            {"name": "Avocado Wrap", "price": 10.51, "category": "Sandwiches"},
            {"name": "Curry Bowl", "price": 9.99, "category": "Bowls"},
            {"name": "Chicken Sandwich", "price": 8.99, "category": "Sandwiches"},
        ]
    },
    {
        "name": "Temple Teppanyaki",
        "category": "Japanese and Korean",
        "location": {
            "latitude": 39.9805,
            "longitude": -75.1545,
            "address": "1840 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "http://localhost:3000/images/templeteppanyaki.jpeg",
        "is_active": True,
        "menu_items": [
            {"name": "Chicken Teppanyaki", "price": 10.00, "category": "Plates"},
            {"name": "Chicken Rice Bowl", "price": 9.50, "category": "Bowls"},
            {"name": "Shrimp Teppanyaki", "price": 10.00, "category": "Plates"},
            {"name": "Veggie Teppanyaki", "price": 10.00, "category": "Plates"},
            {"name": "Beef Rice Bowl", "price": 9.50, "category": "Bowls"},
            {"name": "Fried Shrimp", "price": 10.00, "category": "Sides"}
        ]
    },
    {
        "name": "7-Eleven",
        "category": "Convenience Store",
        "location": {
            "latitude": 39.9820,
            "longitude": -75.1535,
            "address": "1835 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "http://localhost:3000/images/7-eleven 2.jpeg",
        "is_active": True,
        "menu_items": [
            {"name": "Classic Hoagie", "price": 8.99, "category": "Hoagies"},
            {"name": "Buffalo Chicken Mac & Cheese Bowl", "price": 7.49, "category": "Hot Foods"},
            {"name": "Chicken Caesar Salad", "price": 8.99, "category": "Salads"},
            {"name": "Coffee (Medium)", "price": 1.89, "category": "Beverages"},
            {"name": "Soft Pretzel", "price": 1.29, "category": "Snacks"},
            {"name": "Energy Drink", "price": 3.49, "category": "Beverages"}
        ]
    },
    {
        "name": "McDonald's",
        "category": "Fast Food",
        "location": {
            "latitude": 39.9790,
            "longitude": -75.1550,
            "address": "1801 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "http://localhost:3000/images/mcdonalds.jpg",
        "is_active": True,
        "menu_items": [
            {"name": "Big Mac", "price": 6.49, "category": "Burgers"},
            {"name": "Quarter Pounder with Cheese", "price": 7.79, "category": "Burgers"},
            {"name": "10 Piece McNuggets", "price": 5.99, "category": "Chicken"},
            {"name": "Large Fries", "price": 3.79, "category": "Sides"},
            {"name": "McFlurry", "price": 4.39, "category": "Desserts"},
            {"name": "Medium Coke", "price": 1.00, "category": "Beverages"}
        ]
    },
    {
        "name": "Starbucks",
        "category": "Coffee",
        "location": {
            "latitude": 39.9815,
            "longitude": -75.1525,
            "address": "1900 N 12th St, Philadelphia, PA 19122"
        },
        "image_url": "http://localhost:3000/images/starbucks.jpeg",
        "is_active": True,
        "menu_items": [
            {"name": "Grande Pike Place Roast", "price": 2.85, "category": "Hot Coffee"},
            {"name": "Venti Iced Caramel Macchiato", "price": 5.95, "category": "Cold Coffee"},
            {"name": "Grande Chai Tea Latte", "price": 4.95, "category": "Tea"},
            {"name": "Bacon, Gouda & Egg Sandwich", "price": 5.45, "category": "Food"},
            {"name": "Blueberry Muffin", "price": 3.25, "category": "Pastries"},
            {"name": "Cake Pop", "price": 2.25, "category": "Treats"}
        ]
    },
    {
        "name": "Dunkin'",
        "category": "Coffee",
        "location": {
            "latitude": 39.9800,
            "longitude": -75.1560,
            "address": "1700 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "http://localhost:3000/images/dunkin.jpg",
        "is_active": True,
        "menu_items": [
            {"name": "Medium Original Blend Coffee", "price": 2.29, "category": "Hot Coffee"},
            {"name": "Large Iced Caramel Latte", "price": 4.59, "category": "Cold Coffee"},
            {"name": "Boston Kreme Donut", "price": 1.59, "category": "Donuts"},
            {"name": "Everything Bagel with Cream Cheese", "price": 3.49, "category": "Bagels"},
            {"name": "Sausage, Egg & Cheese on Croissant", "price": 5.29, "category": "Breakfast"},
            {"name": "Hash Browns", "price": 2.49, "category": "Sides"}
        ]
    },
    {
        "name": "Halal Guys",
        "category": "Mediterranean",
        "location": {
            "latitude": 39.9825,
            "longitude": -75.1530,
            "address": "1850 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "http://localhost:3000/images/halalguys.jpeg",
        "is_active": True,
        "menu_items": [
            {"name": "Chicken & Rice Platter", "price": 9.99, "category": "Platters"},
            {"name": "Lamb & Rice Platter", "price": 11.99, "category": "Platters"},
            {"name": "Mixed Platter (Chicken & Lamb)", "price": 12.99, "category": "Platters"},
            {"name": "Chicken Gyro", "price": 7.99, "category": "Gyros"},
            {"name": "Falafel Platter", "price": 8.99, "category": "Vegetarian"},
            {"name": "Baklava", "price": 3.99, "category": "Desserts"}
        ]
    },
    {
        "name": "Popeyes Louisiana Kitchen",
        "category": "Fast Food",
        "location": {
            "latitude": 39.9785,
            "longitude": -75.1555,
            "address": "1750 N Broad St, Philadelphia, PA 19122"
        },
        "image_url": "http://localhost:3000/images/popeyes.jpg",
        "is_active": True,
        "menu_items": [
            {"name": "3 Piece Chicken Tenders", "price": 8.99, "category": "Chicken"},
            {"name": "Spicy Chicken Sandwich", "price": 6.99, "category": "Sandwiches"},
            {"name": "8 Piece Family Meal", "price": 19.99, "category": "Family Meals"},
            {"name": "Large Red Beans & Rice", "price": 4.49, "category": "Sides"},
            {"name": "Biscuit", "price": 1.79, "category": "Sides"},
            {"name": "Sweet Tea (Large)", "price": 2.49, "category": "Beverages"}
        ]
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
    
    # Force refresh establishments to match current template
    # Clear all existing establishments and insert fresh ones
    await db.establishments.delete_many({})
    await db.establishments.insert_many(TEMPLE_ESTABLISHMENTS)
    print(f"DEBUG: Refreshed {len(TEMPLE_ESTABLISHMENTS)} establishments in database")
    
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

@router.get("/{establishment_id}/menu")
async def get_establishment_menu(
    establishment_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get menu items for a specific establishment"""
    from bson import ObjectId
    
    if not ObjectId.is_valid(establishment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid establishment ID format"
        )
    
    db = await get_database()
    establishment = await db.establishments.find_one({"_id": ObjectId(establishment_id)})
    
    print(f"DEBUG: Looking for establishment ID: {establishment_id}")
    print(f"DEBUG: Found establishment: {establishment is not None}")
    
    if not establishment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Establishment not found"
        )
    
    menu_items = establishment.get("menu_items", [])
    print(f"DEBUG: Menu items count: {len(menu_items)}")
    
    # Return menu items if they exist, otherwise empty list
    return menu_items