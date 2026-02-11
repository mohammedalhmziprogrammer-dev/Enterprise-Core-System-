# Quick Start Guide - Ufuq Frontend

## 🚀 Getting Started in 3 Steps

### Step 1: Start the Backend
```bash
cd Ufuq
python manage.py runserver
```
✅ Backend should be running at http://localhost:8000

### Step 2: Start the Frontend
Open a new terminal:
```bash
cd frontend
npm run dev
```
✅ Frontend should be running at http://localhost:5173 or http://localhost:5174

### Step 3: Login
1. Open your browser to http://localhost:5173 (or 5174)
2. You'll be redirected to the login page
3. Enter your Django admin credentials
4. Click "Sign In"

## 📱 What You'll See

After logging in, you'll have access to:

### Dashboard
- Overview of your application
- Quick statistics

### Clients (Sidebar Navigation)
- **Beneficiaries Tab**: View all beneficiaries
- **Structures Tab**: View organizational structures  
- **Levels Tab**: View hierarchical levels

### Users (Sidebar Navigation)
- **Users Tab**: View all system users
- **Roles Tab**: View user roles
- **Groups Tab**: View user groups

### Apps (Sidebar Navigation)
- Grid view of all applications
- App descriptions and links

## 🎨 Design Features

- **Dark Theme**: Premium dark mode throughout
- **Glassmorphism**: Modern glass-effect panels
- **Smooth Animations**: Fade-in effects and transitions
- **Responsive**: Works on all screen sizes
- **Icons**: Beautiful Lucide React icons

## 🔑 Test Credentials

Use your Django superuser credentials:
- Username: (your Django admin username)
- Password: (your Django admin password)

If you don't have a superuser, create one:
```bash
cd Ufuq
python manage.py createsuperuser
```

## 🛠️ Troubleshooting

### Port Already in Use
If port 5173 is in use, Vite will automatically try 5174. Both ports are configured in the backend CORS settings.

### CORS Errors
Make sure:
1. Backend is running on port 8000
2. CORS_ALLOWED_ORIGINS includes your frontend port in settings.py
3. corsheaders is in INSTALLED_APPS and MIDDLEWARE

### Authentication Errors
- Make sure you're using valid Django user credentials
- Check that the backend /token/ endpoint is accessible
- Clear localStorage and try again

### Data Not Loading
- Verify backend is running
- Check browser console for errors
- Ensure API endpoints are accessible (try visiting http://localhost:8000/clients/beneficiaries/ directly)

## 📦 Production Build

To create a production build:
```bash
cd frontend
npm run build
```

The build output will be in the `dist/` folder.

## 🎯 Key Files

- `src/api.js` - All API endpoints and authentication
- `src/App.jsx` - Main routing configuration
- `src/index.css` - All styles (545+ lines)
- `src/components/Layout.jsx` - Sidebar navigation
- `src/pages/` - All page components

## 💡 Tips

1. **Navigation**: Use the sidebar to switch between sections
2. **Tabs**: Click tabs in Clients/Users pages to view different data
3. **Logout**: Click the red logout button at the bottom of the sidebar
4. **Refresh**: Data is fetched when you navigate to a page

## 📚 Learn More

- See `README.md` for detailed documentation
- See `PROJECT_SUMMARY.md` for technical overview
- Check the backend API at http://localhost:8000/admin/

Enjoy your new frontend! 🎉
