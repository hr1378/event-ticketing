const API_BASE = '/api';

// Get auth token
function getToken() {
    return localStorage.getItem('token');
}

// Load events
async function loadEvents() {
    const app = document.getElementById('app');
    app.innerHTML = '<div class="loading">Loading events...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/events`);
        const events = await response.json();
        
        if (events.length === 0) {
            app.innerHTML = '<div class="error">No events available. Create an admin account to add events.</div>';
            return;
        }
        
        const eventsGrid = document.createElement('div');
        eventsGrid.className = 'events-grid';
        
        events.forEach(event => {
            const eventCard = document.createElement('div');
            eventCard.className = 'event-card';
            eventCard.innerHTML = `
                <div class="event-image">🎭</div>
                <div class="event-details">
                    <h3 class="event-title">${event.title}</h3>
                    <p class="event-info">📍 ${event.venue}</p>
                    <p class="event-info">📅 ${new Date(event.date).toLocaleDateString()}</p>
                    <p class="event-price">$${event.base_price}</p>
                    <a href="/event/${event.id}" class="btn btn-view btn-primary">View Event</a>
                </div>
            `;
            eventsGrid.appendChild(eventCard);
        });
        
        app.innerHTML = '';
        app.appendChild(eventsGrid);
        
        // Update auth buttons
        updateAuthButtons();
    } catch (error) {
        app.innerHTML = '<div class="error">Failed to load events</div>';
    }
}

// Load page
if (window.location.pathname === '/') {
    loadEvents();
}
