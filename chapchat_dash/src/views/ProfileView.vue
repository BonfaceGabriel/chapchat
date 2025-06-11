<template>
  <div class="profile-view">
    <h2>My Seller Profile</h2>

    <!-- Show a loading message while fetching data -->
    <div v-if="isLoading" class="loading-state">Loading profile...</div>

    <!-- Show an error message if something went wrong -->
    <div v-else-if="error" class="error-state">
      <p>Error loading profile: {{ error }}</p>
      <button @click="fetchProfile">Try Again</button>
    </div>

    <!-- The main form, shown only when data is loaded successfully -->
    <form v-else-if="profileData" @submit.prevent="handleProfileUpdate">
      <div class="profile-section">
        <h3>Account Information (Read-only)</h3>
        <div class="form-group">
          <label>Username</label>
          <input type="text" :value="profileData.username" disabled />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input type="email" :value="profileData.email" disabled />
        </div>
      </div>

      <div class="profile-section">
        <h3>Business Details</h3>
        <div class="form-group">
          <label for="companyName">Company Name</label>
          <input
            type="text"
            id="companyName"
            v-model="profileData.company_name"
          />
        </div>
      </div>

      <div class="profile-section">
        <h3>M-Pesa Configuration</h3>
        <div class="form-group">
          <label for="mpesaShortcode">M-Pesa Shortcode</label>
          <input
            type="text"
            id="mpesaShortcode"
            v-model="profileData.mpesa_shortcode"
          />
        </div>
        <div class="form-group">
          <label for="mpesaPasskey">M-Pesa Passkey</label>
          <input
            type="password"
            id="mpesaPasskey"
            v-model="profileData.mpesa_passkey"
            placeholder="Enter new passkey to update"
          />
        </div>
        <!-- Add other M-Pesa fields here -->
      </div>

      <div class="profile-section">
        <h3>WhatsApp Configuration</h3>
        <div class="form-group">
          <label for="whatsappPhoneNumberId">WhatsApp Phone Number ID</label>
          <p class="help-text">
            Find this in your Meta for Developers App under WhatsApp > API
            Setup.
          </p>
          <input
            type="text"
            id="whatsappPhoneNumberId"
            v-model="profileData.whatsapp_phone_number_id"
          />
        </div>
      </div>

      <div v-if="updateSuccess" class="success-message">
        Profile updated successfully!
      </div>
      <div v-if="updateError" class="error-message">{{ updateError }}</div>

      <button type="submit" :disabled="isUpdating">
        {{ isUpdating ? "Saving..." : "Save Changes" }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import apiClient from "@/services/api";

// --- Vue Fundamentals: Component Lifecycle (onMounted) ---
// WHAT: `onMounted` is a "lifecycle hook". It's a function that Vue
// automatically runs at a specific point in a component's life.
// 'onMounted' runs right after the component has been added to the page (the DOM).
// WHY: It's the perfect place to fetch initial data from an API that the
// component needs to display.

// --- State Management for this component ---
const profileData = ref(null); // Will hold the profile data from the API
const isLoading = ref(true); // To show a loading indicator
const error = ref(null); // To store any errors during data fetching

const isUpdating = ref(false); // For the save button's loading state
const updateError = ref(null);
const updateSuccess = ref(false);

// Function to fetch the profile data
const fetchProfile = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get("/seller/profile/");
    profileData.value = response.data; // Store the fetched data
  } catch (err) {
    error.value = err.response?.data?.detail || "Could not fetch profile data.";
    console.error("Profile fetch error:", err);
  } finally {
    isLoading.value = false;
  }
};

// Function to handle the form submission
const handleProfileUpdate = async () => {
  isUpdating.value = true;
  updateError.value = null;
  updateSuccess.value = false;

  // The Django API for this view handles PATCH requests for partial updates.
  // This is ideal because we don't have to send the whole object every time.
  // We also don't want to send read-only fields back.
  const dataToUpdate = {
    company_name: profileData.value.company_name,
    mpesa_shortcode: profileData.value.mpesa_shortcode,
    // Only include sensitive fields if they have been changed from their initial state.
    // For simplicity now, we'll send them if they have a value.
    // A better approach would be to track if they've been "dirtied" by the user.
    mpesa_passkey: profileData.value.mpesa_passkey,
    whatsapp_phone_number_id: profileData.value.whatsapp_phone_number_id,
   
  };

  try {
    const response = await apiClient.patch("/seller/profile/", dataToUpdate);
    profileData.value = response.data; // Update local state with the saved data
    updateSuccess.value = true;
    // Hide success message after a few seconds
    setTimeout(() => {
      updateSuccess.value = false;
    }, 3000);
  } catch (err) {
    updateError.value =
      err.response?.data?.detail || "Failed to update profile.";
    console.error("Profile update error:", err);
  } finally {
    isUpdating.value = false;
  }
};

// --- Lifecycle Hook ---
// WHAT: We call our fetchProfile function as soon as the component is mounted.
// WHY: To load the data the user sees when they first navigate to this page.
onMounted(() => {
  fetchProfile();
});
</script>

<style scoped>
.profile-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.profile-section {
  background-color: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}
.profile-section h3 {
  margin-top: 0;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
  margin-bottom: 20px;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}
.form-group input {
  width: 100%;
  padding: 0.75rem;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.form-group input:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}
button {
  padding: 0.75rem 1.5rem;
  background-color: #2c3e50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}
button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.error-state,
.loading-state {
  text-align: center;
  padding: 40px;
  color: #666;
}
.error-message {
  color: red;
  margin-bottom: 1rem;
}
.success-message {
  color: green;
  margin-bottom: 1rem;
}
.help-text {
    font-size: 0.8rem;
    color: #666;
    margin-top: -0.5rem;
    margin-bottom: 0.5rem;
  }
</style>
