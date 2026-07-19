const API_BASE = '/api';
let socket = null;
let selectedSeats = [];
let currentEvent = null;
let currentUser = null;
let stripe = null;
let elements = null;
let cardElement = null;
let currentBooking = null;

// Get auth token
function getToken() {
    return localStorage.getItem('token');
}

// Get event ID from URL
function getEventId() {
    const pathParts = window.location.pathname.split('/');
    return pathParts[pathParts.length - 1];
}

// Load event details
async function loadEventDetails() {
    const eventId = getEventId();
    const eventDetails = document.getElementById('event-details');
    
    try {
        const response = await fetch(`${API_BASE}/events/${eventId}`);
        currentEvent = await response.json();
        
        eventDetails.innerHTML = `
            <div class="event-card">
                <div class="event-image">🎭</div>
                <div class="event-details">
                    <h2 class="event-title">${currentEvent.title}</h2>
                    <p class="event-info">${currentEvent.description}</p>
                    <p class="event-info">📍 ${currentEvent.venue}</p>
                    <p class="event-info">📅 ${new Date(currentEvent.date).toLocaleDateString()}</p>
                    <p class="event-price">$${currentEvent.base_price} per seat</p>
                </div>
            </div>
        `;
        
        loadSeats();
    } catch (error) {
        eventDetails.innerHTML = '<div class="error">Failed to load event details</div>';
    }
}

// Load seats
async function loadSeats() {
    const eventId = getEventId();
    const seatSelection = document.getElementById('seat-selection');
    
    try {
        const response = await fetch(`${API_BASE}/seats/event/${eventId}`);
        const seats = await response.json();
        
        // Group seats by row
        const seatsByRow = {};
        seats.forEach(seat => {
            if (!seatsByRow[seat.row]) {
                seatsByRow[seat.row] = [];
            }
            seatsByRow[seat.row].push(seat);
        });
        
        let seatGridHTML = '<div class="seat-grid">';
        
        Object.keys(seatsByRow).sort().forEach(row => {
            seatGridHTML += `<div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">`;
            seatGridHTML += `<span style="width: 30px; font-weight: bold;">${row}</span>`;
            
            seatsByRow[row].sort((a, b) => a.number - b.number).forEach(seat => {
                seatGridHTML += `
                    <div class="seat ${seat.status}" 
                         data-seat-id="${seat.id}" 
                         data-row="${seat.row}" 
                         data-number="${seat.number}"
                         onclick="toggleSeat('${seat.id}', '${seat.status}')">
                        ${seat.number}
                    </div>
                `;
            });
            
            seatGridHTML += `</div>`;
        });
        
        seatGridHTML += '</div>';
        seatGridHTML += `
            <div style="display: flex; gap: 2rem; justify-content: center; margin-top: 1rem;">
                <div><span class="seat available"></span> Available</div>
                <div><span class="seat reserved"></span> Reserved</div>
                <div><span class="seat booked"></span> Booked</div>
                <div><span class="seat selected"></span> Selected</div>
            </div>
        `;
        
        seatSelection.innerHTML = seatGridHTML;
        
        // Initialize Socket.io
        initSocket();
    } catch (error) {
        seatSelection.innerHTML = '<div class="error">Failed to load seats</div>';
    }
}

// Initialize Socket.io
function initSocket() {
    const token = getToken();
    if (!token) {
        return;
    }
    
    socket = io({
        auth: {
            token: token
        }
    });
    
    socket.on('connect', () => {
        console.log('Connected to socket');
        socket.emit('join_event_room', { event_id: getEventId() });
    });
    
    socket.on('seat_updated', (data) => {
        const seatElement = document.querySelector(`[data-seat-id="${data.seat_id}"]`);
        if (seatElement) {
            seatElement.className = `seat ${data.status}`;
            // Remove from selected if it was selected
            if (selectedSeats.includes(data.seat_id)) {
                selectedSeats = selectedSeats.filter(id => id !== data.seat_id);
                updateBookingSummary();
            }
        }
    });
    
    socket.on('error', (data) => {
        alert(data.message);
    });
}

// Toggle seat selection
async function toggleSeat(seatId, status) {
    const token = getToken();
    if (!token) {
        alert('Please login to select seats');
        window.location.href = '/login';
        return;
    }
    
    if (status === 'booked') {
        return;
    }
    
    const seatElement = document.querySelector(`[data-seat-id="${seatId}"]`);
    
    if (selectedSeats.includes(seatId)) {
        // Deselect and release
        selectedSeats = selectedSeats.filter(id => id !== seatId);
        seatElement.classList.remove('selected');
        
        // Release via socket
        socket.emit('release_seat', {
            seat_id: seatId,
            user_id: currentUser?.id,
            event_id: getEventId()
        });
    } else {
        // Select and reserve
        selectedSeats.push(seatId);
        seatElement.classList.add('selected');
        
        // Reserve via socket
        socket.emit('reserve_seat', {
            seat_id: seatId,
            user_id: currentUser?.id,
            event_id: getEventId()
        });
    }
    
    updateBookingSummary();
}

