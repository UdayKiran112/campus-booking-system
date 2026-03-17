# Campus Facility Booking & Conflict Resolver - Sprint 1

Complete Sprint 1 implementation with Django backend + React frontend.

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit database credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000

## Features Implemented ✅
- User Authentication (8 roles)
- Venue Management (4 categories)
- Real-time Slot Availability
- Priority-based Booking (P1-P5)
- Conflict Detection
- Alternative Slots
- Payment Calculation
- Admin Dashboard

## API: http://localhost:8000/api
## Admin: http://localhost:8000/admin

See full documentation in project files.
