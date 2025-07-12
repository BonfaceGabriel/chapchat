import { useRoutes, Link as RouterLink } from 'react-router-dom';

// We will import our page components here later
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardLayout from './layouts/DashboardLayout';
import ProtectedRoute from './components/ProtectedRoute'; 
import ProductPage from './pages/ProductPage';
import OrderPage from './pages/OrderPage';
import AnalyticsPage from './pages/AnalyticsPage';
import InboxPage from './pages/InboxPage';

export default function AppRouter() {
  const routes = useRoutes([
    {
      path: '/login',
      element: <LoginPage />,
    },
    {
      path: '/register',
      element: <RegisterPage />,
    },
    {
            // This is our protected dashboard route
            path: '/dashboard',
            element: (
                <ProtectedRoute>
                    <DashboardLayout />
                </ProtectedRoute>
            ),
            // These are the nested child routes
            children: [
                { index: true, element: <InboxPage /> },
                { path: 'inbox', element: <InboxPage /> },
                { path: 'products', element: <ProductPage /> },
                { path: 'orders', element: <OrderPage /> },
                { path: 'analytics', element: <AnalyticsPage /> },
            ],
        },
    {
      // A simple index route
      path: '/',
            element: <div>Welcome! <RouterLink to="/login">Login</RouterLink> or <RouterLink to="/register">Register</RouterLink></div>,
    },
  ]);

  return routes;
}