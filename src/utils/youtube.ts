import type { YTVideoResult } from '../types';

/**
 * 2.3 類似判定
 * タイトルの正規化
 */
export const normalizeTitle = (title: string, searchKeyword: string): string => {
  let normalized = title.toLowerCase();

  // 全角英数字を半角に変換
  normalized = normalized.replace(/[Ａ-Ｚａ-ｚ０-９]/g, (s) => String.fromCharCode(s.charCodeAt(0) - 0xfee0));

  // 記号、括弧を除去 (Fullwidth and halfwidth)
  normalized = normalized.replace(/[()[\]{}<>《》「」『』【】（）〔〕［］]/g, ' ');
  normalized = normalized.replace(/[-_/:,.;~!?|@#$%^&*=+~〜ー]/g, ' ');

  // 検索キーワードを除去
  if (searchKeyword) {
    const keywordNormalized = searchKeyword.toLowerCase().replace(/[Ａ-Ｚａ-ｚ０-９]/g, (s) => String.fromCharCode(s.charCodeAt(0) - 0xfee0));
    normalized = normalized.replace(new RegExp(keywordNormalized, 'gi'), ' ');
  }

  // 一般的な表記を除去
  const commonTerms = [
    'official', 'music video', 'mv', 'pv', 'lyrics', '歌詞付き', 'full', 'hd', '4k', 'audio',
    'official video', 'official audio', 'lyric video'
  ];
  commonTerms.forEach(term => {
    normalized = normalized.replace(new RegExp(`\\b${term}\\b`, 'gi'), ' ');
  });

  // 連続する空白を除去
  normalized = normalized.replace(/\s+/g, ' ').trim();

  return normalized;
};

/**
 * 別バージョンの検出
 */
export const extractVersions = (title: string) => {
  const t = title.toLowerCase();
  return {
    isLive: t.includes('live'),
    isCover: t.includes('cover') || t.includes('歌ってみた'),
    isRemix: t.includes('remix') || t.includes('sped up') || t.includes('nightcore'),
    isAcoustic: t.includes('acoustic'),
    isInst: t.includes('instrumental') || t.includes('karaoke') || t.includes('カラオケ'),
    isShort: t.includes('short ver'),
    isFirstTake: t.includes('the first take'),
  };
};

/**
 * 類似度の計算 (2-gram / Bi-gram Jaccard Index)
 */
const getBigrams = (str: string) => {
  const bigrams = new Set<string>();
  for (let i = 0; i < str.length - 1; i++) {
    bigrams.add(str.slice(i, i + 2));
  }
  return bigrams;
};

const calculateTextSimilarity = (str1: string, str2: string) => {
  if (str1 === str2) return 1.0;
  if (str1.length < 2 || str2.length < 2) return 0.0;
  
  const bg1 = getBigrams(str1);
  const bg2 = getBigrams(str2);
  
  let intersection = 0;
  for (let bg of bg1) {
    if (bg2.has(bg)) intersection++;
  }
  
  const union = bg1.size + bg2.size - intersection;
  return intersection / union;
};

/**
 * 類似度を0〜100点で計算する
 */
export const calculateSimilarityScore = (
  vid1: YTVideoResult, 
  vid2: YTVideoResult, 
  searchKeyword: string
): { score: number, reasons: string[], isWarning: boolean } => {
  let score = 0;
  const reasons: string[] = [];
  let isWarning = false;

  const normTitle1 = normalizeTitle(vid1.title, searchKeyword);
  const normTitle2 = normalizeTitle(vid2.title, searchKeyword);

  // 1. 正規化後のタイトルの類似度 (Max 60)
  const textSim = calculateTextSimilarity(normTitle1, normTitle2);
  const textScore = textSim * 60;
  score += textScore;
  if (textSim > 0.8) reasons.push('タイトルが非常に似ている');

  // 2. 検索キーワードまたは歌手名の一致 (Max 15)
  // Both videos found under the same keyword search technically implicitly matches, 
  // but if keyword is in title, give points.
  const hasKeyword1 = vid1.title.toLowerCase().includes(searchKeyword.toLowerCase());
  const hasKeyword2 = vid2.title.toLowerCase().includes(searchKeyword.toLowerCase());
  if (hasKeyword1 && hasKeyword2) {
    score += 15;
  }

  // 3. 動画時間の近さ (Max 15)
  const timeDiff = Math.abs(vid1.durationSeconds - vid2.durationSeconds);
  if (timeDiff <= 5) {
    score += 15;
    reasons.push('動画時間がほぼ一致');
  } else if (timeDiff <= 15) {
    score += 10;
  } else if (timeDiff >= 60) {
    isWarning = true; // 動画時間の差が60秒以上ある
  }

  // 4. チャンネル名の一致 (Max 10)
  if (vid1.channelTitle === vid2.channelTitle) {
    score += 10;
    reasons.push('チャンネル名が一致');
  }

  // 5. 別バージョン不一致 (20〜30点減点)
  const v1 = extractVersions(vid1.title);
  const v2 = extractVersions(vid2.title);
  
  let mismatchCount = 0;
  if (v1.isLive !== v2.isLive) { mismatchCount++; isWarning = true; }
  if (v1.isCover !== v2.isCover) { mismatchCount++; isWarning = true; }
  if (v1.isRemix !== v2.isRemix) { mismatchCount++; isWarning = true; }
  if (v1.isAcoustic !== v2.isAcoustic) mismatchCount++;
  if (v1.isInst !== v2.isInst) mismatchCount++;

  if (mismatchCount > 0) {
    score -= Math.min(30, mismatchCount * 15);
    reasons.push('別バージョン(Live/Cover等)の不一致');
  }

  return {
    score: Math.max(0, Math.round(score)),
    reasons,
    isWarning
  };
};

/**
 * Parses YT ISO 8601 duration (PT1M30S) to seconds
 */
export const parseYTDuration = (duration: string): number => {
  const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!match) return 0;
  const hours = parseInt(match[1] || '0');
  const minutes = parseInt(match[2] || '0');
  const seconds = parseInt(match[3] || '0');
  return hours * 3600 + minutes * 60 + seconds;
};

export const formatDuration = (seconds: number): string => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}分${s}秒`;
};
