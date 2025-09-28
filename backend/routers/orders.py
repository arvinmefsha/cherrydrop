from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List, Optional
from models.schemas import Order, OrderCreate, OrderUpdate, OrderStatus, UserResponse
from utils.auth import get_current_user
from utils.database import get_database
from bson import ObjectId
import base64
from io import BytesIO

router = APIRouter()

@router.post("/", response_model=Order)
async def create_order(
    order_data: OrderCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new delivery order"""
    db = await get_database()
    
    # Check if user has enough points
    if current_user.points < order_data.delivery_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points for this delivery"
        )
    
    # Verify establishment exists
    if not ObjectId.is_valid(order_data.establishment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid establishment ID format"
        )
    
    establishment = await db.establishments.find_one({"_id": ObjectId(order_data.establishment_id)})
    if not establishment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Establishment not found"
        )
    
    # Create order
    order_dict = {
        "customer_id": str(current_user.id),
        "establishment_id": order_data.establishment_id,
        "items": [item.dict() for item in order_data.items],
        "delivery_location": order_data.delivery_location.dict(),
        "special_instructions": order_data.special_instructions,
        "delivery_points": order_data.delivery_points,
        "status": OrderStatus.PENDING
    }
    
    result = await db.orders.insert_one(order_dict)
    order_dict["id"] = str(result.inserted_id)  # Convert ObjectId to string and rename to id
    if "_id" in order_dict:
        del order_dict["_id"]  # Remove the _id field
    
    return Order(**order_dict)

@router.get("/my-orders", response_model=List[Order])
async def get_my_orders(
    status_filter: Optional[OrderStatus] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user's orders"""
    db = await get_database()
    
    filter_query = {"customer_id": str(current_user.id)}
    if status_filter:
        filter_query["status"] = status_filter
    
    orders = []
    async for order in db.orders.find(filter_query).sort("created_at", -1):
        order["id"] = str(order["_id"])  # Convert ObjectId to string and rename to id
        del order["_id"]  # Remove the _id field
        print(f"DEBUG: My order after conversion: {order.get('id')}")
        orders.append(Order(**order))
    
    return orders

@router.get("/available", response_model=List[Order])
async def get_available_orders(current_user: UserResponse = Depends(get_current_user)):
    """Get available orders for delivery (excluding user's own orders)"""
    db = await get_database()
    
    orders = []
    async for order in db.orders.find({
        "status": OrderStatus.PENDING,
        "customer_id": {"$ne": str(current_user.id)}
    }).sort("created_at", 1):
        order["id"] = str(order["_id"])  # Convert ObjectId to string and rename to id
        del order["_id"]  # Remove the _id field
        orders.append(Order(**order))
    
    return orders

@router.get("/delivering", response_model=List[Order])
async def get_delivering_orders(current_user: UserResponse = Depends(get_current_user)):
    """Get orders currently being delivered by the user"""
    db = await get_database()
    
    orders = []
    async for order in db.orders.find({
        "deliverer_id": str(current_user.id),
        "status": {"$in": [OrderStatus.ACCEPTED, OrderStatus.PICKED_UP]}
    }).sort("accepted_at", 1):
        order["id"] = str(order["_id"])  # Convert ObjectId to string and rename to id
        del order["_id"]  # Remove the _id field
        orders.append(Order(**order))
    
    return orders

@router.put("/{order_id}/accept")
async def accept_order(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Accept an order for delivery"""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    db = await get_database()
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order["status"] != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is not available for acceptance"
        )
    
    if order["customer_id"] == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot accept your own order"
        )
    
    # Update order
    from datetime import datetime
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "deliverer_id": str(current_user.id),
                "status": OrderStatus.ACCEPTED,
                "accepted_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Order accepted successfully"}

@router.put("/{order_id}/update-status")
async def update_order_status(
    order_id: str,
    status_update: OrderUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update order status (for deliverer)"""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    db = await get_database()
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order["deliverer_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this order"
        )
    
    update_data = {"status": status_update.status}
    
    if status_update.status == OrderStatus.DELIVERED:
        update_data["completion_image_url"] = status_update.completion_image_url
    
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": update_data}
    )
    
    return {"message": "Order status updated successfully"}

@router.put("/{order_id}/complete")
async def complete_order(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Complete an order (customer confirms receipt)"""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    db = await get_database()
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order["customer_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this order"
        )
    
    if order["status"] != OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be delivered before completion"
        )
    
    # Transfer points
    customer_id = ObjectId(order["customer_id"])
    deliverer_id = ObjectId(order["deliverer_id"])
    points = order["delivery_points"]
    
    # Deduct points from customer
    await db.users.update_one(
        {"_id": customer_id},
        {"$inc": {"points": -points}}
    )
    
    # Add points to deliverer
    await db.users.update_one(
        {"_id": deliverer_id},
        {"$inc": {"points": points}}
    )
    
    # Mark order as completed
    from datetime import datetime
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "status": OrderStatus.COMPLETED,
                "completed_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Order completed successfully, points transferred"}

@router.post("/{order_id}/upload-image")
async def upload_completion_image(
    order_id: str,
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload completion image for an order"""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    # Check file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    db = await get_database()
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order["deliverer_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload image for this order"
        )
    
    # Convert image to base64 for simple storage
    image_data = await file.read()
    image_base64 = base64.b64encode(image_data).decode()
    image_url = f"data:{file.content_type};base64,{image_base64}"
    
    # Update order with image and status
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "completion_image_url": image_url,
                "status": OrderStatus.DELIVERED
            }
        }
    )
    
    return {"message": "Image uploaded successfully", "image_url": image_url}

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get specific order details"""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    db = await get_database()
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user is authorized to view this order
    if (order["customer_id"] != str(current_user.id) and 
        order.get("deliverer_id") != str(current_user.id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return Order(**order)