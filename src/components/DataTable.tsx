import React, { useState } from 'react';
import { useDataStore } from '../store/dataStore';
import { hydrateSong, hydrateSinger } from '../utils/dataStoreUtils';
import { Trash2, RefreshCw } from 'lucide-react';
import type { Song } from '../types';

interface DataTableProps {
  type: 'songs' | 'singers';
  data: any[];
  onSingerUpdate?: (name: string) => void;
  // Options for views (Linked DB)
  visibleColumns?: string[];
  wrapText?: boolean;
}

const DataTable: React.FC<DataTableProps> = ({ type, data, onSingerUpdate, visibleColumns, wrapText }) => {
  const { songs, singers, updateSong, deleteSong, updateSinger, deleteSinger } = useDataStore();
  
  const [editingCell, setEditingCell] = useState<{ id: string, field: string } | null>(null);
  const [editValue, setEditValue] = useState<string>('');

  // Hydrate Data
  const hydratedData = data.map(row => 
    type === 'songs' ? hydrateSong(row, singers, songs) : hydrateSinger(row, songs)
  );

  // Column definitions based on type (Simplified version of draggable columns for Phase 3)
  const allSongColumns = [
    { key: 'title', label: '曲名', type: 'text', editable: true },
    { key: 'id', label: 'ID', type: 'text', editable: false },
    { key: 'mainSingerId', label: 'メイン歌手', type: 'relation-singer', editable: false },
    { key: 'subSingerIds', label: 'サブ歌手', type: 'relation-singer-multi', editable: true },
    { key: 'location', label: '場所', type: 'select', options: ['日本', '海外'], editable: true },
    { key: 'genre', label: 'ジャンル', type: 'select', options: ['沖縄', 'HIPHOP', 'アイドル'], editable: true },
    { key: 'use', label: '用途', type: 'select', options: ['盛上', '高音練習', 'おはこ'], editable: true },
    { key: 'eval1', label: '評価1', type: 'select', options: ['排除'], editable: true },
    { key: 'urls', label: 'URL', type: 'urls', editable: false },
    { key: 'releaseDate', label: 'リリース日', type: 'date', editable: true },
    { key: 'views', label: '再生数', type: 'number', editable: false },
    { key: 'calcViewsPerDay', label: '回/日', type: 'number', editable: false },
    { key: 'calcTop70Views', label: '同アーティストの再生数の上位70%', type: 'number', editable: false },
    { key: 'calcTop70ViewsPerDay', label: '同アーティストの回/日の上位70%', type: 'number', editable: false },
    { key: 'calcSingerLiking', label: '歌手の好き度', type: 'number', editable: false },
    { key: 'calcTrend', label: '流行関数', type: 'text', editable: false },
    { key: 'createdAt', label: '作成日時', type: 'date-time', editable: false },
    { key: 'updatedAt', label: '更新日時', type: 'date-time', editable: false },
  ];

  const allSingerColumns = [
    { key: 'actions', label: '操作', type: 'actions', editable: false },
    { key: 'name', label: '歌手名', type: 'text', editable: true },
    { key: 'liking', label: '好き度', type: 'number', editable: true },
    { key: 'singability', label: '歌いやすさ', type: 'number', editable: true },
    { key: 'calcMainSongs', label: 'メイン曲', type: 'relation-song-multi', editable: false },
    { key: 'calcSubSongs', label: 'サブ曲', type: 'relation-song-multi', editable: true },
    { key: 'calcSongViews', label: '曲の再生数', type: 'number-array', editable: false },
    { key: 'calcSongViewsPerDay', label: '曲の回/日', type: 'number-array', editable: false },
    { key: 'calcTop70Views', label: '再生数_上位70%', type: 'number', editable: false },
    { key: 'calcTop70ViewsPerDay', label: '回/日_上位70%', type: 'number', editable: false },
    { key: 'createdAt', label: '作成日時', type: 'date-time', editable: false },
    { key: 'updatedAt', label: '更新日時', type: 'date-time', editable: false },
  ];

  const cols = type === 'songs' ? allSongColumns : allSingerColumns;
  const activeCols = visibleColumns ? cols.filter(c => visibleColumns.includes(c.key)) : cols;

  const handleEditClick = (row: any, col: any) => {
    if (!col.editable) return;
    setEditingCell({ id: row.id, field: col.key });
    
    // Convert array values to comma string for simple text editing if needed
    if (col.type === 'relation-singer-multi' || col.type === 'relation-song-multi') {
      setEditValue(row[col.key]?.join(',') || '');
    } else {
      setEditValue(row[col.key] || '');
    }
  };

  const handleSaveEdit = (rowId: string, col: any) => {
    let parsedValue: any = editValue;
    if (col.type === 'number') parsedValue = Number(editValue) || '';
    if (col.type.includes('multi')) parsedValue = editValue.split(',').map(s => s.trim()).filter(s => s);

    if (type === 'songs') updateSong(rowId, { [col.key]: parsedValue });
    else updateSinger(rowId, { [col.key]: parsedValue });
    
    setEditingCell(null);
  };

  const handleDelete = (id: string) => {
    if (window.confirm('本当に削除しますか？')) {
      if (type === 'songs') deleteSong(id);
      else deleteSinger(id);
    }
  };

  const renderCellContent = (row: any, col: any) => {
    if (editingCell?.id === row.id && editingCell?.field === col.key) {
      if (col.type === 'select') {
        return (
          <select 
            value={editValue} 
            onChange={e => setEditValue(e.target.value)}
            onBlur={() => handleSaveEdit(row.id, col)}
            autoFocus
          >
            <option value=""></option>
            {col.options.map((opt: string) => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        );
      }
      return (
        <input
          type={col.type === 'number' ? 'number' : 'text'}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={() => handleSaveEdit(row.id, col)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSaveEdit(row.id, col); }}
          autoFocus
          style={{ width: '100%', padding: '4px', border: '1px solid var(--primary-color)' }}
        />
      );
    }

    // Display rendering
    if (col.key === 'actions' && type === 'singers') {
      return (
        <button 
          className="btn btn-sm btn-primary" 
          onClick={() => onSingerUpdate && onSingerUpdate(row.name)}
          style={{ padding: '2px 8px' }}
        >
          <RefreshCw size={12} /> 更新
        </button>
      );
    }

    if (col.type === 'urls') {
      if (!row[col.key] || row[col.key].length === 0) return '';
      return row[col.key].map((url: string, idx: number) => {
        // "動画タイトルの冒頭10文字" 
        // We might not have the title per URL saved separately, so just show a generic link or the row title
        const display = row.title ? row.title.substring(0, 10) : url.substring(0, 10);
        return <div key={idx}><a href={url} target="_blank" rel="noreferrer" style={{ color: 'var(--primary-color)' }}>{display}...</a></div>
      });
    }

    if (col.type === 'relation-singer') {
      const singer = singers.find(s => s.id === row[col.key]);
      return singer ? singer.name : '';
    }

    if (col.type === 'relation-singer-multi') {
      const ids = row[col.key] || [];
      return ids.map((id: string) => singers.find(s => s.id === id)?.name || id).join(', ');
    }

    if (col.type === 'relation-song-multi') {
      const sngs = row[col.key] || [];
      return sngs.map((s: Song) => s.title).join(', ');
    }
    
    if (col.type === 'number') {
      return typeof row[col.key] === 'number' ? Math.round(row[col.key]).toLocaleString() : '';
    }

    if (col.type === 'date-time') {
      return row[col.key] ? new Date(row[col.key]).toLocaleString() : '';
    }

    return String(row[col.key] || '');
  };

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', minWidth: '800px' }}>
      <thead style={{ backgroundColor: 'var(--bg-surface)', borderBottom: '2px solid var(--border-color)', position: 'sticky', top: 0, zIndex: 10 }}>
        <tr>
          {activeCols.map(col => (
            <th key={col.key} style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 600, color: 'var(--text-secondary)', whiteSpace: wrapText ? 'normal' : 'nowrap' }}>
              {col.label}
            </th>
          ))}
          <th style={{ padding: '10px 12px', width: '50px' }}></th>
        </tr>
      </thead>
      <tbody>
        {hydratedData.map((row) => (
          <tr key={row.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background 0.2s' }}>
            {activeCols.map(col => (
              <td 
                key={col.key} 
                style={{ padding: '10px 12px', cursor: col.editable ? 'cell' : 'default', backgroundColor: editingCell?.id === row.id && editingCell?.field === col.key ? 'var(--bg-surface-hover)' : 'transparent', whiteSpace: wrapText ? 'pre-wrap' : 'nowrap' }}
                onDoubleClick={() => handleEditClick(row, col)}
              >
                {renderCellContent(row, col)}
              </td>
            ))}
            <td style={{ padding: '10px 12px', textAlign: 'right' }}>
              <button className="btn btn-sm" style={{ backgroundColor: 'transparent', color: 'var(--danger-color)', padding: '4px' }} onClick={() => handleDelete(row.id)}>
                <Trash2 size={14} />
              </button>
            </td>
          </tr>
        ))}
        {hydratedData.length === 0 && (
          <tr>
            <td colSpan={activeCols.length + 1} style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)' }}>
              データがありません
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
};

export default DataTable;
