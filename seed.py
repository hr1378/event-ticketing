"""
Seed script to create initial admin user and sample events
Run this after starting MongoDB to populate the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_password_hash
from datetime import datetime, timedelta
from config import settings


async def seed_database():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client.event_ticketing
    
    print("Seeding database...")
    
    # Create admin user
    admin_exists = await db.users.find_one({"email": "admin@eventticket.com"})
    if not admin_exists:
        admin_user = {
            "email": "admin@eventticket.com",
            "username": "admin",
            "hashed_password": get_password_hash("admin123"),
            "role": "admin",
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(admin_user)
        print("✓ Created admin user (admin@eventticket.com / admin123)")
    else:
        print("✓ Admin user already exists")
    
    # Create sample events
    sample_events = [
        {
            "title": "Rock Concert 2024",
            "description": "An amazing night of rock music featuring top bands",
            "venue": "Madison Square Garden",
            "date": datetime.utcnow() + timedelta(days=30),
            "total_seats": 100,
            "rows": 10,
            "seats_per_row": 10,
            "base_price": 75.0,
            "created_by": "admin",
            "created_at": datetime.utcnow()
        },
        {
            "title": "Comedy Night",
            "description": "Laugh your heart out with the best comedians",
            "venue": "Comedy Club Downtown",
            "date": datetime.utcnow() + timedelta(days=15),
            "total_seats": 50,
            "rows": 5,
            "seats_per_row": 10,
            "base_price": 45.0,
            "created_by": "admin",
            "created_at": datetime.utcnow()
        },
        {
            "title": "Tech Conference 2024",
            "description": "Annual technology conference featuring industry leaders",
            "venue": "Convention Center",
            "date": datetime.utcnow() + timedelta(days=45),
            "total_seats": 200,
            "rows": 20,
            "seats_per_row": 10,
            "base_price": 150.0,
            "created_by": "admin",
            "created_at": datetime.utcnow()
        }
    ]
    
    for event_data in sample_events:
        existing = await db.events.find_one({"title": event_data["title"]})
        if not existing:
            result = await db.events.insert_one(event_data)
            event_id = str(result.inserted_id)
            
            # Create seats for the event
            seats = []
            for row_num in range(event_data["rows"]):
                row_letter = chr(65 + row_num)
                for seat_num in range(1, event_data["seats_per_row"] + 1):
                    seat = {
                        "row": row_letter,
                        "number": seat_num,
                        "status": "available",
                        "price": event_data["base_price"],
                        "event_id": event_id
                    }
                    seats.append(seat)
            
            if seats:
                await db.seats.insert_many(seats)
            
            print(f"✓ Created event: {event_data['title']}")
        else:
            print(f"✓ Event already exists: {event_data['title']}")
    
    print("\nDatabase seeding completed!")
    print("Admin credentials: admin@eventticket.com / admin123")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
