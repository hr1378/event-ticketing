from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models import Booking, BookingCreate, User
from database import get_database
from auth import get_current_active_user
from datetime import datetime

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("/", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_database)
):
    # Verify all seats exist and are reserved by current user
    seats = []
    total_amount = 0
    
    for seat_id in booking.seat_ids:
        seat = await db.seats.find_one({"_id": seat_id})
        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Seat {seat_id} not found"
            )
        
        if seat["status"] != "reserved" or seat["reserved_by"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Seat {seat_id} is not reserved by you"
            )
        
        seats.append(seat)
        total_amount += seat["price"]
    
    # Create booking
    booking_dict = {
        "user_id": current_user.id,
        "event_id": booking.event_id,
        "seat_ids": booking.seat_ids,
        "total_amount": total_amount,
        "payment_status": "pending"
    }
    
    result = await db.bookings.insert_one(booking_dict)
    booking_dict["id"] = str(result.inserted_id)
    
    # Mark seats as booked
    await db.seats.update_many(
        {"_id": {"$in": booking.seat_ids}},
        {"$set": {"status": "booked"}}
    )
    
    return Booking(**booking_dict)


@router.get("/", response_model=List[Booking])
async def get_user_bookings(
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_database)
):
    bookings = await db.bookings.find({"user_id": current_user.id}).to_list(length=100)
    for booking in bookings:
        booking["id"] = str(booking["_id"])
    return bookings


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_database)
):
    booking = await db.bookings.find_one({"_id": booking_id})
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking"
        )
    
    booking["id"] = str(booking["_id"])
    return Booking(**booking)
