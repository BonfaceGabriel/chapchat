import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import apiClient from '../services/api'; // We still need it to make calls

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
          
          // Fetch profile after setting token
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
          set({ user: response.data, isLoading: false });
        } catch (err) {
          console.error('Failed to fetch user profile:', err);
          get().logout();
        }
      },

      logout: () => {
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          error: null,
        });
        // The interceptor will handle not adding the header anymore.
      },
    }),
    {
      name: 'auth-storage', // Name for the localStorage item
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
);