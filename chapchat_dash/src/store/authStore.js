import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import apiClient from '../services/api';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      // --- STATE ---
      accessToken: null,
      refreshToken: null,
      user: null,
      isLoading: false,
      error: null,

      // --- ACTIONS ---
      login: async (username, password) => {
        set({ isLoading: true, error: null });
        try {
          const params = new URLSearchParams();
          params.append('username', username);
          params.append('password', password);

          const response = await apiClient.post('token/', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          });

          const { access, refresh } = response.data;
          set({ accessToken: access, refreshToken: refresh, isLoading: false });
          await get().fetchUserProfile();
        } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Invalid credentials. Please try again.';
          set({ error: errorMessage, isLoading: false });
          throw new Error(errorMessage);
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await apiClient.post('accounts/register/', userData);
          set({ isLoading: false }); 
          return response.data;
        } catch (err) {
          set({ isLoading: false });
          throw err;
        }
      },

      fetchUserProfile: async () => {
        if (!get().accessToken) return;
        set({ isLoading: true });
        try {
          const response = await apiClient.get('seller/profile/');
          set({ user: response.data, isLoading: false, error: null });
        } catch (err) {
          console.error('Failed to fetch user profile:', err);
          get().logout();
        }
      },

      // (+) NEW ACTION TO HANDLE TOKEN REFRESH
      refreshtoken: async () => {
        const currentRefreshToken = get().refreshToken;
        if (!currentRefreshToken) {
            console.log("No refresh token available.");
            return Promise.reject(new Error("No refresh token."));
        }

        try {
            const response = await apiClient.post('token/refresh/', {
                refresh: currentRefreshToken,
            });
            const { access } = response.data;
            set({ accessToken: access });
            return access; // Return the new access token
        } catch (err) {
            console.error("Failed to refresh token:", err);
            // If refresh fails, the user's session is invalid. Log them out.
            get().logout();
            return Promise.reject(err);
        }
      },

      logout: () => {
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          error: null,
        });
        // We navigate from the component that calls logout.
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        accessToken: state.accessToken, 
        refreshToken: state.refreshToken,
        user: state.user 
      }),
    }
  )
);