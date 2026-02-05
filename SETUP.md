# Food Waste Management Platform - Setup Guide

## Backend Setup (Django)

1. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server:**
   ```bash
   python manage.py runserver
   ```
   Backend will run on `http://localhost:8000`

## Frontend Setup (React)

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

## Features

### Backend Features
- ✅ User authentication with JWT
- ✅ Role-based access (Donor/NGO/Admin)
- ✅ Donation management
- ✅ Food request system
- ✅ Pickup scheduling
- ✅ Risk assessment (time-based, no ML)
- ✅ Impact tracking (meals saved, CO₂ reduced)
- ✅ Rating system
- ✅ Heatmap data endpoint
- ✅ CORS configured for React frontend

### Frontend Features
- ✅ User authentication (Login/Register)
- ✅ Dashboard with statistics
- ✅ Donation listing and creation
- ✅ Food request management
- ✅ Impact statistics visualization
- ✅ Heatmap data display
- ✅ Responsive design

## API Endpoints

### Authentication
- `POST /api/register/` - Register new user
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Donations
- `GET /api/donations/` - List donations (role-based)
- `POST /api/donations/` - Create donation (Donor only)
- `GET /api/donations/{id}/` - Get donation details
- `PUT /api/donations/{id}/` - Update donation (Donor only)
- `DELETE /api/donations/{id}/` - Delete donation (Donor only)

### Requests
- `GET /api/requests/` - List requests (role-based)
- `POST /api/requests/` - Create request (NGO only)
- `POST /api/requests/{id}/approve/` - Approve request (Donor only)
- `POST /api/requests/{id}/complete_pickup/` - Complete pickup (NGO only)

### Statistics
- `GET /api/stats/impact/` - Get impact statistics
- `GET /api/stats/heatmap/` - Get heatmap data

### Ratings
- `GET /api/ratings/` - List ratings
- `POST /api/ratings/` - Create rating

### Documentation
- `GET /swagger/` - Swagger UI documentation
- `GET /schema/` - OpenAPI schema

## User Roles

- **DONOR**: Can create donations, approve requests
- **NGO**: Can view available donations, create requests, complete pickups
- **ADMIN**: Full access (via Django admin)

## Notes

- No ML/AI is used - risk assessment is based on simple time-based rules
- Email notifications are configured but use console backend (for development)
- Database is SQLite (can be changed to PostgreSQL in production)
- CORS is configured for localhost:5173 and localhost:3000

