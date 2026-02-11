# Frontend for Ufuq Project

This is the React frontend for the Ufuq project, built with Vite and connected to a Django REST backend.

## Features

### 🔐 Authentication
- JWT-based login system
- Protected routes with automatic redirection
- Token management with localStorage

### 📊 Dashboard
- Overview page with statistics
- Modern glassmorphism design
- Dark theme with premium aesthetics

### 👥 Clients Management
- **Beneficiaries**: View and manage beneficiaries
- **Structures**: Organizational structure management
- **Levels**: Hierarchical level management
- Tabbed interface for easy navigation
- Dynamic data tables

### 👤 Users Management
- **Users**: Complete user management
- **Roles**: Role-based access control
- **Groups**: User group management
- Comprehensive user information display

### 📱 Applications
- App catalog with grid layout
- App descriptions and links
- Visual app icons

## Prerequisites

- Node.js (v16 or higher)
- Backend running on `http://localhost:8000`

## Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (if not already done):
   ```bash
   npm install
   ```

## Running the Development Server

To start the frontend in development mode:

```bash
npm run dev
```

The app will be available at `http://localhost:5173` or `http://localhost:5174`.

## Building for Production

To create a production build:

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── api.js                 # API service and endpoints
│   ├── App.jsx                # Main app with routing
│   ├── index.css              # Global styles
│   ├── components/
│   │   └── Layout.jsx         # Main layout with sidebar
│   └── pages/
│       ├── Login.jsx          # Login page
│       ├── Dashboard.jsx      # Dashboard page
│       ├── Clients.jsx        # Clients management
│       ├── Users.jsx          # Users management
│       └── Apps.jsx           # Applications page
├── public/
└── package.json
```

## API Endpoints Used

- `/token/` - Authentication
- `/clients/beneficiaries/` - Beneficiaries data
- `/clients/structures/` - Structures data
- `/clients/levels/` - Levels data
- `/users/users/` - Users data
- `/users/role/` - Roles data
- `/users/group/` - Groups data
- `/apps/apps/` - Applications data

## Connecting to Backend

The frontend is configured to connect to `http://localhost:8000`.
If your backend runs on a different port, update the `API_URL` constant in `src/api.js`.

## Design Features

- **Dark Theme**: Premium dark mode with carefully selected colors
- **Glassmorphism**: Modern glass-effect panels with backdrop blur
- **Smooth Animations**: Fade-in effects and hover transitions
- **Responsive Layout**: Adapts to different screen sizes
- **Icon System**: Lucide React icons throughout the interface
- **Custom CSS**: Vanilla CSS with semantic class names (no Tailwind)

## Technologies Used

- **React** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **Vanilla CSS** - Styling (no CSS frameworks)
