import axios from "axios";
import { useAuthStore } from "../store/authStore";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// --- Request Interceptor ---
// This runs before every request.
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --- Response Interceptor ---
// This runs after a response is received.
apiClient.interceptors.response.use(
  (response) => response, // If response is successful, just return it.
  async (error) => {
    const originalRequest = error.config;
    const authStore = useAuthStore.getState();

    // Check if the error is a 401 Unauthorized AND it's not a request to the refresh token endpoint itself,
    // AND it's the first time we're retrying this request.
    if (
      error.response?.status === 401 &&
      originalRequest.url !== "token/refresh/" &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true; // Mark this request as having been retried.

      if (authStore.refreshToken) {
        try {
          console.log("Access token expired. Attempting to refresh...");
          // Call our new refreshToken action.
          const newAccessToken = await authStore.refreshtoken();

          // Update the header of the original failed request with the new token.
          originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;

          // Retry the original request.
          console.log(
            "Token refreshed successfully. Retrying original request."
          );
          return apiClient(originalRequest);
        } catch (refreshError) {
          console.log("Could not refresh token. Logging out.");
          // If refresh fails, the user is logged out.
          authStore.logout();
          // Redirect to login page
          window.location.href = "/login";
          return Promise.reject(refreshError);
        }
      } else {
        console.log("No refresh token available. Logging out.");
        authStore.logout();
        window.location.href = "/login";
      }
    }

    // For all other errors, just pass them along.
    return Promise.reject(error);
  }
);

export default apiClient;
