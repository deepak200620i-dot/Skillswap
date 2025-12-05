// Authentication JavaScript

// API Base URL
const API_URL = 'http://localhost:5000/api';

// Signup Form Handler
if (document.getElementById('signup-form')) {
    document.getElementById('signup-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fullName = document.getElementById('full_name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        // Validate passwords match
        if (password !== confirmPassword) {
            showAlert('Passwords do not match', 'danger');
            return;
        }
        
        // Show loading
        setLoading(true);
        
        try {
            const response = await fetch(`${API_URL}/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    full_name: fullName,
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Save token and user data
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Show success and redirect
                showAlert('Account created successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                showAlert(data.error || 'Signup failed', 'danger');
                setLoading(false);
            }
        } catch (error) {
            showAlert('Network error. Please try again.', 'danger');
            setLoading(false);
        }
    });
}

// Login Form Handler
if (document.getElementById('login-form')) {
    document.getElementById('login-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Show loading
        setLoading(true);
        
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Save token and user data
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Show success and redirect
                showAlert('Login successful!', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                showAlert(data.error || 'Login failed', 'danger');
                setLoading(false);
            }
        } catch (error) {
            showAlert('Network error. Please try again.', 'danger');
            setLoading(false);
        }
    });
}

// Helper Functions
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    alertContainer.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

function setLoading(isLoading) {
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const submitBtn = document.querySelector('button[type="submit"]');
    
    if (isLoading) {
        btnText.textContent = 'Please wait...';
        btnSpinner.style.display = 'inline-block';
        submitBtn.disabled = true;
    } else {
        btnText.textContent = document.getElementById('login-form') ? 'Login' : 'Sign Up';
        btnSpinner.style.display = 'none';
        submitBtn.disabled = false;
    }
}

// Check if user is already logged in
function checkLoggedIn() {
    const token = localStorage.getItem('token');
    if (token && (window.location.pathname === '/login' || window.location.pathname === '/signup')) {
        window.location.href = '/dashboard';
    }
}

checkLoggedIn();
