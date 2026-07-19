import socketio
from fastapi import FastAPI
from database import get_database

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed.origins='*',
    logger=True,
    engineio_logger=True
)


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('connected', {'sid': sid}, to=sid)


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def join_event_room(sid, data):
    """Join a room for a specific event to receive seat updates"""
    event_id = data.get('event_id')
    if event_id:
        await sio.enter_room(sid, f"event_{event_id}")
        print(f"Client {sid} joined event room: {event_id}")


@sio.event
async def leave_event_room(sid, data):
    """Leave an event room"""
    event_id = data.get('event_id')
    if event_id:
        await sio.leave_room(sid, f"event_{event_id}")
        print(f"Client {sid} left event room: {event_id}")


@sio.event
async def reserve_seat(sid, data):
    """Handle seat reservation via Socket.IO"""
    seat_id = data.get('seat_id')
    user_id = data.get('user_id')
    event_id = data.get('event_id')
    
    db = get_database()
    
    # Check if seat is available
    seat = await db.seats.find_one({"_id": seat_id})
    if not seat:
        await sio.emit('error', {'message': 'Seat not found'}, to=sid)
        return
    
    if seat["status"] != "available":
        await sio.emit('error', {'message': 'Seat not available'}, to=sid)
        return
    
    # Reserve the seat
    from datetime import datetime
    update_data = {
        "status": "reserved",
        "reserved_by": user_id,
        "reserved_at": datetime.utcnow()
    }
    
    await db.seats.update_one(
        {"_id": seat_id},
        {"$set": update_data}
    )
    
    # Broadcast seat update to all clients in the event room
    await sio.emit(
        'seat_updated',
        {
            'seat_id': seat_id,
            'status': 'reserved',
            'row': seat['row'],
            'number': seat['number']
        },
        room=f"event_{event_id}"
    )


@sio.event
async def release_seat(sid, data):
    """Handle seat release via Socket.IO"""
    seat_id = data.get('seat_id')
    user_id = data.get('user_id')
    event_id = data.get('event_id')
    
    db = get_database()
    
    seat = await db.seats.find_one({"_id": seat_id})
    if not seat:
        await sio.emit('error', {'message': 'Seat not found'}, to=sid)
        return
    
    if seat["reserved_by"] != user_id:
        await sio.emit('error', {'message': 'Not authorized'}, to=sid)
        return
    
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
    
    # Broadcast seat update to all clients in the event room
    await sio.emit(
        'seat_updated',
        {
            'seat_id': seat_id,
            'status': 'available',
            'row': seat['row'],
            'number': seat['number']
        },
        room=f"event_{event_id}"
    )


async def broadcast_seat_update(event_id: str, seat_data: dict):
    """Helper function to broadcast seat updates"""
    await sio.emit(
        'seat_updated',
        seat_data,
        room=f"event_{event_id}"
    )
