from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection
from routers import auth, events, seats, bookings, payments
from socket_server import sio
import socketio.asgi

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

# Create FastAPI app
app = FastAPI(lifespan=lifespan)

# Mount Socket.IO
socket_app = socketio.asgi.ASGIApp(sio, app)

# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(seats.router)
app.include_router(bookings.router)
app.include_router(payments.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/event/{event_id}", response_class=HTMLResponse)
async def event_page(request: Request, event_id: str):
    return templates.TemplateResponse("event.html", {"request": request})


@app.get("/my-bookings", response_class=HTMLResponse)
async def my_bookings(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
