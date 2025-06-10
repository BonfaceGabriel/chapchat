import { defineStore } from "pinia";
import apiClient from "@/services/api"; // Our configured Axios instance
import router from "@/router"; // Import router for navigation

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: localStorage.getItem("accessToken") || null,
    refreshToken: localStorage.getItem("refreshToken") || null,
    user: JSON.parse(localStorage.getItem("user")) || null, // Basic user info
    isLoading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    currentUser: (state) => state.user,
  },
  actions: {
    async login(credentials) {
      this.isLoading = true;
      this.error = null;
      try {
        // Note: Django's /api/token/ endpoint expects form data, not JSON by default
        // We might need to adjust Axios or the Django endpoint if issues arise.
        // For now, let's assume it can handle JSON or we'll adjust.
        // If it strictly needs form-data:
        // const formData = new URLSearchParams();
        // formData.append('username', credentials.username);
        // formData.append('password', credentials.password);
        // const response = await apiClient.post('/token/', formData, {
        //   headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        // });

        const response = await apiClient.post("/token/", credentials); // Assumes JSON for now

        this.accessToken = response.data.access;
        this.refreshToken = response.data.refresh;
        // You might want to fetch user details in a separate call after login
        // or if /api/token/ can return user details, use that.
        // For simplicity, we'll assume no user details from /token/ endpoint.
        // We'll fetch profile later.
        localStorage.setItem("accessToken", response.data.access);
        localStorage.setItem("refreshToken", response.data.refresh);

        // Fetch user profile after successful login to get user details
        await this.fetchUserProfile();

        router.push("/dashboard"); // Navigate to dashboard after login
      } catch (err) {
        this.error =
          err.response?.data?.detail || err.message || "Login failed";
        console.error("Login error:", err.response || err);
        // Clear any stale tokens on login failure
        this.logoutAction();
        throw err; // Re-throw to be caught by component
      } finally {
        this.isLoading = false;
      }
    },

    async register(userData) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.post("/accounts/register/", userData);
        // After successful registration, you could automatically log them in
        // or prompt them to log in. We decided on separate login for now.
        console.log("Registration successful:", response.data);
        // Optionally store some part of response.data.user if needed immediately,
        // but they will login next to get tokens and full user context.
        return response.data; // Return data to the component
      } catch (err) {
        this.error = err.response?.data || { message: "Registration failed" };
        console.error("Registration error:", err.response?.data || err.message);
        throw err; // Re-throw
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUserProfile() {
      if (!this.accessToken) return; // No token, no profile fetch
      this.isLoading = true;
      try {
        const response = await apiClient.get("/seller/profile/"); // Or your actual profile endpoint
        this.user = {
          // Store relevant parts of the profile
          // id: response.data.user_id, // Assuming your profile serializer returns user_id or similar
          username: response.data.username,
          email: response.data.email,
          company_name: response.data.company_name,
          // Add other details you want readily available
        };
        localStorage.setItem("user", JSON.stringify(this.user));
      } catch (error) {
        console.error("Failed to fetch user profile:", error);
        // Could be due to expired token, handle 401 if not handled by interceptor
        if (error.response && error.response.status === 401) {
          // Potentially try to refresh token here or logout
          this.logout(); // Simple logout on profile fetch failure for now
        }
        this.error = "Failed to fetch profile";
      } finally {
        this.isLoading = false;
      }
    },

    // This is the action components will call
    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");
      // Optionally, call a backend logout endpoint if you have one
      // (e.g., to blacklist refresh token for simplejwt-blacklist)
      router.push("/login");
    },
    // Internal action, might not be needed if logout clears everything
    logoutAction() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");
    },

    // Token refresh action (more advanced, implement later if needed)
    // async refreshTokenAction() { ... }

    // Action to initialize store from localStorage (e.g., on app load)
    // Pinia does this for state with localStorage.getItem directly.
    // We can add a check action if user data is valid, etc.
    async checkAuth() {
      if (this.accessToken) {
        // Optionally verify token with backend or just assume it's good until an API call fails
        // For now, if token exists, try to fetch profile to "validate" the session
        if (!this.user) {
          // Fetch profile if user data isn't already loaded
          await this.fetchUserProfile();
        }
      }
    },
  },
});
