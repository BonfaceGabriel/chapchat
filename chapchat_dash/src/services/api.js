import axios from "axios";

// Get the base URL from an environment variable, defaulting to your local Django dev server
// We'll set VUE_APP_API_BASE_URL in a .env file for Vue
const API_BASE_URL =
  process.env.VUE_APP_API_BASE_URL || "http://127.0.0.1:8000/api/";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    // We will add the Authorization header dynamically when a token exists
  },
});

// Optional: Interceptor to add the JWT token to requests
// We'll set this up properly when we have the Pinia store for tokens
apiClient.interceptors.request.use(
  (config) => {
    // const token = store.state.auth.accessToken; // Example: get token from Pinia store
    const token = localStorage.getItem("accessToken"); // Or from localStorage directly for now
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Optional: Interceptor to handle 401 errors (e.g., token expired)
// This is more advanced, we can add it later. It might involve trying to refresh the token.
// apiClient.interceptors.response.use(
//   (response) => response,
//   async (error) => {
//     const originalRequest = error.config;
//     if (error.response.status === 401 && !originalRequest._retry) {
//       originalRequest._retry = true;
//       // try {
//       //   const newAccessToken = await store.dispatch('auth/refreshToken');
//       //   axios.defaults.headers.common['Authorization'] = 'Bearer ' + newAccessToken;
//       //   return apiClient(originalRequest);
//       // } catch (refreshError) {
//       //   store.dispatch('auth/logout'); // Logout if refresh fails
//       //   router.push('/login');
//       //   return Promise.reject(refreshError);
//       // }
//     }
//     return Promise.reject(error);
//   }
// );

export default apiClient;
