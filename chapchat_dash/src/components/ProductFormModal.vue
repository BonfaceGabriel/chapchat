<template>
  <!-- The modal overlay -->
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <!-- The modal content -->
    <div class="modal-content">
      <button class="close-button" @click="$emit('close')">×</button>
      <h2>{{ isEditing ? "Edit Product" : "Add New Product" }}</h2>

      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="name">Product Name</label>
          <input type="text" id="name" v-model="localProduct.name" required />
        </div>

        <div class="form-group">
          <label for="sku">SKU (Stock Keeping Unit)</label>
          <input type="text" id="sku" v-model="localProduct.sku" required />
        </div>

        <div class="form-group">
          <label for="price">Price</label>
          <input
            type="number"
            step="0.01"
            id="price"
            v-model="localProduct.price"
            required
          />
        </div>

        <div class="form-group">
          <label for="inventory_count">Inventory Count</label>
          <input
            type="number"
            id="inventory_count"
            v-model="localProduct.inventory_count"
            required
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="localProduct.description"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="sizes">Sizes (comma-separated)</label>
          <input
            type="text"
            id="sizes"
            v-model="sizesAsText"
            placeholder="e.g., S, M, L, XL"
          />
        </div>

        <!-- Error message display -->
        <div v-if="error" class="error-message">{{ error }}</div>

        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="$emit('close')">
            Cancel
          </button>
          <button type="submit" :disabled="isLoading">
            {{ isLoading ? "Saving..." : "Save Product" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import apiClient from "@/services/api";

// --- Vue Fundamentals: Props ---
// WHAT: 'props' are how a parent component (like ProductListView) passes data
// DOWN to a child component (this modal).
// WHY: We need props to tell the modal whether it should be shown, and if it's
// for editing, which product's data to pre-fill.
const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  product: {
    type: Object,
    default: null, // Default to null for "Add" mode
  },
});

// --- Vue Fundamentals: Emits ---
// WHAT: 'emits' are how a child component sends messages UP to its parent.
// WHY: The modal needs to tell ProductListView when to close itself or
// when a product has been successfully saved, so the list can be refreshed.
const emit = defineEmits(["close", "product-saved"]);

// --- Component-Specific State ---
const localProduct = ref({});
const isLoading = ref(false);
const error = ref(null);

// --- Vue Fundamentals: computed() ---
// WHAT: A computed property is a value that is derived from other reactive data.
// It automatically updates whenever its dependencies change.
// WHY: Our API expects 'sizes' as an array of strings, but it's easier for the
// user to type them as a single comma-separated string. A computed property is
// perfect for converting between these two formats.
const sizesAsText = computed({
  // The 'get' function runs when we need to display the value
  get() {
    // If sizes exist, join the array into a string. Otherwise, return an empty string.
    return localProduct.value.sizes ? localProduct.value.sizes.join(", ") : "";
  },
  // The 'set' function runs when the user types into the input field
  set(newValue) {
    // Split the string by commas, trim whitespace from each part, and filter out empty strings.
    localProduct.value.sizes = newValue
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s);
  },
});

const isEditing = computed(() => !!props.product);

// --- Vue Fundamentals: watch() ---
// WHAT: `watch` is a function that "watches" a reactive source (like a prop)
// and runs a callback function whenever that source changes.
// WHY: When the parent component tells the modal to open for editing, the `product`
// prop will change. We need to watch for this change to update our form's
// local data (`localProduct`) with the new product's details.
watch(
  () => props.product,
  (newProduct) => {
    if (newProduct) {
      // If we are editing, copy the product's data into our local state.
      // The spread operator `{...newProduct}` creates a copy, so we don't
      // directly modify the original data in the parent list until we save.
      localProduct.value = { ...newProduct };
    } else {
      // If we are adding, reset the form to a blank state.
      localProduct.value = {
        name: "",
        sku: "",
        price: 0,
        inventory_count: 0,
        description: "",
        sizes: [],
        images: [], // We'll handle image uploads later
      };
    }
    // Also reset any error messages when the modal is opened.
    error.value = null;
  },
  { immediate: true }
); // `immediate: true` runs the watcher once right away on component creation.

const submitForm = async () => {
  isLoading.value = true;
  error.value = null;
  //   emit("product-saved"); // This will trigger the parent to refetch its list
  //   emit("close"); // Close the modal immediately for a better UX

  // Prepare the data to be sent. We only send the fields the API expects.
  const payload = {
    name: localProduct.value.name,
    sku: localProduct.value.sku,
    price: localProduct.value.price,
    inventory_count: localProduct.value.inventory_count,
    description: localProduct.value.description,
    sizes: localProduct.value.sizes,
    // images will be handled later
  };

  try {
    if (isEditing.value) {
      // If editing, make a PATCH request to update the existing product
      await apiClient.patch(`/products/${props.product.id}/`, payload);
    } else {
      // If adding, make a POST request to create a new product
      await apiClient.post("/products/", payload);
    }
    // If the API call is successful, emit the event to the parent
    emit("product-saved");
    emit("close"); // Close the modal
  } catch (err) {
    // If the API call fails, display the error
    error.value =
      err.response?.data?.detail ||
      err.response?.data?.sku?.[0] ||
      "An error occurred.";
    console.error("Form submission error:", err.response);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  position: relative;
}
.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  border: none;
  background: none;
  font-size: 1.5rem;
  cursor: pointer;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
textarea {
  min-height: 100px;
  resize: vertical;
}
.cancel-btn {
  background-color: #eee;
  color: #333;
}
</style>
