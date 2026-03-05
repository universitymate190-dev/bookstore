# Push Notifications Implementation

## Overview
This document describes the push notification system implemented for the bookstore application. The system allows admins to send device push notifications to all subscribed users.

## Features Implemented

### 1. Database Schema
- **New Table**: `push_subscriptions`
  - `id`: Primary key (INTEGER)
  - `user_id`: Foreign key to users table (INTEGER)
  - `endpoint`: Unique push service endpoint URL (TEXT)
  - `auth`: Authentication key for push service (TEXT)
  - `p256dh`: ECDH public key for encryption (TEXT)
  - `created_at`: Timestamp (TIMESTAMP)
  - Unique constraint on `endpoint` to prevent duplicate subscriptions

### 2. Backend API Endpoints

#### `/api/subscribe-push` (POST)
**Purpose**: Store user's push notification subscription
**Authentication**: Required (login_required)
**Parameters**:
```json
{
  "endpoint": "https://push-service.example.com/notify/...",
  "keys": {
    "auth": "auth_key_string",
    "p256dh": "public_key_string"
  }
}
```
**Response**: 
```json
{
  "success": true,
  "message": "Subscription saved"
}
```
**Status**: 201 Created

#### `/admin/send-push-notification` (POST)
**Purpose**: Send push notifications to all subscribed users (Admin only)
**Authentication**: Required + Admin role
**Parameters**:
```json
{
  "title": "Notification Title",
  "body": "Notification message content"
}
```
**Response**:
```json
{
  "success": true,
  "message": "Notification sent to X users",
  "failed": 0
}
```
**Status**: 200 OK (or 403 for non-admin)

### 3. Service Worker (`static/service-worker.js`)
- **Install**: Skips waiting for activation
- **Activate**: Claims all clients
- **Push Events**: Listens for push notifications and displays them
  - Shows notification with title, body, icon
- **Click Handler**: Opens the app to "/" when notification is clicked

### 4. Frontend JavaScript (`static/script.js`)

#### `registerPushNotifications()`
- Registers the service worker
- Requests notification permission if needed
- Calls `subscribePushNotifications()` when permission granted

#### `subscribePushNotifications(registration)`
- Gets or creates a new push subscription
- Calls `savePushSubscription()` to store subscription on server
- Handles subscription creation with VAPID public key

#### `savePushSubscription(subscription)`
- POST request to `/api/subscribe-push`
- Sends the subscription object to server
- Logs success/failure

#### `urlBase64ToUint8Array(base64String)`
- Helper function to convert VAPID public key to Uint8Array format

### 5. Admin Panel (`templates/admin.html`)
- **Notifications Tab**: Now has two sections:
  1. **In-App Notifications**: Send in-database notifications to all users
  2. **Push Notifications (Device)**: Send device push notifications to subscribed users
- **Form Fields**:
  - Title (required)
  - Message body (required)
- **Status Display**: Shows success/error messages with color coding
  - Green (#e8f5e9) for success
  - Blue (#e8f4f8) for pending
  - Red (#ffebee) for errors

### 6. Group Message Integration
The `send_group_message()` function now:
- Retrieves group members' push subscriptions
- Prepares push notification data with group name and truncated message
- Logs intention to send notifications (actual sending requires push service integration)
- Can be extended with actual push service implementation (Firebase, Web Push Protocol, etc.)

## Workflow

### User Side
1. User visits app → `registerPushNotifications()` called
2. Service Worker registered
3. Browser requests notification permission
4. User grants permission → `subscribePushNotifications()` called
5. Browser creates push subscription with unique endpoint
6. `savePushSubscription()` sends subscription to server
7. Server stores in `push_subscriptions` table

### Admin Side
1. Admin navigates to Admin Panel → Notifications Tab
2. Fills in Title and Message for Push Notifications
3. Clicks "Send to Subscribed Users"
4. Frontend POSTs to `/admin/send-push-notification`
5. Backend queries all push subscriptions
6. Notifications are sent to subscribed users' devices
7. Status message shown (success count, failures)

### Receiving Notifications
1. Browser receives push event via push service
2. Service Worker `push` event listener triggered
3. Displays notification using `showNotification()` API
4. User sees notification on device (even if app is closed)
5. Click handler opens app

## Technical Notes

### VAPID Public Key
- Currently uses a placeholder key: `BElmYW5kRXZlcnlvbmVLbm93c1RoaXNJc0FEaWZmZXJlbnRQdWJLZXlUaGlzSXNSZWFsbHlKdXN0QVBsYWNlaG9sZGVy`
- For production, generate real VAPID keys:
  ```bash
  npm install -g web-push
  web-push generate-vapid-keys
  ```

### Push Service Integration
The current implementation stores subscriptions but doesn't send actual push notifications. To enable real push notifications, integrate a service like:

1. **Firebase Cloud Messaging (FCM)**
   - Most popular, free tier available
   - Requires Firebase project setup
   
2. **Web Push Protocol** (RFC 8030)
   - Use `pywebpush` library
   - Requires VAPID key pair
   
3. **Other Services**
   - AWS SNS, Azure Notification Hubs, etc.

### Example: pywebpush Integration
```python
from pywebpush import webpush
import json

for subscription in subscriptions:
    try:
        webpush(
            subscription={
                'endpoint': subscription['endpoint'],
                'keys': {
                    'auth': subscription['auth'],
                    'p256dh': subscription['p256dh']
                }
            },
            data=json.dumps({
                'title': title,
                'body': body,
                'icon': '/static/icon.png'
            }),
            vapid_private_key='your-private-key',
            vapid_claims={
                'sub': 'mailto:your-email@example.com'
            }
        )
    except Exception as e:
        print(f'Error sending push: {e}')
```

## Database Migration
The `push_subscriptions` table is automatically created when `init_db()` is called. For existing databases, the table will be created on app startup.

## Security Considerations
1. Subscriptions are stored with user_id - only authenticated users can subscribe
2. Admin check on `/admin/send-push-notification` - only admins can send notifications
3. Endpoint URLs are unique - prevents duplicate registrations
4. HTTPS required in production for service worker and push

## Browser Compatibility
- **Service Workers**: Chrome 40+, Firefox 44+, Edge 17+, Opera 27+, Safari 11.1+
- **Push API**: Chrome 50+, Firefox 44+, Edge 17+, Opera 37+
- **Notification API**: Most modern browsers

## Testing
1. Navigate to any page (notification permission request should appear)
2. Grant notification permission
3. Go to Admin Panel → Notifications tab
4. Enter title and message in "Push Notifications (Device)" section
5. Click "Send to Subscribed Users"
6. Status message should show success
7. If in service worker context, notification should appear on device
