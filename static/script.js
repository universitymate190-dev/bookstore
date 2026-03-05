// Sidebar Navigation
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const hamburger = document.querySelector('.hamburger-menu');
    
    if (sidebar) {
        sidebar.classList.toggle('active');
        overlay?.classList.toggle('active');
        hamburger?.classList.toggle('active');
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const hamburger = document.querySelector('.hamburger-menu');
    
    if (sidebar) {
        sidebar.classList.remove('active');
        overlay?.classList.remove('active');
        hamburger?.classList.remove('active');
    }
}

// Close sidebar when a link is clicked
document.addEventListener('DOMContentLoaded', function() {
    const sidebarLinks = document.querySelectorAll('.sidebar-links a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', closeSidebar);
    });
    
    // Close sidebar when overlay is clicked
    const overlay = document.getElementById('sidebarOverlay');
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }
});

// Dark Mode Toggle
function toggleDarkMode() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    
    if (isDark) {
        html.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
});

// Form Validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

// Login Form Validation
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        if (!username || !password) {
            alert('Please fill in all fields');
            return;
        }

        if (!validatePassword(password)) {
            alert('Password must be at least 6 characters');
            return;
        }

        this.submit();
    });
}

// Signup Form Validation
const signupForm = document.getElementById('signupForm');
if (signupForm) {
    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;

        if (!username || !email || !password || !confirmPassword) {
            alert('Please fill in all fields');
            return;
        }

        if (username.length < 3) {
            alert('Username must be at least 3 characters');
            return;
        }

        if (!validateEmail(email)) {
            alert('Please enter a valid email');
            return;
        }

        if (!validatePassword(password)) {
            alert('Password must be at least 6 characters');
            return;
        }

        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }

        this.submit();
    });
}

// Upload Form Validation
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const title = document.getElementById('title').value.trim();
        const category = document.getElementById('category').value;
        const file = document.getElementById('file').files[0];

        if (!title || !category || !file) {
            alert('Please fill in all fields and select a file');
            return;
        }

        if (file.size > 50 * 1024 * 1024) { // 50MB limit
            alert('File size must be less than 50MB');
            return;
        }

        this.submit();
    });
}

// Smooth Scroll Navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Format Time Display
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

// Show Loading State
function showLoading(button) {
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span> Loading...';
}

function hideLoading(button, text) {
    button.disabled = false;
    button.innerHTML = text;
}

// Fetch API Helper
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Debounce Function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search Debounced
const debouncedSearch = debounce(searchLibrary, 300);

// Notification System
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 5px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Animation Styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Notification Count Loading
let previousNotificationCount = 0;

function loadNotificationCount() {
    const notificationCount = document.getElementById('notificationCount');
    if (!notificationCount) return;

    fetch('/api/notifications/unread-count')
        .then(response => response.json())
        .then(data => {
            const count = data.unread_count;
            if (count > 0) {
                notificationCount.textContent = count > 99 ? '99+' : count;
                notificationCount.style.display = 'inline-block';
            } else {
                notificationCount.style.display = 'none';
            }
            // if count increased and permission granted, show push notification alert
            if (count > previousNotificationCount && previousNotificationCount !== 0) {
                showPushNotification('You have new notifications', {
                    body: `You have ${count} unread notifications.`
                });
            }
            previousNotificationCount = count;
        })
        .catch(error => {
            console.error('Error loading notification count:', error);
        });
}

// Load notification count on page load for authenticated users
document.addEventListener('DOMContentLoaded', function() {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    
    // Load notification count if user is authenticated
    const notificationCount = document.getElementById('notificationCount');
    if (notificationCount) {
        loadNotificationCount();
        // Refresh notification count every 30 seconds
        setInterval(loadNotificationCount, 30000);
    }
});

// Request push notification permission and register service worker
function registerPushNotifications() {
    if ('serviceWorker' in navigator && 'Notification' in window && 'PushManager' in window) {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(reg => {
                console.log('Service Worker registered:', reg);
                if (Notification.permission === 'default') {
                    Notification.requestPermission().then(permission => {
                        console.log('Notification permission:', permission);
                        if (permission === 'granted') {
                            subscribePushNotifications(reg);
                        }
                    });
                } else if (Notification.permission === 'granted') {
                    subscribePushNotifications(reg);
                }
            })
            .catch(err => console.error('Service Worker registration failed:', err));
    }
}

// Subscribe to push notifications
function subscribePushNotifications(registration) {
    registration.pushManager.getSubscription()
        .then(subscription => {
            if (!subscription) {
                // Create new subscription
                registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array('BElmYW5kRXZlcnlvbmVLbm93c1RoaXNJc0FEaWZmZXJlbnRQdWJLZXlUaGlzSXNSZWFsbHlKdXN0QVBsYWNlaG9sZGVy')
                })
                .then(subscription => {
                    console.log('Push subscription created:', subscription);
                    savePushSubscription(subscription);
                })
                .catch(err => {
                    console.warn('Push subscription failed (this is normal without a push service):', err);
                });
            } else {
                console.log('Already subscribed to push:', subscription);
                savePushSubscription(subscription);
            }
        })
        .catch(err => console.warn('Error getting push subscription:', err));
}

// Save subscription to server
function savePushSubscription(subscription) {
    fetch('/api/subscribe-push', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(subscription)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Push subscription saved:', data);
    })
    .catch(err => console.error('Error saving subscription:', err));
}

// Convert base64 string to Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// call registration on load
document.addEventListener('DOMContentLoaded', function() {
    registerPushNotifications();
});

// function to show a push-style notification
function showPushNotification(title, options) {
    if (Notification.permission === 'granted') {
        navigator.serviceWorker.getRegistration().then(reg => {
            if (reg) {
                reg.showNotification(title, options);
            } else {
                new Notification(title, options);
            }
        });
    }
}

// Export Functions
window.toggleDarkMode = toggleDarkMode;
window.showNotification = showNotification;
window.fetchAPI = fetchAPI;
window.showPushNotification = showPushNotification;

