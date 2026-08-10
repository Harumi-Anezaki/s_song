import type { Song, Singer } from '../types';

/**
 * DB Formulas & Rollups
 */

// 1. Calculate Views/Day for a song
export const calcSongViewsPerDay = (song: Song): number => {
  if (!song.releaseDate || song.views === undefined) return 0;
  const release = new Date(song.releaseDate).getTime();
  const now = new Date().getTime();
  const diffDays = Math.max(1, (now - release) / (1000 * 3600 * 24));
  return song.views / diffDays;
};

// 2. Singer: Get Top 70% Views
export const calcSingerTop70Views = (singerId: string, songs: Song[]): number | null => {
  const relatedSongs = songs.filter(s => s.mainSingerId === singerId || s.subSingerIds.includes(singerId));
  if (relatedSongs.length <= 5) return null; // prompt says length() <= 5 return ""
  
  const viewsList = relatedSongs.map(s => s.views).sort((a, b) => b - a); // reverse sort
  const count = Math.floor(viewsList.length * 0.7);
  if (count === 0) return null;
  return viewsList[count - 1]; // 0-indexed, so 70th percentile is at count-1
};

// 3. Singer: Get Top 70% Views/Day
export const calcSingerTop70ViewsPerDay = (singerId: string, songs: Song[]): number | null => {
  const relatedSongs = songs.filter(s => s.mainSingerId === singerId || s.subSingerIds.includes(singerId));
  if (relatedSongs.length <= 5) return null;
  
  const viewsPerDayList = relatedSongs.map(calcSongViewsPerDay).sort((a, b) => b - a);
  const count = Math.floor(viewsPerDayList.length * 0.7);
  if (count === 0) return null;
  return viewsPerDayList[count - 1];
};

// 4. Song: Trend calculation
export const calcSongTrend = (song: Song, top70Views: number | null, top70ViewsPerDay: number | null): string => {
  if (top70Views === null || top70ViewsPerDay === null) return '';
  const viewsPerDay = calcSongViewsPerDay(song);
  if (song.views < top70Views && viewsPerDay < top70ViewsPerDay) {
    return '時代遅れ';
  }
  return '';
};

// Full row hydration
export const hydrateSong = (song: Song, singers: Singer[], allSongs: Song[]) => {
  const mainSinger = singers.find(s => s.id === song.mainSingerId);
  const top70Views = mainSinger ? calcSingerTop70Views(mainSinger.id, allSongs) : null;
  const top70ViewsPerDay = mainSinger ? calcSingerTop70ViewsPerDay(mainSinger.id, allSongs) : null;

  return {
    ...song,
    calcViewsPerDay: calcSongViewsPerDay(song),
    calcTop70Views: top70Views,
    calcTop70ViewsPerDay: top70ViewsPerDay,
    calcTrend: calcSongTrend(song, top70Views, top70ViewsPerDay),
    calcSingerLiking: mainSinger?.liking || '',
  };
};

export const hydrateSinger = (singer: Singer, allSongs: Song[]) => {
  const relatedSongs = allSongs.filter(s => s.mainSingerId === singer.id || s.subSingerIds.includes(singer.id));
  
  return {
    ...singer,
    calcSongViews: relatedSongs.map(s => s.views),
    calcSongViewsPerDay: relatedSongs.map(calcSongViewsPerDay),
    calcTop70Views: calcSingerTop70Views(singer.id, allSongs),
    calcTop70ViewsPerDay: calcSingerTop70ViewsPerDay(singer.id, allSongs),
    calcMainSongs: allSongs.filter(s => s.mainSingerId === singer.id),
    calcSubSongs: allSongs.filter(s => s.subSingerIds.includes(singer.id)),
  };
};
