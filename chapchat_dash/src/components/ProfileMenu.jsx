import React from "react";
import { useAuthStore } from "../store/authStore";
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Typography,
  Divider,
  TextField,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings"; // Example icon
import LogoutIcon from "@mui/icons-material/Logout";
import apiClient from "../services/api";

function ProfileMenu() {
  const { user, accessToken, fetchUserProfile, logout } = useAuthStore();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [formData, setFormData] = React.useState(user || {});
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [success, setSuccess] = React.useState(false);

  const open = Boolean(anchorEl);

  const handleClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => {
    setAnchorEl(null);
    setError(null);
    setSuccess(false);
  };

  const handleChange = (event) => {
    setFormData({ ...formData, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(false);
    try {
      // We only need to send the fields that can actually be changed.
      const payload = {
        company_name: formData.company_name,
        whatsapp_phone_number_id: formData.whatsapp_phone_number_id,
        mpesa_shortcode: formData.mpesa_shortcode,
      };
      // Only include the passkey if the user has typed something into the field.
      // This prevents sending an empty string and overwriting an existing key.
      if (formData.mpesa_passkey) {
        payload.mpesa_passkey = formData.mpesa_passkey;
      }
      // Add other sensitive fields here in the same way (consumer_key, etc.)

      await apiClient.patch("seller/profile/", payload);
      await fetchUserProfile();
      setSuccess(true);
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update profile.");
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    // Pre-fill form, but don't show sensitive keys for security
    if (user) {
      setFormData({
        ...user,
        mpesa_passkey: "", // Always start with sensitive fields blank
        // Reset other sensitive fields here too
      });
    }
  }, [user]);

  if (!accessToken) return null;

  return (
    <div>
      <IconButton onClick={handleClick} size="small" sx={{ ml: 2 }}>
        <Avatar sx={{ width: 32, height: 32, bgcolor: "secondary.main" }}>
          {user?.username ? user.username[0].toUpperCase() : "?"}
        </Avatar>
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          elevation: 0,
          sx: {
            overflow: "visible",
            filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
            mt: 1.5,
            "& .MuiAvatar-root": { width: 32, height: 32, ml: -0.5, mr: 1 },
            "&:before": {
              content: '""',
              display: "block",
              position: "absolute",
              top: 0,
              right: 14,
              width: 10,
              height: 10,
              bgcolor: "background.paper",
              transform: "translateY(-50%) rotate(45deg)",
              zIndex: 0,
            },
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <Box sx={{ p: 2, minWidth: 320 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            {user?.username}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {user?.email}
          </Typography>
        </Box>
        <Divider />
        <Box component="form" onSubmit={handleSubmit} sx={{ p: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Profile Settings
          </Typography>
          <TextField
            fullWidth
            size="small"
            margin="dense"
            label="Company Name"
            name="company_name"
            value={formData.company_name || ""}
            onChange={handleChange}
          />
          <TextField
            fullWidth
            size="small"
            margin="dense"
            label="WhatsApp Phone Number ID"
            name="whatsapp_phone_number_id"
            value={formData.whatsapp_phone_number_id || ""}
            onChange={handleChange}
          />

          <TextField
            fullWidth
            size="small"
            margin="dense"
            label="Notification WhatsApp Number"
            name="notification_phone_number"
            value={formData.notification_phone_number || ""}
            onChange={handleChange}
            helperText="The number where you receive order alerts (e.g. 254...)."
          />


          {/* --- (+) ADDED MPESA FIELDS BACK --- */}
          <Typography variant="subtitle2" sx={{ mt: 2 }} gutterBottom>
            M-Pesa Settings
          </Typography>
          <TextField
            fullWidth
            size="small"
            margin="dense"
            label="M-Pesa Shortcode"
            name="mpesa_shortcode"
            value={formData.mpesa_shortcode || ""}
            onChange={handleChange}
          />
          <TextField
            fullWidth
            size="small"
            margin="dense"
            type="password"
            label="New M-Pesa Passkey"
            name="mpesa_passkey"
            value={formData.mpesa_passkey || ""}
            onChange={handleChange}
            placeholder="Leave blank to keep current key"
          />
          {/* You would add mpesa_consumer_key and secret here in the same way */}
          
          {success && (
            <Alert severity="success" sx={{ mt: 2, mb: 1 }}>
              Saved!
            </Alert>
          )}
          {error && (
            <Alert severity="error" sx={{ mt: 2, mb: 1 }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            size="small"
            variant="contained"
            sx={{ mt: 2 }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={20} /> : "Save Profile"}
          </Button>
        </Box>
        <Divider />
        <MenuItem onClick={logout}>
          <LogoutIcon sx={{ mr: 1 }} />
          Logout
        </MenuItem>
      </Menu>
    </div>
  );
}

export default ProfileMenu;
