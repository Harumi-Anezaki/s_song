import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type AppRoute = 'search' | 'linked-db' | 'main-db' | 'settings';

interface AppState {
  youtubeApiKey: string;
  setYoutubeApiKey: (key: string) => void;
  currentRoute: AppRoute;
  setCurrentRoute: (route: AppRoute) => void;
  
  // For cross-component navigation like Singer DB "Update" button
  searchKeyword: string;
  setSearchKeyword: (keyword: string) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      youtubeApiKey: '',
      setYoutubeApiKey: (key) => set({ youtubeApiKey: key }),
      currentRoute: 'search',
      setCurrentRoute: (route) => set({ currentRoute: route }),
      searchKeyword: '',
      setSearchKeyword: (keyword) => set({ searchKeyword: keyword }),
    }),
    {
      name: 'youtube-song-manager-app',
    }
  )
);
