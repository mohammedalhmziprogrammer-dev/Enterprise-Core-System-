import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Clients from './pages/Clients';
import Users from './pages/Users';
import UserManagement from './pages/UserManagement';
import RoleManagement from './pages/RoleManagement';
import GroupManagement from './pages/GroupManagement';
import Apps from './pages/Apps';
import Codings from './pages/Codings';
import Releases from './pages/Releases';
import Layout from './components/Layout';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="clients" element={<Clients />} />
          <Route path="users" element={<Users />} />
          <Route path="user-management" element={<UserManagement />} />
          <Route path="role-management" element={<RoleManagement />} />
          <Route path="group-management" element={<GroupManagement />} />
          <Route path="apps" element={<Apps />} />
          <Route path="codings" element={<Codings />} />
          <Route path="releases" element={<Releases />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
