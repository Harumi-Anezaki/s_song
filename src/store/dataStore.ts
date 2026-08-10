import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Song, Singer } from '../types';

interface DataState {
  songs: Song[];
  singers: Singer[];
  addSong: (song: Song) => void;
  updateSong: (id: string, updates: Partial<Song>) => void;
  deleteSong: (id: string) => void;
  addSinger: (singer: Singer) => void;
  updateSinger: (id: string, updates: Partial<Singer>) => void;
  deleteSinger: (id: string) => void;
  // Merging YT results
  mergeToSong: (songId: string | null, ytVideos: any[]) => void;
  excludeYTVideos: (ytVideoIds: string[], keyword: string) => void;
  excludedVideoIds: Record<string, string[]>; // keyword -> videoIds
}

export const useDataStore = create<DataState>()(
  persist(
    (set) => ({
      songs: [],
      singers: [],
      excludedVideoIds: {},
      addSong: (song) => set((state) => ({ songs: [...state.songs, song] })),
      updateSong: (id, updates) =>
        set((state) => ({
          songs: state.songs.map((s) => (s.id === id || s.id.includes(id) ? { ...s, ...updates, updatedAt: new Date().toISOString() } : s)),
        })),
      deleteSong: (id) =>
        set((state) => ({
          songs: state.songs.filter((s) => s.id !== id && !s.id.includes(id)),
        })),
      addSinger: (singer) => set((state) => ({ singers: [...state.singers, singer] })),
      updateSinger: (id, updates) =>
        set((state) => ({
          singers: state.singers.map((s) => (s.id === id ? { ...s, ...updates, updatedAt: new Date().toISOString() } : s)),
        })),
      deleteSinger: (id) =>
        set((state) => ({
          singers: state.singers.filter((s) => s.id !== id),
        })),
      mergeToSong: (songId, ytVideos) =>
        set((state) => {
          // Implement merge logic here based on prompt "2.4 統合・除外"
          // If songId is provided, we merge into an existing song (which handles updates)
          // If songId is null, we are merging brand new search results into a new song template, but the prompt says:
          // Title: empty
          // URLs: multiple, separated by newline
          // Views: sum
          // Date: oldest
          // Account: empty
          // Time: empty
          // ID: multiple
          
          const combinedIds = ytVideos.map(v => v.id).join(',');
          const combinedUrls = ytVideos.map(v => v.url);
          const totalViews = ytVideos.reduce((sum, v) => sum + (v.views || 0), 0);
          
          // Find oldest date
          let oldestDate = ytVideos[0]?.publishedAt || new Date().toISOString().split('T')[0];
          ytVideos.forEach(v => {
            if (v.publishedAt && v.publishedAt < oldestDate) oldestDate = v.publishedAt;
          });

          const newSongTemplate: Song = {
            id: combinedIds,
            title: '',
            mainSingerId: '',
            subSingerIds: [],
            location: '',
            genre: '',
            use: '',
            eval1: '',
            urls: combinedUrls,
            releaseDate: oldestDate,
            views: totalViews,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            excludedFromYTSearch: false
          };

          if (songId) {
            // Update existing song
            return {
              songs: state.songs.map(s => {
                if (s.id === songId || s.id.includes(songId)) {
                  // Merge into existing
                  const mergedUrls = Array.from(new Set([...s.urls, ...combinedUrls]));
                  const mergedIds = Array.from(new Set([...s.id.split(','), ...ytVideos.map(v=>v.id)])).join(',');
                  return {
                    ...s,
                    id: mergedIds,
                    title: '', // Re-prompt user
                    urls: mergedUrls,
                    views: s.views + totalViews, // Wait, if the video already existed in the song, we shouldn't double count? The prompt implies selecting results from search. If user selects 2 videos, we sum. We will refine this later.
                    updatedAt: new Date().toISOString()
                  };
                }
                return s;
              })
            };
          } else {
            return { songs: [...state.songs, newSongTemplate] };
          }
        }),
      excludeYTVideos: (ytVideoIds, keyword) =>
        set((state) => {
          const prevExcluded = state.excludedVideoIds[keyword] || [];
          return {
            excludedVideoIds: {
              ...state.excludedVideoIds,
              [keyword]: Array.from(new Set([...prevExcluded, ...ytVideoIds]))
            }
          };
        }),
    }),
    {
      name: 'youtube-song-manager-data',
    }
  )
);
