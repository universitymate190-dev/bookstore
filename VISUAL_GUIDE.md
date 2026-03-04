# 🎓 BOOKSTORE WEBSITE - VISUAL GUIDE

## 🏠 Application Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    BOOKSTORE WEBSITE                         │
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────┐ │
│  │ HOMEPAGE     │      │   LIBRARY    │      │   EXAMS    │ │
│  │              │      │              │      │            │ │
│  │ - Features   │──────│ - Search     │──────│ - List     │ │
│  │ - Call-to-   │      │ - Filter     │      │ - Timer    │ │
│  │   action     │      │ - Download   │      │ - Grade    │ │
│  └──────────────┘      └──────────────┘      └────────────┘ │
│         ▲                                           ▲          │
│         └───────────────┬───────────────────────────┘          │
│                         │                                      │
│                    ┌────────────┐                              │
│                    │ NAVBAR     │                              │
│                    │            │                              │
│                    │ Home       │                              │
│                    │ Library    │                              │
│                    │ Exams      │                              │
│                    │ Login/Out  │                              │
│                    └────────────┘                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 👤 User Journey

### Unregistered User
```
Home → Sign Up → Create Account → Login → Dashboard
```

### Registered User
```
Login → Dashboard → Explore Library → Upload Files → Take Exam → View Results
```

### Admin User
```
Login → Dashboard → Admin Panel → Manage Everything
```

## 📊 Database Relationships

```
                    ┌─────────────┐
                    │ Users       │
                    │             │
                    │ - id (PK)   │
                    │ - username  │
                    │ - email     │
                    │ - password  │
                    │ - role      │
                    └─────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Files    │  │ Exams    │  │ Results  │
    │          │  │          │  │          │
    │ uploaded │  │ created  │  │ taken by │
    │ by→user  │  │ by→user  │  │ user→id  │
    └──────────┘  └──────────┘  └──────────┘
                        │
                        ▼
                  ┌──────────────┐
                  │ Questions    │
                  │              │
                  │ belong to    │
                  │ exam→id      │
                  └──────────────┘
```

## 🎨 UI Component Hierarchy

```
┌─ DOCUMENT ROOT
│
├─ NAVBAR (sticky)
│  ├─ Logo
│  ├─ Navigation Links
│  │  ├─ Home
│  │  ├─ Library
│  │  ├─ Exams
│  │  └─ Auth (Login/Logout)
│  └─ Theme Toggle
│
├─ MAIN CONTENT
│  ├─ Page-specific Content
│  │  ├─ Forms
│  │  │  ├─ Input Fields
│  │  │  ├─ Labels
│  │  │  └─ Submit Button
│  │  │
│  │  ├─ Grids
│  │  │  ├─ Cards
│  │  │  │  ├─ Title
│  │  │  │  ├─ Description
│  │  │  │  └─ CTA Button
│  │  │  └─ Responsive Layout
│  │  │
│  │  └─ Tables (Admin)
│  │     ├─ Headers
│  │     ├─ Rows
│  │     └─ Actions
│  │
│  └─ Flash Messages
│     ├─ Success
│     ├─ Error
│     └─ Info
│
└─ FOOTER
   ├─ Copyright
   └─ Links
```

## 🔄 Authentication Flow

```
┌─────────────┐
│ Unauthent.  │
└──────┬──────┘
       │
       ├─ Click "Sign Up"
       │
       ▼
┌──────────────────┐
│ Signup Form      │
│ - Username       │
│ - Email          │
│ - Password       │
│ - Confirm Pass   │
└────────┬─────────┘
         │
         ├─ Validate Input
         ├─ Hash Password
         ├─ Save to DB
         │
         ▼
    ┌────────────┐
    │ Redirect   │
    │ to Login   │
    └────────────┘
         │
         │
       ┌─┴─────────────────┐
       │                   │
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ Login Form   │    │ Account      │
│             │    │ Created ✓     │
│ - Username  │    │             │
│ - Password  │    └──────────────┘
└────────┬────┘
         │
         ├─ Verify Credentials
         ├─ Hash & Compare
         ├─ Create Session
         │
         ▼
    ┌────────────┐
    │ Logged In  │
    │ ✓          │
    └────────────┘
         │
         ▼
   ┌──────────────┐
   │ Access All  │
   │ Features    │
   └──────────────┘
```

## 📝 Exam Taking Flow

```
┌───────────────┐
│ Exam List     │
│ /exams        │
└────────┬──────┘
         │
         ├─ Select Exam
         │
         ▼
┌──────────────────────┐
│ Exam Page            │
│ /exam/<id>           │
│                      │
│ Title & Time Display │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────┐
│ Questions Display        │
│ with Options & Timer     │
│                          │
│ [ ] Option A             │
│ [ ] Option B             │
│ [ ] Option C             │
│ [ ] Option D             │
└────────┬─────────────────┘
         │
    ┌────┴────┐
    │          │
    ▼          ▼
  Manual    Auto-Submit
  Submit    (Time Ends)
    │          │
    └────┬─────┘
         │
         ▼
┌────────────────────────────┐
│ Grade Exam                 │
│ - Compare answers          │
│ - Count correct            │
│ - Save results to DB       │
└────────┬───────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Results Page                │
│ /results/<id>               │
│                             │
│ Score: 8/10                 │
│ Percentage: 80%             │
│ Correct: 8                  │
│ Wrong: 2                    │
└─────────────────────────────┘
```

