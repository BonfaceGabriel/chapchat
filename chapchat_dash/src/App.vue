<template>
  <div id="app-container">
    <header>
      <!-- You can put a global navigation bar here if you want -->
      <nav v-if="!isAuthenticated">
        <router-link to="/">Home</router-link> |
        <router-link to="/login">Login</router-link> |
        <router-link to="/register">Register</router-link>
      </nav>
    </header>
    <main>
      <!-- Top-level routes will be rendered here -->
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
// A computed property will automatically update when the store's state changes.
const isAuthenticated = computed(() => authStore.isAuthenticated);

onMounted(() => {
  // This will try to fetch the user profile if a token exists,
  // effectively validating the session and populating the user state.
  authStore.checkAuth();
});
</script>

<style>
/* Global styles for your entire app can go here */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
/* ... other global styles ... */
</style>
