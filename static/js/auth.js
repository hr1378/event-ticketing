const API_BASE = '/api/auth';

// Check if user is logged in
async function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        try {
            const response = await fetch(`${API_BASE}/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const user = await response.json();
                return user;
            }
        } catch (error) {
            console.error('Auth check failed:', error);
        }
    }
    return null;
}

// Update auth buttons
async function updateAuthButtons() {
    const user = await checkAuth();
    const authButtons = document.getElementById('auth-buttons');
    
    if (user) {
        authButtons.innerHTML = `
            <span>Welcome, ${user.username}</span>
            <button onclick="logout()" class="btn btn-primary" style="width: auto; padding: 0.5rem 1rem;">Logout</button>
        `;
    } else {
        authButtons.innerHTML = `
            <a href="/login" class="btn btn-primary" style="text-decoration: none; color: white; padding: 0.5rem 1rem;">Login</a>
            <a href="/register" class="btn btn-primary" style="text-decoration: none; color: white; padding: 0.5rem 1rem; margin-left: 0.5rem;">Register</a>
        `;
    }
}

// Login
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            window.location.href = '/';
        } else {
            const error = await response.json();
            alert(error.detail || 'Login failed');
        }
    } catch (error) {
        alert('Login failed: ' + error.message);
    }
});

// Register
document.getElementById('register-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, username, password })
        });
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            window.location.href = '/login';
        } else {
            const error = await response.json();
            alert(error.detail || 'Registration failed');
        }
    } catch (error) {
        alert('Registration failed: ' + error.message);
    }
});

// Logout
function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

// Initialize auth buttons on page load
if (document.getElementById('auth-buttons')) {
    updateAuthButtons();
}
