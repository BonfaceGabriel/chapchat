<template>
  <div>
    <div class="product-list-view">
      <div class="header">
        <h2>Your Products</h2>
        <button @click="openAddModal">Add New Product</button>
      </div>

      <div v-if="isLoading" class="loading-state">Loading products...</div>
      <div v-else-if="error" class="error-state">
        <p>Error loading products: {{ error }}</p>
        <button @click="fetchProducts">Try Again</button>
      </div>

      <table v-else-if="products.length > 0" class="product-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>SKU</th>
            <th>Price</th>
            <th>Inventory</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td>{{ product.name }}</td>
            <td>{{ product.sku }}</td>
            <td>${{ product.price }}</td>
            <td>{{ product.inventory_count }}</td>
            <td>
              <button class="action-btn edit" @click="openEditModal(product)">
                Edit
              </button>
              <button class="action-btn delete" @click="confirmDelete(product)">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty-state">
        <p>You haven't added any products yet.</p>
        <button @click="openAddModal">Add your first product</button>
      </div>
    </div>

    <!-- (+) USE THE MODAL COMPONENT -->
    <!-- We bind its props to our local state and listen for its emits. -->
    <ProductFormModal
      :show="isModalVisible"
      :product="selectedProduct"
      @close="closeModal"
      @product-saved="handleProductSaved"
    />
  </div>
</template>

<script setup>
import ProductFormModal from "@/components/ProductFormModal.vue";
import { ref, onMounted } from "vue";
import apiClient from "@/services/api";

// --- State for this component ---
const products = ref([]);
const isLoading = ref(true);
const error = ref(null);

// (+) NEW STATE to manage the modal
const isModalVisible = ref(false);
const selectedProduct = ref(null); // Will hold the product being edited

// --- Logic for fetching products ---
// WHAT: An async function to make the API call to our Django backend.
// WHY: We need to fetch the data to display it. `async/await` makes
// handling the asynchronous API call clean and readable.
const fetchProducts = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get("/products/");
    products.value = response.data; // Store the array of products in our reactive state
  } catch (err) {
    error.value = "Could not fetch products. Please try again later.";
    console.error("Product fetch error:", err);
  } finally {
    isLoading.value = false;
  }
};

// --- Lifecycle Hook ---
// WHAT: Call `fetchProducts` when the component is first mounted.
// WHY: To automatically load the product list when the user navigates to this page.
onMounted(() => {
  fetchProducts();
});

// --- Placeholder functions for our modal actions ---
// We will implement these properly when we create the modal component.
const openAddModal = () => {
  selectedProduct.value = null; // Clear any selected product (so it's in "Add" mode)
  isModalVisible.value = true;
};

const openEditModal = (product) => {
  selectedProduct.value = product; // Set the product to be edited
  isModalVisible.value = true;
};

const closeModal = () => {
  isModalVisible.value = false;
  selectedProduct.value = null; // Clear selection on close
};

const handleProductSaved = () => {
  // When the modal emits 'product-saved', we simply close the modal
  // and refetch the list to show the new/updated data.
  closeModal();
  fetchProducts();
};

const confirmDelete = async (product) => {
  if (
    window.confirm(
      `Are you sure you want to delete "${product.name}"? This cannot be undone.`
    )
  ) {
    try {
      // Make the DELETE request to our API
      await apiClient.delete(`/products/${product.id}/`);
      // If successful, refetch the product list to show the change
      alert(`"${product.name}" has been deleted.`);
      fetchProducts();
    } catch (err) {
      alert(`Failed to delete product. Please try again.`);
      console.error("Delete error:", err);
    }
  }
};

onMounted(() => {
  fetchProducts();
});
</script>

<style scoped>
.product-list-view {
  padding: 1rem;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.header h2 {
  margin: 0;
}
.product-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
.product-table th,
.product-table td {
  border-bottom: 1px solid #ddd;
  padding: 12px 15px;
}
.product-table th {
  background-color: #f8f8f8;
}
.action-btn {
  margin-right: 5px;
  padding: 5px 10px;
  border: 1px solid transparent;
  border-radius: 4px;
  cursor: pointer;
}
.action-btn.edit {
  background-color: #e0e0e0;
}
.action-btn.delete {
  background-color: #fbe9e7;
  color: #c62828;
}
.empty-state,
.loading-state,
.error-state {
  text-align: center;
  padding: 50px;
  background-color: #f9f9f9;
  border-radius: 8px;
}
</style>
