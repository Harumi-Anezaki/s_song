import React, { useState } from 'react';
import { useDataStore } from '../store/dataStore';
import { useAppStore } from '../store/appStore';
import DataTable from './DataTable'; // We will create this next
import { v4 as uuidv4 } from 'uuid';

const MainDB: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'songs' | 'singers'>('songs');
  const { songs, singers, addSong, addSinger } = useDataStore();
  const { setCurrentRoute, setSearchKeyword } = useAppStore();

  const handleAddNew = () => {
    const now = new Date().toISOString();
    if (activeTab === 'songs') {
      addSong({
        id: uuidv4(),
        title: '',
        mainSingerId: '',
        subSingerIds: [],
        location: '',
        genre: '',
        use: '',
        eval1: '',
        urls: [],
        releaseDate: '',
        views: 0,
        createdAt: now,
        updatedAt: now,
        excludedFromYTSearch: false
      });
    } else {
      addSinger({
        id: uuidv4(),
        name: '',
        liking: '',
        singability: '',
        createdAt: now,
        updatedAt: now
      });
    }
  };

  const handleSingerUpdate = (singerName: string) => {
    setSearchKeyword(singerName);
    setCurrentRoute('search');
  };

  return (
    <div className="main-db-container" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <header className="content-header">
        <h2 className="content-title">DB原本</h2>
        <div className="flex-row">
          <button className="btn btn-primary" onClick={handleAddNew}>
            新規追加
          </button>
        </div>
      </header>
      
      <div style={{ padding: '10px 30px', borderBottom: '1px solid var(--border-color)', display: 'flex', gap: '20px' }}>
        <div 
          style={{ cursor: 'pointer', paddingBottom: '10px', borderBottom: activeTab === 'songs' ? '2px solid var(--primary-color)' : 'none', color: activeTab === 'songs' ? 'var(--text-primary)' : 'var(--text-muted)' }}
          onClick={() => setActiveTab('songs')}
        >
          曲DB
        </div>
        <div 
          style={{ cursor: 'pointer', paddingBottom: '10px', borderBottom: activeTab === 'singers' ? '2px solid var(--primary-color)' : 'none', color: activeTab === 'singers' ? 'var(--text-primary)' : 'var(--text-muted)' }}
          onClick={() => setActiveTab('singers')}
        >
          歌手DB
        </div>
      </div>

      <div className="content-body" style={{ padding: '0', overflowX: 'auto' }}>
        {activeTab === 'songs' ? (
          <DataTable type="songs" data={songs} />
        ) : (
          <DataTable type="singers" data={singers} onSingerUpdate={handleSingerUpdate} />
        )}
      </div>
    </div>
  );
};

export default MainDB;
