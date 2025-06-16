import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

// This component checks if a user is authenticated.
// If they are, it renders the child components (the protected page).
// If not, it redirects them to the login page.
function ProtectedRoute({ children }) {
    const accessToken = useAuthStore((state) => state.accessToken);

    if (!accessToken) {
        // User not logged in, redirect to login page
        return <Navigate to="/login" replace />;
    }

    // User is logged in, render the page they were trying to access
    return children;
}

export default ProtectedRoute;