// Update booking summary
function updateBookingSummary() {
    const bookingSummary = document.getElementById('booking-summary');
    
    if (selectedSeats.length === 0) {
        bookingSummary.innerHTML = '';
        document.getElementById('payment-form-container').innerHTML = '';
        return;
    }
    
    const total = selectedSeats.length * currentEvent.base_price;
    
    bookingSummary.innerHTML = `
        <div class="booking-summary">
            <h3>Booking Summary</h3>
            <div class="summary-item">
                <span>Selected Seats</span>
                <span>${selectedSeats.length}</span>
            </div>
            <div class="summary-item">
                <span>Price per seat</span>
                <span>$${currentEvent.base_price}</span>
            </div>
            <div class="summary-item total">
                <span>Total</span>
                <span>$${total.toFixed(2)}</span>
            </div>
            <button onclick="proceedToPayment()" class="btn btn-book">Proceed to Payment</button>
            <button onclick="clearSelection()" class="btn btn-cancel">Clear Selection</button>
        </div>
    `;
}

// Clear selection
function clearSelection() {
    selectedSeats.forEach(seatId => {
        socket.emit('release_seat', {
            seat_id: seatId,
            user_id: currentUser?.id,
            event_id: getEventId()
        });
    });
    selectedSeats = [];
    document.querySelectorAll('.seat.selected').forEach(seat => {
        seat.classList.remove('selected');
    });
    updateBookingSummary();
}

// Proceed to payment
async function proceedToPayment() {
    const token = getToken();
    if (!token) {
        alert('Please login to book');
        window.location.href = '/login';
        return;
    }
    
    // First create the booking
    try {
        const response = await fetch(`${API_BASE}/bookings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                event_id: getEventId(),
                seat_ids: selectedSeats
            })
        });
        
        if (response.ok) {
            currentBooking = await response.json();
            showPaymentForm();
        } else {
            const error = await response.json();
            alert(error.detail || 'Booking failed');
        }
    } catch (error) {
        alert('Booking failed: ' + error.message);
    }
}

// Show payment form
async function showPaymentForm() {
    const paymentContainer = document.getElementById('payment-form-container');
    const total = selectedSeats.length * currentEvent.base_price;
    
    paymentContainer.innerHTML = `
        <div class="booking-summary">
            <h3>Payment</h3>
            <div id="payment-element"></div>
            <button id="submit-payment" class="btn btn-book" onclick="processPayment()">Pay $${total.toFixed(2)}</button>
            <div id="payment-message" class="error" style="display: none;"></div>
        </div>
    `;
    
    // Create payment intent
    const token = getToken();
    try {
        const response = await fetch(`${API_BASE}/payments/create-payment-intent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                amount: total,
                booking_id: currentBooking.id
            })
        });
        
        if (response.ok) {
            const paymentData = await response.json();
            initializeStripe(paymentData.publishable_key, paymentData.client_secret);
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to initialize payment');
        }
    } catch (error) {
        alert('Payment initialization failed: ' + error.message);
    }
}

// Initialize Stripe
function initializeStripe(publishableKey, clientSecret) {
    stripe = Stripe(publishableKey);
    elements = stripe.elements({
        clientSecret: clientSecret
    });
    
    cardElement = elements.create('payment', {
        layout: 'tabs'
    });
    
    cardElement.mount('#payment-element');
}

// Process payment
async function processPayment() {
    const submitButton = document.getElementById('submit-payment');
    const paymentMessage = document.getElementById('payment-message');
    
    submitButton.disabled = true;
    submitButton.textContent = 'Processing...';
    
    try {
        const { error, paymentIntent } = await stripe.confirmPayment({
            elements: elements,
            confirmParams: {
                return_url: window.location.origin + '/my-bookings',
            },
            redirect: 'if_required'
        });
        
        if (error) {
            paymentMessage.textContent = error.message;
            paymentMessage.style.display = 'block';
            submitButton.disabled = false;
            submitButton.textContent = 'Pay $' + (selectedSeats.length * currentEvent.base_price).toFixed(2);
        } else if (paymentIntent.status === 'succeeded') {
            paymentMessage.textContent = 'Payment successful!';
            paymentMessage.className = 'success';
            paymentMessage.style.display = 'block';
            
            setTimeout(() => {
                window.location.href = '/my-bookings';
            }, 2000);
        }
    } catch (error) {
        paymentMessage.textContent = 'Payment failed: ' + error.message;
        paymentMessage.style.display = 'block';
        submitButton.disabled = false;
        submitButton.textContent = 'Pay $' + (selectedSeats.length * currentEvent.base_price).toFixed(2);
    }
}

// Get current user
async function getCurrentUser() {
    const token = getToken();
    if (!token) return null;
    
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            currentUser = await response.json();
        }
    } catch (error) {
        console.error('Failed to get user:', error);
    }
}

// Initialize
getCurrentUser();
loadEventDetails();
updateAuthButtons();
