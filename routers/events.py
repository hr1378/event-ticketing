from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models import Event, EventCreate, User
from database import get_database
from auth import get_current_active_user, get_admin_user
from datetime import datetime

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.post("/", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    current_user: User = Depends(get_admin_user),
    db=Depends(get_database)
):
    event_dict = event.dict()
    event_dict["created_by"] = current_user.id
    event_dict["created_at"] = datetime.utcnow()
    
    result = await db.events.insert_one(event_dict)
    event_dict["id"] = str(result.inserted_id)
    
    # Create seats for the event
    seats = []
    for row_num in range(event.rows):
        row_letter = chr(65 + row_num)
        for seat_num in range(1, event.seats_per_row + 1):
            seat = {
                "row": row_letter,
                "number": seat_num,
                "status": "available",
                "price": event.base_price,
                "event_id": str(result.inserted_id)
            }
            seats.append(seat)
    
    if seats:
        await db.seats.insert_many(seats)
    
    return Event(**event_dict)


@router.get("/", response_model=List[Event])
async def get_events(db=Depends(get_database)):
    events = await db.events.find().to_list(length=100)
    for event in events:
        event["id"] = str(event["_id"])
    return events


@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: str, db=Depends(get_database)):
    event = await db.events.find_one({"_id": event_id})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    event["id"] = str(event["_id"])
    return Event(**event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_admin_user),
    db=Depends(get_database)
):
    event = await db.events.find_one({"_id": event_id})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    await db.events.delete_one({"_id": event_id})
    await db.seats.delete_many({"event_id": event_id})
    await db.bookings.delete_many({"event_id": event_id})
