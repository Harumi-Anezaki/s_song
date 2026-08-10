import React, { useState, useEffect } from 'react';
import { useViewStore } from '../store/viewStore';
import { useDataStore } from '../store/dataStore';
import DataTable from './DataTable';
import type { ViewSetting } from '../types';
import { v4 as uuidv4 } from 'uuid';
import { Plus, Settings2, Trash2, Copy, Edit3, AlignLeft, Search as SearchIcon, GripVertical } from 'lucide-react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import type { DragEndEvent } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, horizontalListSortingStrategy, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { SortableItem } from './SortableItem';
import FilterSortBuilder from './FilterSortBuilder';
import { hydrateSong, hydrateSinger } from '../utils/dataStoreUtils';

const LinkedDB: React.FC = () => {
  const { views, addView, updateView, deleteView, lastOpenedViewId, setLastOpenedViewId, reorderViews } = useViewStore();
  const { songs, singers } = useDataStore();
  
  const [activeViewId, setActiveViewId] = useState<string | null>(lastOpenedViewId);
  const [showSettings, setShowSettings] = useState(false);
  const [localSearch, setLocalSearch] = useState('');
  
  useEffect(() => {
    if (views.length > 0 && !activeViewId) {
      setActiveViewId(views[0].id);
    }
  }, [views, activeViewId]);

  useEffect(() => {
    if (activeViewId) {
      setLastOpenedViewId(activeViewId);
    }
  }, [activeViewId, setLastOpenedViewId]);

  const activeView = views.find(v => v.id === activeViewId);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleInitialSetup = (sourceDb: 'songs' | 'singers') => {
    const defaultCols = sourceDb === 'songs' 
      ? ['title', 'mainSingerId', 'views', 'urls', 'calcViewsPerDay']
      : ['name', 'liking', 'singability'];
      
    const newView: ViewSetting = {
      id: uuidv4(),
      name: `初期ビュー (${sourceDb === 'songs' ? '曲' : '歌手'})`,
      sourceDb,
      columns: defaultCols.map((c, i) => ({ id: c, visible: true, width: 150, order: i })),
      filters: [],
      filterOperator: 'AND',
      sorts: [],
      wrapText: false
    };
    addView(newView);
    setActiveViewId(newView.id);
  };

  const handleAddView = () => {
    if (!activeView) return;
    const newView: ViewSetting = {
      ...activeView,
      id: uuidv4(),
      name: `${activeView.name} (コピー)`,
    };
    addView(newView);
    setActiveViewId(newView.id);
  };

  const handleDeleteView = (id: string) => {
    if (views.length <= 1) {
      alert('最後の1つのビューは削除できません。');
      return;
    }
    if (window.confirm('このビューを削除しますか？')) {
      deleteView(id);
      if (activeViewId === id) {
        setActiveViewId(views.find(v => v.id !== id)?.id || null);
      }
    }
  };

  const handleRenameView = (id: string) => {
    const view = views.find(v => v.id === id);
    if (!view) return;
    const newName = window.prompt('新しいビュー名:', view.name);
    if (newName && newName.trim()) {
      updateView(id, { name: newName.trim() });
    }
  };

  const handleDragEndTabs = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = views.findIndex((v) => v.id === active.id);
      const newIndex = views.findIndex((v) => v.id === over.id);
      reorderViews(oldIndex, newIndex);
    }
  };

  const handleDragEndColumns = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id && activeView) {
      const oldIndex = activeView.columns.findIndex((c) => c.id === active.id);
      const newIndex = activeView.columns.findIndex((c) => c.id === over.id);
      const newCols = arrayMove(activeView.columns, oldIndex, newIndex);
      updateView(activeView.id, { columns: newCols.map((c, i) => ({ ...c, order: i })) });
    }
  };

  const toggleWrap = () => {
    if (activeView) {
      updateView(activeView.id, { wrapText: !activeView.wrapText });
    }
  };

  if (views.length === 0) {
    return (
      <div className="linked-db-container" style={{ padding: '40px', textAlign: 'center' }}>
        <h2>初回設定</h2>
        <p style={{ margin: '20px 0', color: 'var(--text-muted)' }}>参照元DBを選択してください</p>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
          <button className="btn btn-primary" onClick={() => handleInitialSetup('songs')}>曲DBを参照</button>
          <button className="btn btn-secondary" onClick={() => handleInitialSetup('singers')}>歌手DBを参照</button>
        </div>
      </div>
    );
  }

  // Filter raw data locally for "Search" and apply activeView filters/sorts
  let processedData: any[] = [];
  if (activeView) {
    const hydratedSongs = songs.map(s => hydrateSong(s, singers, songs));
    const hydratedSingers = singers.map(s => hydrateSinger(s, songs));
    processedData = activeView.sourceDb === 'songs' ? hydratedSongs : hydratedSingers;
    
    // Apply Filters
    if (activeView.filters.length > 0) {
      processedData = processedData.filter(item => {
        const results = activeView.filters.map(f => {
          const val = item[f.columnId];
          const target = f.value.toString().toLowerCase();
          const strVal = String(val).toLowerCase();
          switch (f.operator) {
            case 'contains': return strVal.includes(target);
            case 'equals': return strVal === target;
            case 'greaterThan': return Number(val) > Number(f.value);
            case 'lessThan': return Number(val) < Number(f.value);
            default: return true;
          }
        });
        return activeView.filterOperator === 'AND' ? results.every(r => r) : results.some(r => r);
      });
    }

    // Apply Local Search
    if (localSearch.trim()) {
      const lowerSearch = localSearch.toLowerCase();
      processedData = processedData.filter((item: any) => {
        const titleProp = activeView.sourceDb === 'songs' ? item.title : item.name;
        return String(titleProp).toLowerCase().includes(lowerSearch);
      });
    }

    // Apply Sorts
    if (activeView.sorts.length > 0) {
      processedData.sort((a, b) => {
        for (const sort of activeView.sorts) {
          const aVal = a[sort.columnId];
          const bVal = b[sort.columnId];
          if (aVal === bVal) continue;
          const aIsNum = typeof aVal === 'number';
          const bIsNum = typeof bVal === 'number';
          
          let compare = 0;
          if (aIsNum && bIsNum) compare = aVal - bVal;
          else compare = String(aVal).localeCompare(String(bVal));
          
          return sort.direction === 'asc' ? compare : -compare;
        }
        return 0;
      });
    }
  }

  return (
    <div className="linked-db-container" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <header className="content-header" style={{ paddingBottom: '0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center', paddingBottom: '20px' }}>
          <h2 className="content-title">リンクドDB</h2>
          <div className="flex-row">
            {activeView && (
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid var(--border-color)', borderRadius: '4px', padding: '4px 8px', backgroundColor: 'var(--bg-base)' }}>
                <SearchIcon size={14} color="var(--text-muted)" />
                <input 
                  type="text" 
                  placeholder="ビュー内検索..." 
                  value={localSearch}
                  onChange={(e) => setLocalSearch(e.target.value)}
                  style={{ border: 'none', outline: 'none', background: 'transparent', padding: '0 8px', color: 'var(--text-primary)', width: '150px' }}
                />
              </div>
            )}
            <button className={`btn btn-sm ${activeView?.wrapText ? 'btn-primary' : 'btn-secondary'}`} onClick={toggleWrap} title="折り返し表示">
              <AlignLeft size={16} />
            </button>
            <button className="btn btn-secondary btn-sm" onClick={() => setShowSettings(!showSettings)}>
              <Settings2 size={16} /> 表示設定
            </button>
          </div>
        </div>
        
        {/* Sortable Tabs */}
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEndTabs}>
          <div style={{ display: 'flex', gap: '10px', overflowX: 'auto', paddingBottom: '1px' }}>
            <SortableContext items={views.map(v => v.id)} strategy={horizontalListSortingStrategy}>
              {views.map(view => (
                <SortableItem key={view.id} id={view.id}>
                  <div 
                    style={{
                      padding: '8px 16px',
                      backgroundColor: activeViewId === view.id ? 'var(--bg-surface-hover)' : 'transparent',
                      borderTop: `2px solid ${activeViewId === view.id ? 'var(--primary-color)' : 'transparent'}`,
                      borderRight: '1px solid var(--border-color)',
                      borderLeft: '1px solid var(--border-color)',
                      borderTopLeftRadius: '4px',
                      borderTopRightRadius: '4px',
                      cursor: 'grab',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                    onClick={() => setActiveViewId(view.id)}
                  >
                    <span onDoubleClick={(e) => { e.stopPropagation(); handleRenameView(view.id); }}>{view.name}</span>
                    {activeViewId === view.id && (
                      <div style={{ display: 'flex', gap: '4px', marginLeft: '8px' }}>
                        <Edit3 size={12} color="var(--text-muted)" style={{ cursor: 'pointer' }} onClick={(e) => { e.stopPropagation(); handleRenameView(view.id); }} />
                        <Copy size={12} color="var(--text-muted)" style={{ cursor: 'pointer' }} onClick={(e) => { e.stopPropagation(); handleAddView(); }} />
                        {views.length > 1 && (
                          <Trash2 size={12} color="var(--danger-color)" style={{ cursor: 'pointer' }} onClick={(e) => { e.stopPropagation(); handleDeleteView(view.id); }} />
                        )}
                      </div>
                    )}
                  </div>
                </SortableItem>
              ))}
            </SortableContext>
            <button className="btn btn-sm" style={{ alignSelf: 'center', marginLeft: '10px' }} onClick={handleAddView}>
              <Plus size={16} />
            </button>
          </div>
        </DndContext>
      </header>
      
      <div className="content-body" style={{ padding: '0', overflowX: 'auto', display: 'flex' }}>
        {showSettings && activeView && (
          <div style={{ width: '250px', backgroundColor: 'var(--bg-surface)', borderRight: '1px solid var(--border-color)', padding: '20px', flexShrink: 0, overflowY: 'auto' }}>
            <h4 style={{ marginBottom: '15px' }}>表示カラム設定 (ドラッグで並び替え)</h4>
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEndColumns}>
              <SortableContext items={activeView.columns.map(c => c.id)} strategy={verticalListSortingStrategy}>
                <div style={{ fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {activeView.columns.map(col => (
                    <SortableItem key={col.id} id={col.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'grab', padding: '4px', backgroundColor: 'var(--bg-base)', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                      <GripVertical size={14} color="var(--text-muted)" />
                      <input 
                        type="checkbox" 
                        checked={col.visible}
                        onChange={(e) => {
                          const newCols = activeView.columns.map(c => c.id === col.id ? { ...c, visible: e.target.checked } : c);
                          updateView(activeView.id, { columns: newCols });
                        }}
                      />
                      <span style={{ flexGrow: 1 }}>{col.id}</span>
                    </SortableItem>
                  ))}
                </div>
              </SortableContext>
            </DndContext>
            <FilterSortBuilder view={activeView} onUpdate={(updates) => updateView(activeView.id, updates)} />
          </div>
        )}
        
        <div style={{ flexGrow: 1, overflowX: 'auto' }}>
          {activeView && (
            <DataTable 
              type={activeView.sourceDb} 
              data={processedData} 
              visibleColumns={activeView.columns.filter(c => c.visible).map(c => c.id)}
              wrapText={activeView.wrapText}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default LinkedDB;
