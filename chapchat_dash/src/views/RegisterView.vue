<template>
  <div class="register-view">
    <h1>Create Your Retailer Account</h1>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="formData.username" required />
      </div>
      <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" v-model="formData.email" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          v-model="formData.password"
          required
        />
      </div>
      <div class="form-group">
        <label for="password2">Confirm Password</label>
        <input
          type="password"
          id="password2"
          v-model="formData.password2"
          required
        />
      </div>

      <!-- Display loading state or error messages -->
      <div v-if="authStore.isLoading" class="loading">Registering...</div>
      <div v-if="errorMessage" class="error-message">
        <p>{{ errorMessage }}</p>
      </div>
      <div v-if="successMessage" class="success-message">
        <p>{{ successMessage }}</p>
      </div>

      <button type="submit" :disabled="authStore.isLoading">Register</button>
    </form>
    <p>
      Already have an account? <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

// --- Vue Fundamentals: reactive() ---
// WHAT: `reactive()` is another way to declare reactive state, best used for objects.
// WHY: Instead of creating a separate `ref()` for each form field, we can group
// them into a single reactive object. You access properties directly, e.g., `formData.username`.
const formData = reactive({
  username: "",
  email: "",
  password: "",
  password2: "",
});

const errorMessage = ref(null);
const successMessage = ref(null);
const authStore = useAuthStore();
const router = useRouter();

const handleRegister = async () => {
  // Clear previous messages
  errorMessage.value = null;
  successMessage.value = null;

  try {
    await authStore.register({ ...formData }); // Pass a copy of the formData
    successMessage.value = "Registration successful! Redirecting to login...";

    // Redirect to login page after a short delay
    setTimeout(() => {
      router.push("/login");
    }, 2000); // 2-second delay
  } catch (error) {
    // The store sets its own error, but we can format it nicely here
    if (error.response && error.response.data) {
      // Combine multiple errors into a single string
      const errorData = error.response.data;
      errorMessage.value = Object.keys(errorData)
        .map((key) => `${key}: ${errorData[key].join(", ")}`)
        .join(" | ");
    } else {
      errorMessage.value = "An unknown error occurred during registration.";
    }
    console.error("Registration failed in component:", error);
  }
};
</script>

<style scoped>
/* You can copy the styles from LoginView.vue or use a shared CSS file */
.register-view {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  text-align: left;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}
.form-group input {
  width: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 0.75rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.error-message {
  color: red;
  margin-bottom: 1rem;
  background-color: #ffdddd;
  border-left: 6px solid #f44336;
  padding: 10px;
}
.success-message {
  color: green;
  margin-bottom: 1rem;
  background-color: #ddffdd;
  border-left: 6px solid #4caf50;
  padding: 10px;
}
.loading {
  color: #333;
  margin-bottom: 1rem;
}
p {
  text-align: center;
  margin-top: 1rem;
}
</style>
