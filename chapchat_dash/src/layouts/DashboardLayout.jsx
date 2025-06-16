import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Box, Container, Link } from '@mui/material';
import ProfileMenu from '../components/ProfileMenu'; // We will create this next
import logo from '../assets/chapchat_logo.svg'; // We'll create a placeholder logo

function DashboardLayout() {
    return (
        <Box sx={{ display: 'flex' }}>
            {/* The Top Navigation Bar */}
            <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, background: 'linear-gradient(to right, #4c51bf, #667eea)' }}>
                <Toolbar>
                    {/* Logo and Company Name */}
                    <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
                        <img src={logo} alt="Chapchat Logo" style={{ height: '32px', marginRight: '16px' }} />
                        <Typography variant="h6" noWrap component="div">
                            Chapchat
                        </Typography>
                    </Box>

                    {/* Main Navigation Links */}
                    <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 2 }}>
                        {/* The Inbox route will be our dashboard index later */}
                        <Link component={NavLink} to="/dashboard/inbox" sx={navLinkStyles}>Inbox</Link>
                        <Link component={NavLink} to="/dashboard/products" sx={navLinkStyles}>Products</Link>
                        <Link component={NavLink} to="/dashboard/orders" sx={navLinkStyles}>Orders</Link>
                        <Link component={NavLink} to="/dashboard/analytics" sx={navLinkStyles}>Analytics</Link>
                    </Box>

                    <Box sx={{ flexGrow: 1 }} />

                    {/* Profile Menu on the right */}
                    <ProfileMenu />
                </Toolbar>
            </AppBar>

            {/* Main Content Area */}
            <Box component="main" sx={{ flexGrow: 1, p: 3, background: '#f4f7fe' }}>
                <Toolbar /> {/* This is a spacer to push content below the fixed AppBar */}
                <Container maxWidth="lg">
                   <Outlet />
                </Container>
            </Box>
        </Box>
    );
}

// Helper styles for NavLink active state
const navLinkStyles = {
    color: 'rgba(255, 255, 255, 0.8)',
    textDecoration: 'none',
    fontWeight: 500,
    '&.active': {
        color: '#ffffff',
        fontWeight: 700,
    },
    '&:hover': {
        color: '#ffffff',
    }
};

export default DashboardLayout;