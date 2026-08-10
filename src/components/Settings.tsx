import React from 'react';
import { useAppStore } from '../store/appStore';

const AppSettings: React.FC = () => {
  const { youtubeApiKey, setYoutubeApiKey } = useAppStore();
  
  const handleExport = () => {
    const dataStore = JSON.parse(localStorage.getItem('youtube-song-manager-data') || '{}');
    const viewStore = JSON.parse(localStorage.getItem('youtube-song-manager-views') || '{}');
    const exportData = {
      dataStore,
      viewStore,
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `song-manager-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const importedData = JSON.parse(event.target?.result as string);
        if (importedData.dataStore) {
          localStorage.setItem('youtube-song-manager-data', JSON.stringify(importedData.dataStore));
        }
        if (importedData.viewStore) {
          localStorage.setItem('youtube-song-manager-views', JSON.stringify(importedData.viewStore));
        }
        alert('データをインポートしました。反映させるためにリロードします。');
        window.location.reload();
      } catch (err) {
        alert('インポートに失敗しました。');
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="settings-page">
      <header className="content-header">
        <h2 className="content-title">設定</h2>
      </header>
      <div className="content-body" style={{ maxWidth: '600px' }}>
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ marginBottom: '15px' }}>YouTube API キー</h3>
          <div className="flex-row">
            <input 
              type="text" 
              value={youtubeApiKey}
              onChange={(e) => setYoutubeApiKey(e.target.value)}
              placeholder="AIzaSyB..."
              style={{ flexGrow: 1 }}
            />
          </div>
          <p style={{ marginTop: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
            YouTube Data API v3のキーを入力してください。検索機能を使用するために必要です。
          </p>
        </div>

        <hr style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: '30px 0' }} />

        <div>
          <h3 style={{ marginBottom: '15px' }}>データ管理</h3>
          <div className="flex-row">
            <button className="btn btn-secondary" onClick={handleExport}>
              JSONエクスポート
            </button>
            <div style={{ position: 'relative', display: 'inline-block' }}>
              <button className="btn btn-secondary" onClick={() => document.getElementById('import-file')?.click()}>
                JSONインポート
              </button>
              <input 
                id="import-file" 
                type="file" 
                accept=".json"
                style={{ display: 'none' }} 
                onChange={handleImport}
              />
            </div>
          </div>
          <p style={{ marginTop: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
            すべてのDBデータとビュー設定をJSONファイルとして保存・復元します。
          </p>
        </div>
      </div>
    </div>
  );
};

export default AppSettings;
