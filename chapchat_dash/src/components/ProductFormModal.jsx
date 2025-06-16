import React, { useState, useEffect } from "react";
import {
  Modal,
  Box,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";
import apiClient from "../services/api";

// This is the style for the modal content box. It's a standard MUI practice.
const style = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "90%",
  maxWidth: 600,
  bgcolor: "background.paper",
  border: "1px solid #ddd",
  boxShadow: 24,
  p: 4,
  borderRadius: 2,
};

function ProductFormModal({ show, onClose, product, onProductSaved }) {
  // --- React Fundamentals: Props ---
  // 'show': boolean to control if the modal is open.
  // 'onClose': function to call when the modal should close.
  // 'product': object with product data (or null if we are adding a new product).
  // 'onProductSaved': function to call after a product is successfully saved.

  const [formData, setFormData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const isEditing = Boolean(product); // True if a product prop is passed

  // --- React Fundamentals: useEffect ---
  // This hook "watches" the `product` prop. If it changes (e.g., user clicks 'Edit'),
  // we update the form's internal state with the new data.
  useEffect(() => {
    if (isEditing) {
      // If we're editing, pre-fill the form with the product's data
      setFormData({
        name: product.name || "",
        sku: product.sku || "",
        price: product.price || 0,
        inventory_count: product.inventory_count || 0,
        description: product.description || "",
        sizes: product.sizes?.join(", ") || "", // Convert array to comma-separated string for the input
      });
    } else {
      // If adding a new product, reset the form to a blank state
      setFormData({
        name: "",
        sku: "",
        price: "",
        inventory_count: 0,
        description: "",
        sizes: "",
      });
    }
    // Reset error when modal is opened for a new product or re-opened
    setError(null);
  }, [product, show, isEditing]); // Rerun this effect if the `product`, `show`, or `isEditing` props change

  const handleChange = (event) => {
    setFormData({ ...formData, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    // Convert the comma-separated sizes string back into an array for the API
    const payload = {
      ...formData,
      price: parseFloat(formData.price),
      inventory_count: parseInt(formData.inventory_count, 10),
      sizes: formData.sizes
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s),
    };

    try {
      if (isEditing) {
        // If editing, make a PATCH request
        await apiClient.patch(`/products/${product.id}/`, payload);
      } else {
        // If adding, make a POST request
        await apiClient.post("/products/", payload);
      }
      onProductSaved(); // Call the parent's callback function
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData) {
        // Format multiple backend errors into a single string
        const messages = Object.keys(errorData)
          .map(
            (key) =>
              `${key}: ${
                Array.isArray(errorData[key])
                  ? errorData[key].join(", ")
                  : errorData[key]
              }`
          )
          .join(" | ");
        setError(messages || "An error occurred.");
      } else {
        setError("An unknown network error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      open={show}
      onClose={onClose}
      aria-labelledby="product-modal-title"
      aria-describedby="product-modal-description"
    >
      <Box sx={style}>
        <Typography id="product-modal-title" variant="h6" component="h2">
          {isEditing ? "Edit Product" : "Add New Product"}
        </Typography>

        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <TextField
            fullWidth
            margin="normal"
            label="Product Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
          <TextField
            fullWidth
            margin="normal"
            label="SKU (Stock Keeping Unit)"
            name="sku"
            value={formData.sku}
            onChange={handleChange}
            required
          />
          <TextField
            fullWidth
            margin="normal"
            label="Price"
            name="price"
            type="number"
            value={formData.price}
            onChange={handleChange}
            required
          />
          <TextField
            fullWidth
            margin="normal"
            label="Inventory Count"
            name="inventory_count"
            type="number"
            value={formData.inventory_count}
            onChange={handleChange}
            required
          />
          <TextField
            fullWidth
            margin="normal"
            multiline
            rows={4}
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleChange}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Sizes (comma-separated)"
            name="sizes"
            value={formData.sizes}
            onChange={handleChange}
            helperText="e.g., S, M, L, XL"
          />

          <Box
            sx={{ mt: 3, display: "flex", justifyContent: "flex-end", gap: 1 }}
          >
            <Button variant="outlined" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={isLoading}>
              {isLoading ? <CircularProgress size={24} /> : "Save Product"}
            </Button>
          </Box>
        </Box>
      </Box>
    </Modal>
  );
}

export default ProductFormModal;
