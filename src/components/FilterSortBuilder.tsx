import React from 'react';
import type { ViewSetting, FilterCondition, SortCondition } from '../types';
import { Plus, Trash2 } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

interface Props {
  view: ViewSetting;
  onUpdate: (updates: Partial<ViewSetting>) => void;
}

const FilterSortBuilder: React.FC<Props> = ({ view, onUpdate }) => {
  
  // Available Columns for this view's source
  const columns = view.sourceDb === 'songs' 
    ? [
        { id: 'title', label: '曲名' },
        { id: 'mainSingerId', label: 'メイン歌手' },
        { id: 'genre', label: 'ジャンル' },
        { id: 'use', label: '用途' },
        { id: 'views', label: '再生数' },
        { id: 'calcViewsPerDay', label: '回/日' },
      ]
    : [
        { id: 'name', label: '歌手名' },
        { id: 'liking', label: '好き度' },
        { id: 'singability', label: '歌いやすさ' },
        { id: 'calcTop70Views', label: '再生数_上位70%' },
      ];

  const addFilter = () => {
    onUpdate({
      filters: [...view.filters, { id: uuidv4(), columnId: columns[0].id, operator: 'contains', value: '' }]
    });
  };

  const updateFilter = (id: string, updates: Partial<FilterCondition>) => {
    onUpdate({
      filters: view.filters.map(f => f.id === id ? { ...f, ...updates } : f)
    });
  };

  const removeFilter = (id: string) => {
    onUpdate({ filters: view.filters.filter(f => f.id !== id) });
  };

  const addSort = () => {
    onUpdate({
      sorts: [...view.sorts, { id: uuidv4(), columnId: columns[0].id, direction: 'asc' }]
    });
  };

  const updateSort = (id: string, updates: Partial<SortCondition>) => {
    onUpdate({
      sorts: view.sorts.map(s => s.id === id ? { ...s, ...updates } : s)
    });
  };

  const removeSort = (id: string) => {
    onUpdate({ sorts: view.sorts.filter(s => s.id !== id) });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '20px', borderTop: '1px solid var(--border-color)', paddingTop: '20px' }}>
      
      {/* FILTER BUILDER */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h4>フィルター</h4>
          <button className="btn btn-sm btn-secondary" onClick={addFilter}><Plus size={14} /> 追加</button>
        </div>
        
        {view.filters.length > 1 && (
          <div style={{ marginBottom: '10px' }}>
            <select 
              value={view.filterOperator} 
              onChange={e => onUpdate({ filterOperator: e.target.value as 'AND' | 'OR' })}
              style={{ padding: '2px 4px', fontSize: '12px' }}
            >
              <option value="AND">すべての条件に一致 (AND)</option>
              <option value="OR">いずれかの条件に一致 (OR)</option>
            </select>
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {view.filters.map(f => (
            <div key={f.id} style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
              <select value={f.columnId} onChange={e => updateFilter(f.id, { columnId: e.target.value })} style={{ width: '80px', fontSize: '12px', padding: '2px' }}>
                {columns.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
              </select>
              <select value={f.operator} onChange={e => updateFilter(f.id, { operator: e.target.value as any })} style={{ width: '70px', fontSize: '12px', padding: '2px' }}>
                <option value="contains">含む</option>
                <option value="equals">一致</option>
                <option value="greaterThan">&gt;</option>
                <option value="lessThan">&lt;</option>
              </select>
              <input type="text" value={f.value} onChange={e => updateFilter(f.id, { value: e.target.value })} style={{ width: '60px', fontSize: '12px', padding: '2px' }} />
              <button className="btn btn-sm" style={{ color: 'var(--danger-color)', padding: '2px' }} onClick={() => removeFilter(f.id)}>
                <Trash2 size={12} />
              </button>
            </div>
          ))}
          {view.filters.length === 0 && <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>フィルターはありません</div>}
        </div>
      </div>

      {/* SORT BUILDER */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h4>並び替え</h4>
          <button className="btn btn-sm btn-secondary" onClick={addSort}><Plus size={14} /> 追加</button>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {view.sorts.map(s => (
            <div key={s.id} style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
              <select value={s.columnId} onChange={e => updateSort(s.id, { columnId: e.target.value })} style={{ width: '100px', fontSize: '12px', padding: '2px' }}>
                {columns.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
              </select>
              <select value={s.direction} onChange={e => updateSort(s.id, { direction: e.target.value as 'asc' | 'desc' })} style={{ width: '80px', fontSize: '12px', padding: '2px' }}>
                <option value="asc">昇順</option>
                <option value="desc">降順</option>
              </select>
              <button className="btn btn-sm" style={{ color: 'var(--danger-color)', padding: '2px' }} onClick={() => removeSort(s.id)}>
                <Trash2 size={12} />
              </button>
            </div>
          ))}
          {view.sorts.length === 0 && <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>並び替え条件はありません</div>}
        </div>
      </div>

    </div>
  );
};

export default FilterSortBuilder;
