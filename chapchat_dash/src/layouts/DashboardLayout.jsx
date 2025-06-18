import React from "react";
import { Outlet, NavLink } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Container,
  Link,
} from "@mui/material";
import ProfileMenu from "../components/ProfileMenu";
// Assuming you have a placeholder logo, otherwise remove the next line and the <img> tag
import logo from "../assets/chapchat_logo.svg";
import { useInboxSocket } from "../hooks/useInboxSocket"; // Keep this import

function DashboardLayout() {
  // This line correctly initializes the WebSocket connection for any page using this layout.
  useInboxSocket();

  // We no longer need to get 'user' or 'logout' here because the
  // ProfileMenu component handles all of that itself.

  return (
    <Box sx={{ display: "flex" }}>
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: "linear-gradient(to right, #4c51bf, #667eea)",
        }}
      >
        <Toolbar>
          <Box sx={{ display: "flex", alignItems: "center", flexGrow: 1 }}>
            <img
              src={logo}
              alt="Chapchat Logo"
              style={{ height: "32px", marginRight: "16px" }}
            />
            <Typography variant="h6" noWrap component="div">
              Chapchat
            </Typography>
          </Box>

          <Box sx={{ display: { xs: "none", md: "flex" }, gap: 2 }}>
            {/* We'll make /dashboard/inbox the main page later */}
            <Link component={NavLink} to="/dashboard" sx={navLinkStyles}>
              Inbox
            </Link>
            <Link
              component={NavLink}
              to="/dashboard/products"
              sx={navLinkStyles}
            >
              Products
            </Link>
            <Link component={NavLink} to="/dashboard/orders" sx={navLinkStyles}>
              Orders
            </Link>
            <Link
              component={NavLink}
              to="/dashboard/analytics"
              sx={navLinkStyles}
            >
              Analytics
            </Link>
          </Box>

          <Box sx={{ flexGrow: 1 }} />
          <ProfileMenu />
        </Toolbar>
      </AppBar>

      <Box component="main" sx={{ flexGrow: 1, p: 3, background: "#f4f7fe" }}>
        <Toolbar />
        <Container maxWidth="lg">
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
}

// Helper styles for NavLink active state
const navLinkStyles = {
  color: "rgba(255, 255, 255, 0.8)",
  textDecoration: "none",
  fontWeight: 500,
  "&.active": {
    color: "#ffffff",
    fontWeight: 700,
  },
  "&:hover": {
    color: "#ffffff",
  },
};

export default DashboardLayout;
