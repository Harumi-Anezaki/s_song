import React, { useState } from 'react';
import { useAppStore } from '../store/appStore';
import { useDataStore } from '../store/dataStore';
import { parseYTDuration, formatDuration, calculateSimilarityScore, extractVersions } from '../utils/youtube';
import type { YTVideoResult, SimilarityCandidate } from '../types';
import { Search, AlertTriangle } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

const YouTubeSearch: React.FC = () => {
  const { youtubeApiKey, searchKeyword, setSearchKeyword } = useAppStore();
  const { songs, singers, addSinger, mergeToSong, excludedVideoIds, excludeYTVideos } = useDataStore();
  
  const [minViews, setMinViews] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SimilarityCandidate[]>([]);
  
  // Compare Modal State
  const [compareGroup, setCompareGroup] = useState<SimilarityCandidate[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedForMerge, setSelectedForMerge] = useState<Set<string>>(new Set());

  // Modeless Dialog State for row operations
  const [activeDialogRowId, setActiveDialogRowId] = useState<string | null>(null);
  
  const searchYouTube = async () => {
    if (!youtubeApiKey) {
      alert('設定画面からYouTube APIキーを入力してください。');
      return;
    }
    if (!searchKeyword.trim()) return;

    setIsLoading(true);
    try {
      // 1. Keyword register to Singer DB
      if (!singers.some(s => s.name === searchKeyword)) {
        addSinger({
          id: uuidv4(),
          name: searchKeyword,
          liking: '',
          singability: '',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        });
      }

      // 2. Fetch from YT API
      const searchRes = await fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&q=${encodeURIComponent(searchKeyword)}&type=video&key=${youtubeApiKey}`);
      const searchData = await searchRes.json();
      
      if (!searchData.items) {
        throw new Error(searchData.error?.message || '検索結果がありません');
      }

      const videoIds = searchData.items.map((item: any) => item.id.videoId).join(',');
      const vidRes = await fetch(`https://www.googleapis.com/youtube/v3/videos?part=contentDetails,statistics&id=${videoIds}&key=${youtubeApiKey}`);
      const vidData = await vidRes.json();

      let fetchedResults: YTVideoResult[] = [];

      vidData.items.forEach((item: any) => {
        const durationSeconds = parseYTDuration(item.contentDetails.duration);
        const views = parseInt(item.statistics.viewCount || '0');
        
        // Exclude < 1m or >= 8m
        if (durationSeconds < 60 || durationSeconds >= 480) return;
        
        // Min views filter
        if (minViews > 0) {
          if (minViews === 10000000 && views < 8000000) return;
          if (minViews === 100000000 && views < 80000000) return;
        }

        const snippet = searchData.items.find((si: any) => si.id.videoId === item.id).snippet;
        
        fetchedResults.push({
          id: item.id,
          title: snippet.title,
          url: `https://youtu.be/${item.id}`,
          views: views,
          publishedAt: snippet.publishedAt.split('T')[0],
          channelTitle: snippet.channelTitle,
          durationFormatted: formatDuration(durationSeconds),
          durationSeconds: durationSeconds,
        });
      });

      // 3. Process Similarity
      processSimilarity(fetchedResults, searchKeyword);
      
    } catch (err: any) {
      alert(`検索エラー: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const processSimilarity = (newResults: YTVideoResult[], keyword: string) => {
    // Collect all videos to compare (new results + existing in Song DB)
    // Actually prompt says: "検索時に1分未満または8分以上として除外した動画は、比較対象に含めない" - already handled
    const existingVideos: YTVideoResult[] = songs.flatMap(s => 
      s.id.split(',').map(vidId => ({
        id: vidId,
        title: s.title, // Approximation for similarity
        url: `https://youtu.be/${vidId}`,
        views: 0, // Not strictly needed for similarity score
        publishedAt: '',
        channelTitle: '', // We don't save this in Song DB, so score will just miss channel points
        durationFormatted: '',
        durationSeconds: 0, // Missing duration points
      }))
    );

    const allComparePool = [...newResults, ...existingVideos];
    
    // Simple grouping logic
    let groupIdCounter = 1;
    const candidates: SimilarityCandidate[] = newResults.map(r => {
      const v = extractVersions(r.title);
      return {
        ...r,
        similarityScore: 0,
        similarityReasons: [],
        isWarning: false,
        isCover: v.isCover,
        isLive: v.isLive,
        isRemix: v.isRemix,
        groupId: '',
        isAlreadyMerged: songs.some(s => s.id.includes(r.id))
      };
    });

    for (let i = 0; i < candidates.length; i++) {
      if (candidates[i].groupId !== '') continue;
      
      let foundSimilar = false;
      for (let j = 0; j < allComparePool.length; j++) {
        if (candidates[i].id === allComparePool[j].id) continue;
        
        const sim = calculateSimilarityScore(candidates[i], allComparePool[j], keyword);
        if (sim.score >= 70) {
          if (!foundSimilar) {
            candidates[i].groupId = `g${groupIdCounter}`;
            foundSimilar = true;
          }
          // If the matching one is in our new candidates, group it
          const matchIdx = candidates.findIndex(c => c.id === allComparePool[j].id);
          if (matchIdx !== -1) {
            candidates[matchIdx].groupId = `g${groupIdCounter}`;
            candidates[matchIdx].similarityScore = sim.score;
            candidates[matchIdx].similarityReasons = sim.reasons;
            candidates[matchIdx].isWarning = sim.isWarning;
          }
        }
      }
      if (foundSimilar) groupIdCounter++;
    }

    setResults(candidates);
  };

  const openCompareModal = (groupId: string) => {
    const group = results.filter(r => r.groupId === groupId);
    setCompareGroup(group);
    setSelectedForMerge(new Set());
    setIsModalOpen(true);
  };

  const handleMergeSelection = (id: string) => {
    const next = new Set(selectedForMerge);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedForMerge(next);
  };

  const commitMerge = () => {
    if (selectedForMerge.size < 2) return;
    const itemsToMerge = compareGroup.filter(c => selectedForMerge.has(c.id));
    
    // Check warnings
    let warningTriggered = false;
    let minScore = 100;
    itemsToMerge.forEach(i => {
      if (i.isCover || i.isRemix || i.isAlreadyMerged) warningTriggered = true;
      if (i.similarityScore < 85 && i.similarityScore > 0) warningTriggered = true;
      if (i.similarityScore < minScore && i.similarityScore > 0) minScore = i.similarityScore;
    });

    const hasLive = itemsToMerge.some(i => i.isLive);
    const hasNormal = itemsToMerge.some(i => !i.isLive);
    if (hasLive && hasNormal) warningTriggered = true;
    
    const times = itemsToMerge.map(i => i.durationSeconds);
    const maxDiff = Math.max(...times) - Math.min(...times);
    if (maxDiff >= 60) warningTriggered = true;

    if (warningTriggered) {
      if (!window.confirm("誤統合の可能性を示す警告があります。本当に統合しますか？")) {
        return;
      }
    }

    mergeToSong(null, itemsToMerge);
    setIsModalOpen(false);
    alert('曲DBに新規統合データとして登録しました。タイトルを入力してください。');
  };

  const handleRowExclude = (id: string) => {
    excludeYTVideos([id], searchKeyword);
    setActiveDialogRowId(null);
  };

  const handleRowUpdate = (vid: SimilarityCandidate) => {
    mergeToSong(null, [vid]);
    setActiveDialogRowId(null);
    alert('曲DBに登録しました。');
  };

  const isExcluded = (id: string) => {
    const excludedList = excludedVideoIds[searchKeyword] || [];
    return excludedList.includes(id);
  };

  return (
    <div className="youtube-search-container">
      <header className="content-header">
        <h2 className="content-title">YouTube検索</h2>
        <div className="flex-row">
          <input 
            type="text" 
            placeholder="検索キーワード（歌手名など）" 
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            style={{ width: '250px' }}
          />
          <select value={minViews} onChange={(e) => setMinViews(Number(e.target.value))}>
            <option value={0}>最低再生回数: 制限なし</option>
            <option value={10000000}>最低再生回数: 1000万回</option>
            <option value={100000000}>最低再生回数: 1億回</option>
          </select>
          <button className="btn btn-primary" onClick={searchYouTube} disabled={isLoading}>
            <Search size={16} /> 検索
          </button>
        </div>
      </header>

      <div className="content-body" style={{ padding: '0' }}>
        {isLoading ? (
          <div style={{ padding: '20px', textAlign: 'center' }}>検索中...</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead style={{ backgroundColor: 'var(--bg-surface)', borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
              <tr>
                <th style={{ padding: '12px' }}>操作</th>
                <th style={{ padding: '12px' }}>タイトル</th>
                <th style={{ padding: '12px' }}>再生数</th>
                <th style={{ padding: '12px' }}>投稿日</th>
                <th style={{ padding: '12px' }}>アカウント</th>
                <th style={{ padding: '12px' }}>時間</th>
                <th style={{ padding: '12px' }}>類似</th>
              </tr>
            </thead>
            <tbody>
              {results.map((res) => {
                const excluded = isExcluded(res.id);
                const merged = res.isAlreadyMerged;
                let bgStyle = {};
                if (excluded) bgStyle = { backgroundColor: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)' };
                else if (merged) bgStyle = { backgroundColor: 'var(--bg-surface-highlight)' }; // 淡い水色
                else if (res.groupId === 'g1') bgStyle = { backgroundColor: 'var(--group-1)' };
                else if (res.groupId === 'g2') bgStyle = { backgroundColor: 'var(--group-2)' };
                else if (res.groupId === 'g3') bgStyle = { backgroundColor: 'var(--group-3)' };

                return (
                  <tr key={res.id} style={{ borderBottom: '1px solid var(--border-color)', position: 'relative', ...bgStyle }}>
                    <td style={{ padding: '12px' }}>
                      <button className="btn btn-sm btn-secondary" onClick={() => setActiveDialogRowId(res.id)}>操作</button>
                      
                      {activeDialogRowId === res.id && (
                        <div style={{ position: 'absolute', zIndex: 10, backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-color)', padding: '10px', borderRadius: '4px', boxShadow: 'var(--shadow-md)', display: 'flex', gap: '8px', top: '100%' }}>
                          <button className="btn btn-sm btn-primary" onClick={() => handleRowUpdate(res)} disabled={excluded}>登録・更新</button>
                          <button className="btn btn-sm btn-danger" onClick={() => handleRowExclude(res.id)}>除外</button>
                          <button className="btn btn-sm btn-secondary" onClick={() => setActiveDialogRowId(null)}>閉じる</button>
                        </div>
                      )}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <a href={res.url} target="_blank" rel="noreferrer" style={{ color: 'var(--primary-color)', textDecoration: 'none' }}>
                        {res.title}
                      </a>
                    </td>
                    <td style={{ padding: '12px' }}>{res.views.toLocaleString()}</td>
                    <td style={{ padding: '12px' }}>{res.publishedAt}</td>
                    <td style={{ padding: '12px' }}>{res.channelTitle}</td>
                    <td style={{ padding: '12px' }}>{res.durationFormatted}</td>
                    <td style={{ padding: '12px' }}>
                      {res.groupId ? (
                        <div style={{ cursor: 'pointer', color: 'var(--primary-hover)' }} onClick={() => openCompareModal(res.groupId)}>
                          {res.similarityScore >= 85 ? '可能性高' : '可能性あり'} ({res.similarityScore}点)
                          {res.isWarning && <AlertTriangle size={14} style={{ color: 'var(--danger-color)', marginLeft: '4px' }} />}
                        </div>
                      ) : '候補なし'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Compare Modal */}
      {isModalOpen && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ backgroundColor: 'var(--bg-base)', width: '90%', maxWidth: '1000px', maxHeight: '90vh', overflowY: 'auto', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
            <div style={{ padding: '20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between' }}>
              <h3>類似候補の比較・統合</h3>
              <button className="btn btn-primary" disabled={selectedForMerge.size < 2} onClick={commitMerge}>
                選択した動画を統合
              </button>
            </div>
            <div style={{ padding: '20px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <th>対象</th>
                    <th>タイトル</th>
                    <th>再生数</th>
                    <th>時間</th>
                    <th>類似度</th>
                    <th>注意事項</th>
                  </tr>
                </thead>
                <tbody>
                  {compareGroup.map(c => (
                    <tr key={c.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <input type="checkbox" checked={selectedForMerge.has(c.id)} onChange={() => handleMergeSelection(c.id)} />
                      </td>
                      <td style={{ padding: '12px' }}><a href={c.url} target="_blank" rel="noreferrer">{c.title}</a><br/><small>{c.channelTitle}</small></td>
                      <td style={{ padding: '12px' }}>{c.views.toLocaleString()}</td>
                      <td style={{ padding: '12px' }}>{c.durationFormatted}</td>
                      <td style={{ padding: '12px' }}>
                        {c.similarityScore}点<br/>
                        <small style={{ color: 'var(--text-muted)' }}>{c.similarityReasons.join(', ')}</small>
                      </td>
                      <td style={{ padding: '12px', color: 'var(--danger-color)' }}>
                        {c.isCover && <div>Cover</div>}
                        {c.isLive && <div>Live</div>}
                        {c.isRemix && <div>Remix</div>}
                        {c.isAlreadyMerged && <div>統合済</div>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div style={{ padding: '20px', borderTop: '1px solid var(--border-color)', textAlign: 'right' }}>
              <button className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>閉じる</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default YouTubeSearch;
