import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ViewSetting } from '../types';

interface ViewState {
  views: ViewSetting[];
  lastOpenedViewId: string | null;
  
  // Actions
  addView: (view: ViewSetting) => void;
  updateView: (id: string, updates: Partial<ViewSetting>) => void;
  deleteView: (id: string) => void;
  setLastOpenedViewId: (id: string) => void;
  reorderViews: (sourceIndex: number, destIndex: number) => void;
}

export const useViewStore = create<ViewState>()(
  persist(
    (set) => ({
      views: [],
      lastOpenedViewId: null,
      
      addView: (view) => set((state) => ({ views: [...state.views, view] })),
      updateView: (id, updates) =>
        set((state) => ({
          views: state.views.map((v) => (v.id === id ? { ...v, ...updates } : v)),
        })),
      deleteView: (id) =>
        set((state) => ({
          views: state.views.filter((v) => v.id !== id),
        })),
      setLastOpenedViewId: (id) => set({ lastOpenedViewId: id }),
      reorderViews: (sourceIndex, destIndex) =>
        set((state) => {
          const newViews = Array.from(state.views);
          const [removed] = newViews.splice(sourceIndex, 1);
          newViews.splice(destIndex, 0, removed);
          return { views: newViews };
        }),
    }),
    {
      name: 'youtube-song-manager-views',
    }
  )
);