## 📂 File Upload Process

```
┌────────────────┐
│ Upload Page    │
│ /upload        │
└────────┬───────┘
         │
         ▼
┌──────────────────────────┐
│ Upload Form              │
│ - Title Input            │
│ - Category Select        │
│ - File Input             │
│ - Submit Button          │
└────────┬─────────────────┘
         │
         ├─ Validate Input
         ├─ Check File Size
         ├─ Check Extension
         │
         ▼
┌──────────────────────┐
│ Valid?               │
└─┬────────────────┬──┘
  │ No             │ Yes
  │                │
  ▼                ▼
Error        Save File
Message      - Generate unique name
             - Save to disk
             - Save to database
             │
             ▼
        Success Message
        Redirect to Library
```

## 🎨 CSS Organization

```
style.css
│
├─ Root Variables (Colors, Fonts)
│
├─ Base Styles
│  ├─ * { box-sizing }
│  ├─ body { font, bg }
│  └─ .container { max-width }
│
├─ Navbar
│  ├─ .navbar { sticky }
│  ├─ .logo
│  └─ .nav-links
│
├─ Hero Section
│
├─ Features Grid
│
├─ Buttons
│  ├─ .btn-primary
│  ├─ .btn-secondary
│  └─ .login-btn (YOUR CSS!)
│
├─ Forms
│  ├─ .form-container
│  ├─ .form-card
│  ├─ .form-group
│  └─ Input Styles
│
├─ Dashboard
│  ├─ .dashboard-grid
│  ├─ .dashboard-card
│  └─ .stats-section
│
├─ Library & Exams
│  ├─ .library-grid
│  ├─ .file-card
│  └─ .exam-card
│
├─ Admin
│  ├─ .admin-tabs
│  └─ .admin-table
│
├─ Responsive (Mobile)
│  └─ @media (max-width: 768px)
│
└─ Animations & Effects
   ├─ @keyframes spin
   └─ Transitions
```

## ⚡ JavaScript Structure

```
script.js
│
├─ Dark Mode
│  ├─ toggleDarkMode()
│  └─ localStorage persistence
│
├─ Form Validation
│  ├─ validateEmail()
│  ├─ validatePassword()
│  ├─ loginForm listener
│  └─ signupForm listener
│
├─ AJAX Functions
│  ├─ fetchAPI()
│  └─ API calls for:
│     ├─ Load Files
│     ├─ Load Exams
│     ├─ Submit Answers
│     └─ Admin Operations
│
├─ UI Utilities
│  ├─ showNotification()
│  ├─ formatTime()
│  ├─ debounce()
│  └─ showLoading()
│
├─ Event Listeners
│  ├─ Form submissions
│  ├─ Button clicks
│  ├─ Filter/search
│  └─ Navigation
│
└─ Exam Logic
   ├─ startTimer()
   ├─ loadQuestions()
   ├─ submitExam()
   └─ displayResults()
```

## 🔐 Security Layers

```
┌─────────────────────────────────────┐
│ REQUEST ARRIVES                     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 1. Input Validation                 │
│    - Check empty fields             │
│    - Validate format                │
│    - Check file extensions          │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 2. Authentication Check             │
│    - Verify session exists          │
│    - Check login required           │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 3. Authorization Check              │
│    - Verify user role               │
│    - Check ownership                │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 4. Query Execution                  │
│    - Parameterized queries          │
│    - SQL injection prevention       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 5. Response Generation              │
│    - Template rendering             │
│    - JSON serialization             │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ RESPONSE SENT TO CLIENT             │
└─────────────────────────────────────┘
```

## 📱 Responsive Breakpoints

```
Mobile (< 768px)
└─ Single Column Layout
   └─ Full-width Forms
   └─ Stacked Cards
   └─ Hamburger Menu

Tablet (768px - 1024px)
└─ 2-Column Layout
   └─ Side-by-side Cards
   └─ Optimized spacing

Desktop (> 1024px)
└─ 3+ Column Layout
   └─ Full grid display
   └─ Maximum content width
```

## 🚀 Deployment Pipeline

```
Local Development
       ↓
   Git Push
       ↓
  GitHub Repo
       ↓
  ┌─────────────────────┐
  │ Deployment Options  │
  ├─────────────────────┤
  │ 1. Render.com       │ ← Recommended
  │ 2. Railway.app      │
  │ 3. PythonAnywhere   │
  │ 4. Heroku           │
  │ 5. AWS              │
  │ 6. DigitalOcean     │
  └─────────────────────┘
       ↓
   Live URL
       ↓
 Share with Users
```

---

**This visual guide helps you understand the complete architecture of your Bookstore website!** 📚✨
