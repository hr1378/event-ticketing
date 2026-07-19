from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models import Seat, User
from database import get_database
from auth import get_current_active_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/seats", tags=["Seats"])


@router.get("/event/{event_id}", response_model=List[Seat])
async def get_event_seats(event_id: str, db=Depends(get_database)):
    seats = await db.seats.find({"event_id": event_id}).to_list(length=1000)
    for seat in seats:
        seat["id"] = str(seat["_id"])
    return seats


@router.post("/{seat_id}/reserve", response_model=Seat)
async def reserve_seat(
    seat_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_database)
):
    # Check if seat exists and is available
    seat = await db.seats.find_one({"_id": seat_id})
    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found"
        )
    
    if seat["status"] != "available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seat is not available"
        )
    
    # Reserve the seat
    update_data = {
        "status": "reserved",
        "reserved_by": current_user.id,
        "reserved_at": datetime.utcnow()
    }
    
    await db.seats.update_one(
        {"_id": seat_id},
        {"$set": update_data}
    )
    
    updated_seat = await db.seats.find_one({"_id": seat_id})
    updated_seat["id"] = str(updated_seat["_id"])
    
    return Seat(**updated_seat)


@router.post("/{seat_id}/release", response_model=Seat)
async def release_seat(
    seat_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_database)
):
    seat = await db.seats.find_one({"_id": seat_id})
    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found"
        )
    
    # Only the user who reserved can release
    if seat["reserved_by"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only release seats you reserved"
        )
    
    if seat["status"] != "reserved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seat is not reserved"
        )
    
    # Release the seat
    update_data = {
        "status": "available",
        "reserved_by": None,
        "reserved_at": None
    }
    
    await db.seats.update_one(
        {"_id": seat_id},
        {"$set": update_data}
    )
    
    updated_seat = await db.seats.find_one({"_id": seat_id})
    updated_seat["id"] = str(updated_seat["_id"])
    
    return Seat(**updated_seat)


@router.post("/cleanup-expired")
async def cleanup_expired_reservations(db=Depends(get_database)):
    # Release reservations older than 10 minutes
    expiry_time = datetime.utcnow() - timedelta(minutes=10)
    
    result = await db.seats.update_many(
        {
            "status": "reserved",
            "reserved_at": {"$lt": expiry_time}
        },
        {
            "$set": {
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            }
        }
    )
    
    return {"released_count": result.modified_count}
