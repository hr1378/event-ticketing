from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from models import User
from database import get_database
from auth import get_current_active_user
from config import settings
import stripe

router = APIRouter(prefix="/api/payments", tags=["Payments"])


class PaymentIntentRequest(BaseModel):
    amount: float
    booking_id: str


if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/create-payment-intent")
async def create_payment_intent(
    payment_data: PaymentIntentRequest,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_database)
):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Stripe not configured"
        )
    
    # Verify booking exists and belongs to user
    booking = await db.bookings.find_one({"_id": payment_data.booking_id})
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Create payment intent
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(payment_data.amount * 100),  # Convert to cents
            currency='usd',
            metadata={'booking_id': payment_data.booking_id},
            automatic_payment_methods={
                'enabled': True,
            }
        )
        
        # Update booking with payment intent ID
        await db.bookings.update_one(
            {"_id": payment_data.booking_id},
            {"$set": {"payment_intent_id": intent.id}}
        )
        
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db=Depends(get_database)):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Stripe not configured"
        )
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata'].get('booking_id')
        
        if booking_id:
            await db.bookings.update_one(
                {"_id": booking_id},
                {"$set": {"payment_status": "completed"}}
            )
    
    return {"status": "success"}
