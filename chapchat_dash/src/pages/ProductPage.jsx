import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, CircularProgress, Alert, IconButton } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

import apiClient from '../services/api';
import ProductFormModal from '../components/ProductFormModal'; // Reuse our existing modal

function ProductPage() {
    const [products, setProducts] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // State for the modal
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedProduct, setSelectedProduct] = useState(null);

    const fetchProducts = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await apiClient.get('/products/');
            setProducts(response.data);
        } catch (err) {
            setError('Failed to fetch products.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    // Fetch products when the component first mounts
    useEffect(() => {
        fetchProducts();
    }, []);

    const handleOpenAddModal = () => {
        setSelectedProduct(null); // No product selected means "Add" mode
        setIsModalOpen(true);
    };

    const handleOpenEditModal = (product) => {
        setSelectedProduct(product);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setSelectedProduct(null);
    };

    const handleProductSaved = () => {
        handleCloseModal();
        // Refresh the product list to show the new/updated data
        fetchProducts();
    };

    const handleDeleteProduct = async (productId) => {
        if (window.confirm('Are you sure you want to delete this product? This action is not easily reversible.')) {
            try {
                await apiClient.delete(`/products/${productId}/`);
                // Refresh the list after successful deletion
                fetchProducts();
            } catch (err) {
                setError('Failed to delete product.');
                console.error(err);
            }
        }
    };

    // Define the columns for our DataGrid
    const columns = [
        { field: 'name', headerName: 'Product Name', flex: 2 },
        { field: 'sku', headerName: 'SKU', flex: 1 },
        {
            field: 'price',
            headerName: 'Price',
            flex: 1,
            renderCell: (params) => `$${parseFloat(params.value).toFixed(2)}`,
        },
        { field: 'inventory_count', headerName: 'Inventory', type: 'number', flex: 1 },
        {
            field: 'actions',
            headerName: 'Actions',
            sortable: false,
            filterable: false,
            width: 150,
            renderCell: (params) => (
                <Box>
                    <IconButton color="primary" onClick={() => handleOpenEditModal(params.row)}>
                        <EditIcon />
                    </IconButton>
                    <IconButton color="error" onClick={() => handleDeleteProduct(params.row.id)}>
                        <DeleteIcon />
                    </IconButton>
                </Box>
            ),
        },
    ];

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1">
                    Product Management
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleOpenAddModal}
                >
                    Add New Product
                </Button>
            </Box>
            
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            
            <Box sx={{ height: 600, width: '100%' }}>
                <DataGrid
                    rows={products}
                    columns={columns}
                    loading={isLoading}
                    pageSizeOptions={[10, 25, 50]}
                    initialState={{
                        pagination: { paginationModel: { pageSize: 10 } },
                    }}
                    sx={{
                        // Style overrides for a professional look
                        border: '1px solid rgba(224, 224, 224, 1)',
                        '& .MuiDataGrid-cell:hover': {
                            color: 'primary.main',
                        },
                    }}
                />
            </Box>

            <ProductFormModal
                show={isModalOpen}
                product={selectedProduct}
                onClose={handleCloseModal}
                onProductSaved={handleProductSaved}
            />
        </Box>
    );
}

export default ProductPage;