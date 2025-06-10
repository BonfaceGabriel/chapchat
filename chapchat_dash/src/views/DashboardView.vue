<template>
  <div class="dashboard-layout">
    <header>
      <h2>My Dashboard</h2>
      <nav>
        <router-link to="/dashboard/profile">My Profile</router-link> |
        <!-- (+) Add the new link -->
        <router-link to="/dashboard/products">Products</router-link>
      </nav>
      <button @click="handleLogout">Logout</button>
    </header>
    <main>
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
// WHAT: This is the new "Composition API" syntax for Vue 3, which is often cleaner.
// The `setup` attribute on the script tag enables it.
import { useAuthStore } from "@/stores/auth";

// WHY: We get access to our store and router instances so we can use them in our component logic.
const authStore = useAuthStore();

const handleLogout = () => {
  // Call the logout action from our Pinia store
  authStore.logout();
  // The logout action in the store already handles redirecting to the login page,
  // but we could also do it here: router.push('/login');
};
</script>

<style scoped>
.dashboard-layout header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f2f2f2;
  border-bottom: 1px solid #ddd;
}
.dashboard-layout nav a {
  margin-right: 1rem;
}
.dashboard-layout main {
  padding: 1rem;
}
</style>
