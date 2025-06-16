import React, { useState, useEffect } from 'react';
import { Box, Typography, Alert, Chip, IconButton } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import VisibilityIcon from '@mui/icons-material/Visibility';
import apiClient from '../services/api';

// Helper to give colors to different order statuses
const statusColors = {
    PENDING_APPROVAL: 'warning',
    PROCESSING: 'info',
    READY_FOR_PICKUP: 'secondary',
    OUT_FOR_DELIVERY: 'secondary',
    DELIVERED: 'success',
    PICKED_UP: 'success',
    CANCELLED: 'error',
    FAILED: 'error',
    PENDING_PAYMENT: 'default',
};

function OrderPage() {
    const [orders, setOrders] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchOrders = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await apiClient.get('/orders/');
            setOrders(response.data);
        } catch (err) {
            setError('Failed to fetch orders.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    const columns = [
        { field: 'id', headerName: 'Order ID', width: 90 },
        {
            field: 'customer',
            headerName: 'Customer',
            flex: 1.5,
            renderCell: (params) => params.value?.name || params.value?.phone_number || 'N/A',
        },
        {
            field: 'status',
            headerName: 'Status',
            flex: 1,
            renderCell: (params) => (
                <Chip
                    label={params.value.replace('_', ' ')}
                    color={statusColors[params.value] || 'default'}
                    size="small"
                />
            ),
        },
        {
            field: 'total_amount',
            headerName: 'Total',
            type: 'number',
            flex: 1,
            renderCell: (params) => `$${parseFloat(params.value).toFixed(2)}`,
        },
        {
            field: 'created_at',
            headerName: 'Date',
            flex: 1.5,
            renderCell: (params) => new Date(params.value).toLocaleString(),
        },
        {
            field: 'actions',
            headerName: 'Actions',
            sortable: false,
            width: 100,
            renderCell: (params) => (
                <IconButton onClick={() => alert(`Viewing details for Order #${params.row.id}`)}>
                    <VisibilityIcon />
                </IconButton>
            ),
        },
    ];

    return (
        <Box>
            <Typography variant="h4" component="h1" gutterBottom>
                Order Management
            </Typography>
            
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            
            <Box sx={{ height: 650, width: '100%' }}>
                <DataGrid
                    rows={orders}
                    columns={columns}
                    loading={isLoading}
                    pageSizeOptions={[10, 25, 100]}
                    initialState={{
                        pagination: { paginationModel: { pageSize: 10 } },
                        sorting: { sortModel: [{ field: 'created_at', sort: 'desc' }] },
                    }}
                    sx={{ border: '1px solid rgba(224, 224, 224, 1)' }}
                />
            </Box>
            {/* TODO: Add a modal for viewing full order details and updating status */}
        </Box>
    );
}

export default OrderPage;