import React, { useState } from 'react';
import { Modal, Box, Typography, Button, CircularProgress, Alert, Grid, Divider, Paper, Stack, Chip } from '@mui/material';
import apiClient from '../services/api';

// Style for the modal box
const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '90%',
  maxWidth: 700,
  bgcolor: 'background.paper',
  boxShadow: 24,
  p: 4,
  borderRadius: 2,
};

// Helper to get colors for status chips
const statusColors = {
  PENDING_APPROVAL: 'warning',
  PROCESSING: 'info',
  OUT_FOR_DELIVERY: 'secondary',
  DELIVERED: 'success',
  CANCELLED: 'error',
  FAILED: 'error',
};

function OrderDetailModal({ show, onClose, order, onOrderUpdate }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!order) return null; // Don't render if no order is selected

  const handleStatusUpdate = async (newStatus) => {
    setIsLoading(true);
    setError(null);
    try {
      // We only need to PATCH the status field
      await apiClient.patch(`/orders/${order.id}/`, { status: newStatus });
      onOrderUpdate(); // This will trigger a refresh on the parent page
    } catch (err) {
      setError('Failed to update order status.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Determine which action buttons to show based on the current status
  const renderActionButtons = () => {
    switch (order.status) {
      case 'PENDING_APPROVAL':
        return (
          <Button variant="contained" onClick={() => handleStatusUpdate('PROCESSING')} disabled={isLoading}>
            Approve Order
          </Button>
        );
      case 'PROCESSING':
        return (
          <Button variant="contained" onClick={() => handleStatusUpdate('OUT_FOR_DELIVERY')} disabled={isLoading}>
            Mark as Out for Delivery
          </Button>
        );
      case 'READY_FOR_PICKUP':
         return (
          <Button variant="contained" onClick={() => handleStatusUpdate('PICKED_UP')} disabled={isLoading}>
            Mark as Picked Up
          </Button>
        );
      case 'OUT_FOR_DELIVERY':
        return (
          <Button variant="contained" onClick={() => handleStatusUpdate('DELIVERED')} disabled={isLoading}>
            Mark as Delivered
          </Button>
        );
      default:
        return null; // No actions for completed, failed, or cancelled orders
    }
  };

  return (
    <Modal open={show} onClose={onClose}>
      <Box sx={style}>
        <Typography variant="h5" component="h2">
          Order Details #{order.id}
        </Typography>
        <Chip
          label={order.status.replace('_', ' ')}
          color={statusColors[order.status] || 'default'}
          size="small"
          sx={{ my: 1 }}
        />
        <Divider sx={{ my: 2 }} />

        <Grid container spacing={2}>
          {/* Customer and Delivery Info */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>Customer</Typography>
            <Typography><strong>Name:</strong> {order.customer?.name || 'N/A'}</Typography>
            <Typography><strong>Phone:</strong> {order.customer?.phone_number}</Typography>
            
            <Typography variant="h6" sx={{ mt: 2 }} gutterBottom>Fulfillment</Typography>
            <Typography><strong>Method:</strong> {order.delivery_option}</Typography>
            {order.delivery_option === 'DELIVERY' && (
              <Typography><strong>Address:</strong> {order.delivery_address_text || 'N/A'}</Typography>
            )}
          </Grid>

          {/* Order Items */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>Items</Typography>
            <Stack spacing={1}>
              {order.items.map(item => (
                <Paper variant="outlined" key={item.id} sx={{ p: 1, display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>
                    {item.quantity} x {item.product?.name} 
                    {item.selected_size && ` (Size: ${item.selected_size})`}
                  </Typography>
                  <Typography fontWeight="bold">
                    ${(item.quantity * item.price_at_time_of_purchase).toFixed(2)}
                  </Typography>
                </Paper>
              ))}
              <Divider />
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="h6">Total:</Typography>
                <Typography variant="h6">${parseFloat(order.total_amount).toFixed(2)}</Typography>
              </Box>
            </Stack>
          </Grid>
        </Grid>

        {/* Action Buttons */}
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button variant="outlined" onClick={onClose}>Close</Button>
          <Box>
            {isLoading ? <CircularProgress size={24} /> : renderActionButtons()}
          </Box>
        </Box>

        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      </Box>
    </Modal>
  );
}

export default OrderDetailModal;