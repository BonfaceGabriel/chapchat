<template>
  <div class="login-view">
    <h1>Retailer Login</h1>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required />
      </div>

      <!-- Display loading state or error messages -->
      <div v-if="authStore.isLoading" class="loading">Logging in...</div>
      <div v-if="authStore.error" class="error-message">
        {{ authStore.error }}
      </div>

      <button type="submit" :disabled="authStore.isLoading">Login</button>
    </form>
    <p>
      Don't have an account?
      <router-link to="/register">Register here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";

// --- Vue Fundamentals: ref() ---
// WHAT: `ref()` is a function from Vue that makes a value "reactive".
// WHY: In Vue, if you want the component to update automatically when a variable's
// value changes (e.g., when a user types into an input field), you need to wrap
// that variable's initial value in `ref()`. `ref()` returns an object with a `.value` property.
// You access or change the value using `username.value`, but in the <template>,
// Vue automatically "unwraps" it, so you can just use `v-model="username"`.
const username = ref("");
const password = ref("");

// WHAT: Get an instance of our Pinia auth store.
// WHY: This gives us access to the store's state (like `isLoading`, `error`)
// and its actions (like the `login` function we defined).
const authStore = useAuthStore();

// WHAT: This is the function that runs when the form is submitted.
// WHY: We use an `async` function because the login process (API call) is asynchronous.
// The `await` keyword pauses the function until the `authStore.login` action is complete.
const handleLogin = async () => {
  try {
    await authStore.login({
      username: username.value,
      password: password.value,
    });
    // The login action in the store handles redirecting to the dashboard on success.
  } catch (error) {
    // The error is already set in the store, so we can just log it here
    // or show a specific UI notification if we want.
    console.error("Login failed in component:", error);
  }
};
</script>

<style scoped>
.login-view {
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
