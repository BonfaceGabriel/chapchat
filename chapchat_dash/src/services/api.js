import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- THE REQUEST INTERCEPTOR ---
apiClient.interceptors.request.use(
  (config) => {
    // This function runs for EVERY request.
    // It gets the MOST RECENT state from the store.
    const token = useAuthStore.getState().accessToken;
    
    // If a token exists, add it to the Authorization header.
    // If it's null, this block is skipped, and no Authorization header is sent.
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return config; // Proceed with the request, either with or without the header.
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;