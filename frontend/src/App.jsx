import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import VenueSearch from './pages/VenueSearch';
import VenueDetails from './pages/VenueDetails';
import CreateBooking from './pages/CreateBooking';
import MyBookings from './pages/MyBookings';
import BookingDetails from './pages/BookingDetails';
import Profile from './pages/Profile';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="venues" element={<VenueSearch />} />
        <Route path="venues/:id" element={<VenueDetails />} />
        <Route path="bookings/create" element={<CreateBooking />} />
        <Route path="bookings" element={<MyBookings />} />
        <Route path="bookings/:id" element={<BookingDetails />} />
        <Route path="profile" element={<Profile />} />
      </Route>
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
        <Toaster position="top-right" />
      </Router>
    </AuthProvider>
  );
}

export default App;
