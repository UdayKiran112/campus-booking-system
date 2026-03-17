# Quick Start Guide - Campus Facility Booking System

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Prerequisites

**Check if you have:**
```bash
python --version  # Should be 3.9+
node --version    # Should be 16+
psql --version    # PostgreSQL 13+
```

### Step 2: Setup Database

```bash
psql -U postgres
CREATE DATABASE campus_booking_db;
\q
```

### Step 3: Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Set DB_PASSWORD=your_postgres_password
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend: http://localhost:8000

### Step 4: Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

### Step 5: First Login

1. Register at http://localhost:3000/register
2. Login with your credentials
3. Start booking venues!

## Common Issues

**Database connection error:**
- Check PostgreSQL is running
- Verify .env database credentials

**Port already in use:**
- Backend: `python manage.py runserver 8001`
- Frontend: Change port in vite.config.js

**Module not found:**
- Backend: `pip install -r requirements.txt`
- Frontend: `npm install`

## Admin Access

Access Django admin: http://localhost:8000/admin
- Create test venues
- Manage users
- View all bookings
