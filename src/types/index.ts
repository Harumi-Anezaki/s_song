export type SongDBLocation = '日本' | '海外';
export type SongDBGenre = '沖縄' | 'HIPHOP' | 'アイドル';
export type SongDBUse = '盛上' | '高音練習' | 'おはこ';
export type SongDBEval1 = '排除';

export interface Song {
  id: string; // can be comma separated if merged, or just keep one ID and store others? The prompt says "ID: 複数保持する" (Keep multiple). We can store as an array.
  title: string;
  mainSingerId: string;
  subSingerIds: string[];
  location: SongDBLocation | '';
  genre: SongDBGenre | '';
  use: SongDBUse | '';
  eval1: SongDBEval1 | '';
  urls: string[];
  releaseDate: string; // YYYY-MM-DD
  views: number;
  createdAt: string;
  updatedAt: string;
  
  // Exclude logic
  excludedFromYTSearch: boolean;
}

export interface Singer {
  id: string;
  name: string;
  liking: number | '';
  singability: number | '';
  createdAt: string;
  updatedAt: string;
}

// YT Search Types
export interface YTVideoResult {
  id: string; // YT video id
  title: string;
  url: string;
  views: number;
  publishedAt: string; // YYYY-MM-DD
  channelTitle: string;
  durationFormatted: string; // ○分○秒
  durationSeconds: number; // For filtering
}

export interface SimilarityCandidate extends YTVideoResult {
  similarityScore: number;
  similarityReasons: string[];
  isWarning: boolean;
  isCover: boolean;
  isLive: boolean;
  isRemix: boolean;
  groupId: string;
  isAlreadyMerged: boolean; // if this ID is already in Song DB
}

// Linked DB View Settings
export interface FilterCondition {
  id: string;
  columnId: string;
  operator: 'equals' | 'contains' | 'greaterThan' | 'lessThan' | 'notEmpty' | 'isEmpty';
  value: any;
}

export interface SortCondition {
  id: string;
  columnId: string;
  direction: 'asc' | 'desc';
}

export interface ColumnSetting {
  id: string; // column key
  visible: boolean;
  width: number;
  order: number;
}

export interface ViewSetting {
  id: string;
  name: string;
  sourceDb: 'songs' | 'singers';
  columns: ColumnSetting[];
  filters: FilterCondition[];
  filterOperator: 'AND' | 'OR';
  sorts: SortCondition[];
  wrapText: boolean;
}
