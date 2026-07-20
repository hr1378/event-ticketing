# Event Ticketing Platform - Python Version

A full-stack event ticketing platform built with Python, featuring real-time seat synchronization, JWT authentication, and Stripe payment integration.

## Tech Stack

- **Backend**: FastAPI (Python web framework)
- **Database**: MongoDB (with Motor for async operations)
- **Authentication**: JWT (JSON Web Tokens) with role-based access
- **Real-time**: Socket.io for seat synchronization
- **Payments**: Stripe integration
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## Features

- **User Authentication**: Register, login, and role-based access control (Admin/User)
- **Event Management**: Create, view, and delete events (Admin only)
- **Seat Selection**: Interactive seat grid with real-time availability
- **Real-time Sync**: Socket.io ensures no double-booking during concurrent purchases
- **Booking System**: Reserve seats and complete bookings
- **Payment Integration**: Stripe payment processing
- **Responsive Design**: Mobile-friendly UI

## Project Structure

```
event_ticketing/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration settings
├── database.py             # MongoDB connection management
├── auth.py                 # JWT authentication utilities
├── socket_server.py        # Socket.io server for real-time updates
├── models.py               # Pydantic models
├── routers/
│   ├── auth.py            # Authentication endpoints
│   ├── events.py          # Event management endpoints
│   ├── seats.py           # Seat management endpoints
│   ├── bookings.py        # Booking endpoints
│   └── payments.py        # Stripe payment endpoints
├── templates/
│   ├── index.html         # Home page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   └── event.html         # Event details page
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       ├── app.js         # Main JavaScript
│       ├── auth.js        # Authentication logic
│       └── event.js       # Event page logic
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Installation

1. **Clone the repository**
   ```bash
   cd /Users/hatim/Desktop/Desktop/Event_ticketing
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start MongoDB**
   ```bash
   # Make sure MongoDB is running on localhost:27017
   # Or update MONGODB_URI in .env
   ```

## Running the Application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Events
- `POST /api/events/` - Create event (Admin only)
- `GET /api/events/` - List all events
- `GET /api/events/{event_id}` - Get event details
- `DELETE /api/events/{event_id}` - Delete event (Admin only)

### Seats
- `GET /api/seats/event/{event_id}` - Get seats for an event
- `POST /api/seats/{seat_id}/reserve` - Reserve a seat
- `POST /api/seats/{seat_id}/release` - Release a reserved seat
- `POST /api/seats/cleanup-expired` - Cleanup expired reservations

### Bookings
- `POST /api/bookings/` - Create a booking
- `GET /api/bookings/` - Get user's bookings
- `GET /api/bookings/{booking_id}` - Get booking details

### Payments
- `POST /api/payments/create-payment-intent` - Create Stripe payment intent
- `POST /api/payments/webhook` - Stripe webhook handler

## Usage

### Creating an Admin User

1. Register a user via the UI or API
2. Manually update the user's role in MongoDB to "admin"
3. Use the admin account to create events

### Creating Events

1. Login as admin
2. Use the API endpoint or add event creation UI
3. Events will automatically generate seats based on rows and seats per row

### Booking Tickets

1. Browse events on the home page
2. Click "View Event" on an event
3. Select available seats (green)
4. Click "Book Now" to complete the booking

## Real-time Seat Synchronization

The platform uses Socket.io to ensure seat availability is synchronized across all clients in real-time:

- When a user selects a seat, it's immediately reserved via Socket.io
- All connected clients receive instant updates
- Expired reservations (10 minutes) are automatically released
- This prevents double-booking during concurrent purchases

## Configuration

Edit `.env` file with your settings:

```env
MONGODB_URI=mongodb://localhost:27017/event_ticketing
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
FRONTEND_URL=http://localhost:8000
```

## Development Notes

This is a resume-quality project, not production-ready. For production use, consider:

- Adding proper error handling and logging
- Implementing rate limiting
- Adding input validation and sanitization
- Using HTTPS
- Implementing proper session management
- Adding comprehensive tests
- Using a production-grade WSGI server
- Implementing proper CORS configuration
- Adding database migrations
- Implementing proper email verification
- Adding password reset functionality

## License

This project is for educational purposes.
# event-ticketing
# event-ticketing
