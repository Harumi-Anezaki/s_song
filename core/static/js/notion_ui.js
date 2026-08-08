
window.showPropertyVisibilityModal = function(allProps, currentProps) {
    return new Promise(resolve => {
        // currentProps contains {key, visible}
        let propsState = allProps.map(p => {
            let cp = currentProps.find(c => c.key === p.key);
            return {
                key: p.key,
                label: p.label || p.key,
                visible: cp ? cp.visible : true
            };
        });

        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100vw';
        overlay.style.height = '100vh';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.4)';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '10000';

        const modal = document.createElement('div');
        modal.style.backgroundColor = 'var(--bg-color)';
        modal.style.color = 'var(--text-color)';
        modal.style.borderRadius = '8px';
        modal.style.boxShadow = '0 10px 25px rgba(0,0,0,0.2)';
        modal.style.width = '350px';
        modal.style.maxHeight = '80vh';
        modal.style.display = 'flex';
        modal.style.flexDirection = 'column';
        modal.style.overflow = 'hidden';

        // Header
        const header = document.createElement('div');
        header.style.padding = '16px';
        header.style.borderBottom = '1px solid var(--border-color)';
        header.style.display = 'flex';
        header.style.justifyContent = 'space-between';
        header.style.alignItems = 'center';
        
        const titleArea = document.createElement('div');
        titleArea.style.display = 'flex';
        titleArea.style.alignItems = 'center';
        titleArea.style.gap = '8px';
        
        const backBtn = document.createElement('span');
        backBtn.innerHTML = '←';
        backBtn.style.cursor = 'pointer';
        backBtn.style.fontSize = '18px';
        backBtn.style.color = 'var(--text-muted)';
        
        const title = document.createElement('h3');
        title.innerText = 'プロパティの表示/非表示';
        title.style.margin = '0';
        title.style.fontSize = '16px';

        titleArea.appendChild(backBtn);
        titleArea.appendChild(title);

        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '✕';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.color = 'var(--text-muted)';
        closeBtn.style.padding = '4px';
        closeBtn.style.borderRadius = '50%';
        closeBtn.style.backgroundColor = '#f1f1f1';
        closeBtn.style.width = '24px';
        closeBtn.style.height = '24px';
        closeBtn.style.display = 'flex';
        closeBtn.style.justifyContent = 'center';
        closeBtn.style.alignItems = 'center';

        header.appendChild(titleArea);
        header.appendChild(closeBtn);

        // Search
        const searchContainer = document.createElement('div');
        searchContainer.style.padding = '12px 16px';
        
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'プロパティを検索...';
        searchInput.style.width = '100%';
        searchInput.style.padding = '8px 12px';
        searchInput.style.borderRadius = '6px';
        searchInput.style.border = '1px solid var(--border-color)';
        searchInput.style.boxSizing = 'border-box';
        searchContainer.appendChild(searchInput);

        // Lists
        const listsContainer = document.createElement('div');
        listsContainer.style.overflowY = 'auto';
        listsContainer.style.flex = '1';
        listsContainer.style.padding = '0 16px 16px 16px';

        const shownSection = document.createElement('div');
        const hiddenSection = document.createElement('div');

        const renderLists = (filterText = '') => {
            shownSection.innerHTML = '';
            hiddenSection.innerHTML = '';

            const shownTitle = document.createElement('div');
            shownTitle.style.fontSize = '12px';
            shownTitle.style.color = 'var(--text-muted)';
            shownTitle.style.marginTop = '16px';
            shownTitle.style.marginBottom = '8px';
            shownTitle.innerText = 'テーブルで表示';
            shownSection.appendChild(shownTitle);

            const hiddenTitle = document.createElement('div');
            hiddenTitle.style.fontSize = '12px';
            hiddenTitle.style.color = 'var(--text-muted)';
            hiddenTitle.style.marginTop = '24px';
            hiddenTitle.style.marginBottom = '8px';
            hiddenTitle.innerText = 'テーブルで非表示';
            hiddenSection.appendChild(hiddenTitle);

            propsState.forEach(p => {
                if (filterText && !p.label.toLowerCase().includes(filterText.toLowerCase())) return;

                const item = document.createElement('div');
                item.style.display = 'flex';
                item.style.alignItems = 'center';
                item.style.padding = '8px 0';
                item.style.cursor = 'pointer';

                const icon = document.createElement('span');
                icon.innerText = '⋮⋮';
                icon.style.color = '#ccc';
                icon.style.marginRight = '8px';
                icon.style.fontSize = '16px';

                const name = document.createElement('span');
                name.innerText = p.label;
                name.style.flex = '1';
                name.style.fontSize = '14px';

                const eye = document.createElement('span');
                eye.innerHTML = p.visible ? '👁️' : '👁️‍🗨️'; // Use appropriate unicode or styling
                eye.style.cursor = 'pointer';
                eye.style.opacity = p.visible ? '1' : '0.4';

                item.appendChild(icon);
                item.appendChild(name);
                item.appendChild(eye);

                item.onclick = () => {
                    p.visible = !p.visible;
                    renderLists(searchInput.value);
                };

                if (p.visible) {
                    shownSection.appendChild(item);
                } else {
                    hiddenSection.appendChild(item);
                }
            });
        };

        renderLists();

        searchInput.oninput = (e) => {
            renderLists(e.target.value);
        };

        listsContainer.appendChild(shownSection);
        listsContainer.appendChild(hiddenSection);

        modal.appendChild(header);
        modal.appendChild(searchContainer);
        modal.appendChild(listsContainer);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        const close = () => {
            document.body.removeChild(overlay);
            resolve(propsState.map(p => ({key: p.key, visible: p.visible})));
        };

        closeBtn.onclick = close;
        backBtn.onclick = close;
        overlay.onclick = (e) => {
            if (e.target === overlay) close();
        };
    });
};


window.customPrompt = function(message, defaultValue = '') {
    return new Promise(resolve => {
        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100vw';
        overlay.style.height = '100vh';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '9999';

        const modal = document.createElement('div');
        modal.style.backgroundColor = 'var(--bg-color)';
        modal.style.color = 'var(--text-color)';
        modal.style.padding = '20px';
        modal.style.borderRadius = '8px';
        modal.style.boxShadow = '0 4px 6px rgba(0,0,0,0.3)';
        modal.style.minWidth = '300px';

        const text = document.createElement('p');
        text.innerText = message;
        text.style.marginBottom = '12px';
        text.style.whiteSpace = 'pre-wrap';

        const input = document.createElement('input');
        input.type = 'text';
        input.value = defaultValue;
        input.style.width = '100%';
        input.style.padding = '8px';
        input.style.marginBottom = '16px';
        input.style.boxSizing = 'border-box';
        
        const btnContainer = document.createElement('div');
        btnContainer.style.display = 'flex';
        btnContainer.style.justifyContent = 'flex-end';
        btnContainer.style.gap = '8px';

        const cancelBtn = document.createElement('button');
        cancelBtn.innerText = 'キャンセル';
        cancelBtn.className = 'btn';
        
        const okBtn = document.createElement('button');
        okBtn.innerText = 'OK';
        okBtn.className = 'btn btn-primary';

        btnContainer.appendChild(cancelBtn);
        btnContainer.appendChild(okBtn);

        modal.appendChild(text);
        modal.appendChild(input);
        modal.appendChild(btnContainer);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        input.focus();

        const close = (value) => {
            document.body.removeChild(overlay);
            resolve(value);
        };

        cancelBtn.onclick = () => close(null);
        okBtn.onclick = () => close(input.value);
        input.onkeydown = (e) => {
            if (e.key === 'Enter') close(input.value);
            if (e.key === 'Escape') close(null);
        };
    });
};

let databaseViews = {};
let customSchemas = [];

let notionData = {
    songs: [],
    artists: [],
    settings: {},
    tags: []
};

let currentViewKey = null;

// Base Schema Definitions
const baseSchemas = {
    songs: [
        { key: 'title', label: 'title', type: 'title', editable: true },
        { key: 'main_artist_id', label: 'main_artist_id', type: 'relation', editable: true, ref: 'artists', single: true },
        { key: 'sub_artists', label: 'sub_artists', type: 'relation', editable: true, ref: 'artists', multiple: true },
        { key: 'tag_a', label: 'tag_a', type: 'select', editable: true, options: ['日本', '海外'] },
        { key: 'tag_b_list', label: 'tag_b_list', type: 'multi_select', editable: true, options: ['tag_high_pitch', 'tag_ohako', 'tag_hiphop', 'tag_ballad', 'tag_anime'] },
        { key: 'primary_url', label: 'primary_url', type: 'url_special', editable: true },
        { key: 'effective_base_date', label: 'effective_base_date', type: 'date', editable: true },
        { key: 'total_views', label: 'total_views', type: 'number', editable: false },
        { key: 'views_per_day', label: 'views_per_day', type: 'number_float', editable: false },
        { key: 'is_outdated', label: 'is_outdated', type: 'formula', editable: false, options: {expression: "prop('is_outdated')"} },
        { key: 'dl_status', label: 'dl_status', type: 'checkbox_3state', editable: true }
    ],
    artists: [
        { key: 'name', label: 'name', type: 'title', editable: true },
        { key: 'rating', label: 'rating', type: 'number', editable: true },
        { key: 'singability', label: 'singability', type: 'number', editable: true },
        { key: 'main_songs', label: 'main_songs', type: 'relation_read', ref: 'songs', multiple: true, editable: false },
        { key: 'created_at', label: 'created_at', type: 'date_time', editable: false }
    ]
};

async function initNotionUI(mode) {
    window.notionUIMode = mode || 'linked';
    await fetchNotionData();
    
    if (window.notionUIMode === 'original') {
        const songsProps = getPropertiesForTable('songs').map(p => ({key: p.key, visible: true}));
        const artistsProps = getPropertiesForTable('artists').map(p => ({key: p.key, visible: true}));
        databaseViews = {
            'original_songs': {
                id: 'original_songs',
                name: 'song',
                type: 'table',
                target_table: 'songs',
                config: { properties: songsProps, sorts: [], filters: [] }
            },
            'original_artists': {
                id: 'original_artists',
                name: 'singer',
                type: 'table',
                target_table: 'artists',
                config: { properties: artistsProps, sorts: [], filters: [] }
            }
        };
        if (!currentViewKey || !databaseViews[currentViewKey]) {
            currentViewKey = 'original_songs';
        }
    } else {
        if (Object.keys(databaseViews).length === 0) {
            await createDefaultViews();
        }
        const urlParams = new URLSearchParams(window.location.search);
        const viewParam = urlParams.get('view');
        if (viewParam && databaseViews[viewParam]) {
            currentViewKey = viewParam;
        } else if (!currentViewKey || !databaseViews[currentViewKey]) {
            currentViewKey = Object.keys(databaseViews)[0];
        }
    }
    renderNotionContainer();
}

async function createDefaultViews() {
    const songsView = {
        target_table: 'songs',
        name: '曲_一覧',
        type: 'table',
        config: {
            properties: baseSchemas.songs.map(p => ({ key: p.key, visible: true })),
            sorts: [],
            filters: []
        }
    };
    
    const artistsView = {
        target_table: 'artists',
        name: '歌手_一覧',
        type: 'table',
        config: {
            properties: baseSchemas.artists.map(p => ({ key: p.key, visible: true })),
            sorts: [{ key: 'created_at', direction: 'desc' }],
            filters: []
        }
    };
    
    await Promise.all([
        fetch('/api/views_config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(songsView) }),
        fetch('/api/views_config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(artistsView) })
    ]);
    
    await fetchNotionData(); // reload
}

async function fetchNotionData() {
    try {
        const [songsRes, artistsRes, viewsRes, tagsRes, optLabelsRes] = await Promise.all([
            fetch('/api/database_view/songs'),
            fetch('/api/database_view/artists'),
            fetch('/api/views_config'),
            fetch('/api/tags'),
            fetch('/api/schemas/option_labels')
        ]);
        
        notionData.songs = await songsRes.json();
        notionData.artists = await artistsRes.json();
        notionData.tags = await tagsRes.json();
        if (optLabelsRes.ok) {
            notionData.optionLabels = await optLabelsRes.json();
        } else {
            notionData.optionLabels = {};
        }
        
        const viewsList = await viewsRes.json();
        
        databaseViews = {};
        viewsList.forEach(v => {
            databaseViews[v.id] = v;
        });
        
    } catch(e) {
        console.error("Failed to load Notion data", e);
    }
}

function getPropertiesForTable(tableName) {
    let props = [...baseSchemas[tableName]];
    
    // Apply local storage labels
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem('customLabels') || '{}'); } catch(e) {}
    if(saved[tableName]) {
        props = props.map(p => {
            if(saved[tableName][p.key]) {
                return {...p, label: saved[tableName][p.key]};
            }
            return p;
        });
    }
    return props;
}

function renderNotionContainer() {
    const root = document.getElementById('notion-root');
    if(window.notionUIMode === 'original') root.classList.add('notion-mode-original'); else root.classList.remove('notion-mode-original');
    const container = document.getElementById('notion-root');
    if(!container) return;
    
    let html = `
        <div class="notion-header">
            <div class="notion-tabs">
                ${Object.keys(databaseViews).map(key => `
                    <div class="notion-tab ${key === currentViewKey ? 'active' : ''}" onclick="switchNotionView('${key}')">
                        <svg viewBox="0 0 14 14" style="width:14px;height:14px;fill:currentColor;opacity:0.6;"><path d="M1.5 1.5v11h11v-11h-11zM11.5 2.5v3h-3.5v-3h3.5zM7 2.5v3h-4.5v-3h4.5zM2.5 6.5h4.5v5h-4.5v-5zM8 11.5v-5h3.5v5h-3.5z"></path></svg>
                        ${databaseViews[key].name}
                    </div>
                `).join('')}
                ${window.notionUIMode === 'original' ? '' : '<div class="notion-tab" onclick="createNewView()">＋</div>'}
            </div>
            <div class="notion-toolbar">
                <!-- Action Buttons (Shown when checkboxes are selected) -->
                <div id="notion-bulk-actions" style="display:none; align-items:center; gap:8px; margin-right: 16px;">
                    <span id="notion-bulk-count" style="font-size:12px; color:var(--text-secondary);"></span>
                    <button class="notion-btn notion-btn-danger" onclick="bulkDelete()" style="color: var(--danger-color); border-color: var(--danger-color);">削除</button>
                    <button class="notion-btn" onclick="bulkMerge()">統合</button>
                </div>
                
            </div>
        </div>
        <div id="notion-view-content" class="notion-view-content"></div>
    `;
    container.innerHTML = html;
    
    renderCurrentView();
}

window.switchNotionView = function(key) {
    if (currentViewKey === key) {
        // Already active! Open edit menu
        if (window.notionUIMode !== 'original' && typeof openViewEditMenu === 'function') {
            openViewEditMenu(key);
        }
        return;
    }
    currentViewKey = key;
    const url = new URL(window.location);
    url.searchParams.set('view', key);
    window.history.pushState({}, '', url);
    renderNotionContainer();
};

function renderCurrentView() {
    if(!currentViewKey || !databaseViews[currentViewKey]) return;
    
    const viewDef = databaseViews[currentViewKey];
    const dataList = notionData[viewDef.target_table];
    const allProps = getPropertiesForTable(viewDef.target_table);
    
    // Apply Filters (Simple stub for now, implement actual filtering based on config)
    let filtered = [...dataList];
    
    // Apply Sorts
    if(viewDef.config.sorts && viewDef.config.sorts.length > 0) {
        filtered.sort((a, b) => {
            for(let sort of viewDef.config.sorts) {
                let valA = a[sort.key];
                let valB = b[sort.key];
                if(valA < valB) return sort.direction === 'asc' ? -1 : 1;
                if(valA > valB) return sort.direction === 'asc' ? 1 : -1;
            }
            return 0;
        });
    }
    
    const content = document.getElementById('notion-view-content');
    
    if (viewDef.type === 'table') {
        content.innerHTML = renderTable(viewDef, filtered, allProps);
        attachTableEvents(viewDef, filtered, allProps);
        initFillHandle(viewDef, filtered, allProps);
    } else if (viewDef.type === 'board') {
        content.innerHTML = renderBoard(viewDef, filtered, allProps);
        // attachBoardEvents(...)
    } else {
        content.innerHTML = `<div>View type ${viewDef.type} not supported yet.</div>`;
    }
}

function renderTable(viewDef, data, allProps) {
    let visibleProps = allProps;
    if(viewDef.config.properties) {
        visibleProps = viewDef.config.properties
            .filter(vp => vp.visible !== false)
            .map(vp => allProps.find(p => p.key === vp.key))
            .filter(p => p);
    }
    
    let html = '<div class="notion-table-container"><table class="notion-table">';
    html += '<thead><tr>';
    html += '<th class="notion-th-checkbox"><input type="checkbox" id="notion-select-all"></th>';
    visibleProps.forEach(prop => {
        html += `<th class="notion-th" data-key="${prop.key}" draggable="true" onclick="editColumnLabel('${viewDef.target_table}', '${prop.key}', '${prop.label.replace(/'/g, '\\\'')}', event)">
            <div class="notion-th-content">
                ${getPropertyIcon(prop.type)}
                ${prop.label}
            </div>
        </th>`;
    });
    html += '</tr></thead><tbody>';
    
    data.forEach(row => {
        html += `<tr class="notion-tr" data-id="${row.id}">`;
        html += '<td class="notion-td-checkbox"><input type="checkbox" class="notion-row-select"></td>';
        visibleProps.forEach(prop => {
            html += `<td class="notion-td" data-key="${prop.key}">${renderCell(prop, row)}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    return html;
}

function getOptionLabel(val) {
    return (notionData.optionLabels && notionData.optionLabels[val]) ? notionData.optionLabels[val] : val;
}

function renderCell(prop, row) {
    let val = row[prop.key];
    
    if (prop.key === 'primary_url' || prop.type === 'url_special') {
        return val ? `<a href="${val}" target="_blank" style="color: #2eaadc; text-decoration: underline;">${val}</a>` : '';
    }
    if (prop.key === 'views_per_day') {
        return val !== null && val !== undefined ? Math.round(val).toLocaleString() : '';
    }
    if (prop.key === 'main_artist_id' && val) {
        // row.artist_name is available from get_database_songs API
        const name = row.artist_name || val;
        return `<a href="javascript:void(0)" onclick="searchArtistYoutube('${name.replace(/'/g, "\'")}')" style="color: #2eaadc; font-weight: bold; text-decoration: underline;">${name}</a>`;
    }
    
    if (prop.type === 'title') {
        return `<div style="display:flex; align-items:center; gap:6px;"><span style="opacity:0.5;"></span><span class="notion-title-text" style="font-weight:500;">${val || ''}</span></div>`;
    } else if (prop.type === 'formula') {
        // Evaluate formula
        const allProps = getPropertiesForTable(databaseViews[currentViewKey].target_table);
        const expr = prop.options && prop.options.expression ? prop.options.expression : '';
        const res = evaluateFormula(expr, row, allProps);
        return res !== null && res !== undefined ? res : '';
    } else if (prop.type === 'checkbox' || prop.type === 'checkbox_3state') {
        const isChecked = val === 'DOWNLOADED' || val === true || val === 1 || val === '1';
        const isError = val === 'ERROR';
        if (isError) return `<div style="display:flex; justify-content:center; align-items:center; height:100%;"><span style="color:var(--danger-color); font-size:14px;">⚠️</span></div>`;
        return `<div style="display:flex; justify-content:center; align-items:center; height:100%;">
                    <div style="width:16px; height:16px; border:1px solid var(--border-color); border-radius:3px; display:flex; align-items:center; justify-content:center; background:${isChecked ? 'var(--primary-color)' : 'transparent'}; cursor:pointer;">
                        ${isChecked ? '<svg viewBox="0 0 14 14" style="width:12px; height:12px; fill:white;"><path d="M5.5 10.5L2 7l1.5-1.5L5.5 7.5 11.5 1.5 13 3z"></path></svg>' : ''}
                    </div>
                </div>`;
    } else if (prop.type === 'select') {
        return val ? `<span class="notion-tag">${getOptionLabel(val)}</span>` : '';
    } else if (prop.type === 'multiselect' || prop.type === 'multi_select') {
        if (!val) return '';
        const arr = Array.isArray(val) ? val : String(val).split(',').map(s => s.trim()).filter(s => s);
        return `<div style="display:flex; flex-wrap:wrap; gap:4px; pointer-events:none;">${arr.map(v => `<span class="notion-tag">${getOptionLabel(v)}</span>`).join('')}</div>`;
    } else if (prop.type === 'number') {
        return val !== null && val !== undefined ? Number(val).toLocaleString() : '';
    } else if (prop.type === 'number_float') {
        return val !== null && val !== undefined ? Number(val).toFixed(2) : '';
    }
    
    return val || '';
}


window.updateBulkActionBar = function(tableName) {
    const rowCheckboxes = document.querySelectorAll('.notion-row-select');
    const checked = Array.from(rowCheckboxes).filter(c => c.checked);
    const count = checked.length;
    
    const actionContainer = document.getElementById('notion-bulk-actions');
    const countSpan = document.getElementById('notion-bulk-count');
    
    if (count > 0) {
        if(actionContainer) actionContainer.style.display = 'flex';
        if(countSpan) countSpan.textContent = `${count}件選択中`;
    } else {
        if(actionContainer) actionContainer.style.display = 'none';
    }
};


function initFillHandle(viewDef, data, allProps) {
    if (!document.getElementById('fill-handle-styles')) {
        const style = document.createElement('style');
        style.id = 'fill-handle-styles';
        style.innerHTML = `
            .notion-fill-handle {
                position: absolute;
                width: 8px;
                height: 8px;
                background: #2eaadc;
                border: 1px solid white;
                border-radius: 50%;
                cursor: crosshair;
                z-index: 10000;
                display: none;
            }
            .fill-highlight {
                outline: 2px solid #2eaadc !important;
                outline-offset: -2px;
                background-color: rgba(46, 170, 220, 0.1) !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    let handle = document.getElementById('notion-fill-handle');
    if (!handle) {
        handle = document.createElement('div');
        handle.id = 'notion-fill-handle';
        handle.className = 'notion-fill-handle';
        document.body.appendChild(handle);
        
        handle.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            if (!handle.currentTd) return;
            
            window.isFilling = true;
            const startTd = handle.currentTd;
            const startTr = startTd.closest('tr');
            const startRowIndex = Array.from(startTr.parentNode.children).indexOf(startTr);
            const startDataId = parseInt(startTr.getAttribute('data-id'));
            const propKey = startTd.getAttribute('data-key');
            
            let currentHighlightIndex = startRowIndex;
            const tbody = startTr.parentNode;
            const rows = Array.from(tbody.children);
            
            const onMouseMove = (moveEvent) => {
                if (!window.isFilling) return;
                
                const targetElements = document.elementsFromPoint(moveEvent.clientX, moveEvent.clientY);
                const targetTd = targetElements.find(el => el.classList && el.classList.contains('notion-td') && el.getAttribute('data-key') === propKey);
                
                if (targetTd) {
                    const targetTr = targetTd.closest('tr');
                    currentHighlightIndex = rows.indexOf(targetTr);
                    
                    const minIdx = Math.min(startRowIndex, currentHighlightIndex);
                    const maxIdx = Math.max(startRowIndex, currentHighlightIndex);
                    
                    rows.forEach((row, idx) => {
                        const cell = row.querySelector(`.notion-td[data-key="${propKey}"]`);
                        if (cell) {
                            if (idx >= minIdx && idx <= maxIdx) {
                                cell.classList.add('fill-highlight');
                            } else {
                                cell.classList.remove('fill-highlight');
                            }
                        }
                    });
                }
            };
            
            const onMouseUp = async (upEvent) => {
                window.isFilling = false;
                handle.style.display = 'none';
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                
                const minIdx = Math.min(startRowIndex, currentHighlightIndex);
                const maxIdx = Math.max(startRowIndex, currentHighlightIndex);
                
                const targetRows = [];
                rows.forEach((row, idx) => {
                    const cell = row.querySelector(`.notion-td[data-key="${propKey}"]`);
                    if (cell) {
                        cell.classList.remove('fill-highlight');
                        if (idx >= minIdx && idx <= maxIdx && idx !== startRowIndex) {
                            targetRows.push({
                                id: parseInt(row.getAttribute('data-id')),
                            });
                        }
                    }
                });
                
                if (targetRows.length > 0) {
                    const endpoint = window.currentConfigTableName === 'artists' ? '/api/artists' : '/api/songs';
                    // We need to fetch the fresh data array since `data` might be stale or closure bound
                    // Actually `data` is passed to initFillHandle.
                    const sourceRow = data.find(r => r.id === startDataId);
                    const sourceValue = sourceRow[propKey];
                    
                    const prop = allProps.find(p => p.key === propKey);
                    
                    for (const tgt of targetRows) {
                        const payload = {};
                        payload[propKey] = sourceValue;
                        
                        // Optimistic DOM update
                        const targetRowData = data.find(r => r.id === tgt.id);
                        if (targetRowData) targetRowData[propKey] = sourceValue;
                        
                        const tr = document.querySelector(`tr[data-id="${tgt.id}"]`);
                        if (tr) {
                            const td = tr.querySelector(`.notion-td[data-key="${propKey}"]`);
                            if (td && prop) {
                                td.innerHTML = renderCell(prop, targetRowData);
                            }
                        }

                        try {
                            // using viewDef.target_table instead of currentConfigTableName which might be null
                            const ep = viewDef.target_table === 'artists' ? '/api/artists' : '/api/songs';
                            fetch(`${ep}/${tgt.id}`, {
                                method: 'PATCH',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify(payload)
                            });
                        } catch(e) {}
                    }
                    window.fetchNotionData(); // Reload UI data in background without resetting scroll
                }
            };
            
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });
    }
    
    // Clear old listeners if any
    const tableContainer = document.querySelector('.notion-table-container');
    if (tableContainer) {
        // Remove old clones to clear listeners
        const newTableContainer = tableContainer.cloneNode(true);
        tableContainer.parentNode.replaceChild(newTableContainer, tableContainer);
        
        newTableContainer.addEventListener('mousemove', (e) => {
            if (window.isFilling) return;
            const td = e.target.closest('.notion-td');
            if (td) {
                const propKey = td.getAttribute('data-key');
                const prop = allProps.find(p => p.key === propKey);
                if (prop && prop.editable) {
                    const rect = td.getBoundingClientRect();
                    handle.style.top = (rect.bottom - 4 + window.scrollY) + 'px';
                    handle.style.left = (rect.right - 4 + window.scrollX) + 'px';
                    handle.style.display = 'block';
                    handle.currentTd = td;
                } else {
                    handle.style.display = 'none';
                }
            } else if (!e.target.closest('.notion-fill-handle')) {
                handle.style.display = 'none';
            }
        });
        
        newTableContainer.addEventListener('mouseleave', (e) => {
            if (!window.isFilling && (!e.relatedTarget || !e.relatedTarget.closest('.notion-fill-handle'))) {
                handle.style.display = 'none';
            }
        });
        
        // Re-attach click events since we cloned the container
        const tds = newTableContainer.querySelectorAll('.notion-td');
        tds.forEach(td => {
            td.addEventListener('click', (ev) => {
                if(ev.target.closest('a') || ev.target.closest('input')) return;
                const propKey = td.getAttribute('data-key');
                const prop = allProps.find(p => p.key === propKey);
                if(prop && prop.editable) {
                    startInlineEdit(td, prop, data, viewDef.target_table);
                }
            });
        });
        
        // Re-attach checkbox logic
        const selectAll = newTableContainer.querySelector('#notion-select-all');
        const rowCheckboxes = newTableContainer.querySelectorAll('.notion-row-select');
        
        if (selectAll) {
            selectAll.addEventListener('change', (ev) => {
                rowCheckboxes.forEach(cb => cb.checked = ev.target.checked);
                updateBulkActionBar(viewDef.target_table);
            });
        }
        rowCheckboxes.forEach(cb => {
            cb.addEventListener('change', () => {
                const allChecked = Array.from(rowCheckboxes).every(c => c.checked);
                const someChecked = Array.from(rowCheckboxes).some(c => c.checked);
                if (selectAll) {
                    selectAll.checked = allChecked;
                    selectAll.indeterminate = someChecked && !allChecked;
                }
                updateBulkActionBar(viewDef.target_table);
            });
        });
    }
}

function attachTableEvents(viewDef, data, allProps) {
    const tds = document.querySelectorAll('.notion-td');
    tds.forEach(td => {
        td.addEventListener('click', (e) => {
            if(e.target.closest('a') || e.target.closest('input')) return;
            const propKey = td.getAttribute('data-key');
            const prop = allProps.find(p => p.key === propKey);
            if(prop && prop.editable) {
                startInlineEdit(td, prop, data, viewDef.target_table);
            }
        });
    });
    
    // Checkbox logic
    const selectAll = document.getElementById('notion-select-all');
    const rowCheckboxes = document.querySelectorAll('.notion-row-select');
    
    if (selectAll) {
        selectAll.addEventListener('change', (e) => {
            rowCheckboxes.forEach(cb => {
                cb.checked = e.target.checked;
            });
            updateBulkActionBar(viewDef.target_table);
        });
    }
    
    rowCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            const allChecked = Array.from(rowCheckboxes).every(c => c.checked);
            const someChecked = Array.from(rowCheckboxes).some(c => c.checked);
            if (selectAll) {
                selectAll.checked = allChecked;
                selectAll.indeterminate = someChecked && !allChecked;
            }
            updateBulkActionBar(viewDef.target_table);
        });
    });
    
    updateBulkActionBar(viewDef.target_table); // Initialize
}

function startInlineEdit(td, prop, data, tableName) {
    if(td.classList.contains('editing')) return;
    const tr = td.closest('tr');
    const id = parseInt(tr.getAttribute('data-id'));
    const row = data.find(r => r.id === id);
    
    td.classList.add('editing');
    const originalHtml = td.innerHTML;

    if (prop.type === 'checkbox' || prop.type === 'checkbox_3state') {
        const current = row[prop.key];
        let newVal = 'NOT_DOWNLOADED';
        if (prop.type === 'checkbox_3state') {
            if (current === 'NOT_DOWNLOADED' || !current) newVal = 'DOWNLOADED';
            else if (current === 'DOWNLOADED') newVal = 'ERROR';
            else newVal = 'NOT_DOWNLOADED';
        } else {
            newVal = !current;
        }
        
        // Save immediately
        const endpoint = tableName === 'songs' ? '/api/songs' : '/api/artists';
        const payload = {};
        payload[prop.key] = newVal;
        fetch(`${endpoint}/${id}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        }).then(res => res.json()).then(result => {
            if(result.success) {
                row[prop.key] = newVal;
                td.innerHTML = renderCell(prop, row);
            } else {
                alert('保存失敗: ' + result.error);
                td.innerHTML = originalHtml;
            }
            td.classList.remove('editing');
        }).catch(e => {
            alert('保存失敗: ' + e);
            td.innerHTML = originalHtml;
            td.classList.remove('editing');
        });
        return; // Skip standard input rendering
    }
    
    if ((prop.type === 'multiselect' || prop.type === 'multi_select') && prop.options) {
        let currentVals = Array.isArray(row[prop.key]) ? [...row[prop.key]] : (row[prop.key] ? String(row[prop.key]).split(',').map(s=>s.trim()).filter(s=>s) : []);
        
        td.innerHTML = `
            <div class="notion-ms-container" style="position:relative; width: 100%; font-size: 14px; background: white;">
                <div class="notion-ms-selected" style="display:flex; flex-wrap:wrap; gap:4px; padding: 4px; min-height: 24px; border: 1px solid #2ea2ff; border-radius: 4px;">
                    <div id="ms-tags-area" style="display:flex; flex-wrap:wrap; gap:4px;"></div>
                    <input type="text" class="notion-ms-input" placeholder="検索..." style="border:none; outline:none; flex:1; min-width:60px; font-size: 14px;">
                </div>
                <div class="notion-ms-dropdown" style="position:absolute; top:100%; left:0; right:0; background:white; border:1px solid #ddd; border-radius:4px; box-shadow:0 4px 12px rgba(0,0,0,0.15); max-height:200px; overflow-y:auto; z-index:10000; margin-top: 4px;">
                    ${prop.options.map(o => `
                        <div class="notion-ms-option-wrap" data-val="${o}" style="display:flex; align-items:center; cursor: pointer; padding: 6px 8px;">
                            <div class="notion-ms-option" style="flex:1;">${getOptionLabel(o)}</div>
                            <div class="notion-ms-edit-btn" style="padding: 0 4px; color:#999; display:none; border-radius:3px;">⋮</div>
                        </div>
                    `).join('')}
                    <div class="notion-ms-no-results" style="padding: 6px 8px; color: #999; display: none;">該当なし</div>
                </div>
            </div>
        `;

        const container = td.querySelector('.notion-ms-container');
        const input = container.querySelector('.notion-ms-input');
        const dropdown = container.querySelector('.notion-ms-dropdown');
        const optionWraps = Array.from(dropdown.querySelectorAll('.notion-ms-option-wrap'));
        const tagsArea = container.querySelector('#ms-tags-area');
        const noResults = container.querySelector('.notion-ms-no-results');

        const renderTags = () => {
            tagsArea.innerHTML = currentVals.map(v => `
                <span class="notion-tag" style="display:flex; align-items:center; gap:4px;">
                    ${getOptionLabel(v)} <span class="ms-remove-btn" data-val="${v}" style="cursor:pointer; color:#999;">&times;</span>
                </span>
            `).join('');
            
            tagsArea.querySelectorAll('.ms-remove-btn').forEach(btn => {
                btn.addEventListener('mousedown', (e) => {
                    e.preventDefault(); // prevent blur
                    e.stopPropagation();
                    const valToRemove = btn.dataset.val;
                    currentVals = currentVals.filter(v => v !== valToRemove);
                    renderTags();
                    input.focus();
                });
            });
            
            // Highlight selected options in dropdown
            optionWraps.forEach(wrap => {
                if (currentVals.includes(wrap.dataset.val)) {
                    wrap.style.backgroundColor = 'rgba(46, 170, 220, 0.1)';
                } else {
                    wrap.style.backgroundColor = '';
                }
            });
        };

        renderTags();
        input.focus();

        input.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase();
            let hasVisible = false;
            optionWraps.forEach(wrap => {
                if (wrap.dataset.val.toLowerCase().includes(val) || getOptionLabel(wrap.dataset.val).toLowerCase().includes(val)) {
                    wrap.style.display = 'flex';
                    hasVisible = true;
                } else {
                    wrap.style.display = 'none';
                }
            });
            noResults.style.display = hasVisible ? 'none' : 'block';
        });

        // Add hover effect via JS
        optionWraps.forEach(wrap => {
            const btn = wrap.querySelector('.notion-ms-edit-btn');
            const optLabel = wrap.querySelector('.notion-ms-option');
            
            wrap.addEventListener('mouseenter', () => {
                btn.style.display = 'block';
                if (!currentVals.includes(wrap.dataset.val)) wrap.style.backgroundColor = '#f2f2f2';
            });
            wrap.addEventListener('mouseleave', () => {
                btn.style.display = 'none';
                if (!currentVals.includes(wrap.dataset.val)) wrap.style.backgroundColor = '';
            });
            
            btn.addEventListener('mouseenter', () => btn.style.backgroundColor = '#e0e0e0');
            btn.addEventListener('mouseleave', () => btn.style.backgroundColor = 'transparent');
            
            btn.addEventListener('mousedown', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const originalText = getOptionLabel(wrap.dataset.val);
                optLabel.innerHTML = `<input type="text" class="notion-ms-label-edit" value="${originalText}" style="width:100%; border:1px solid #2ea2ff; outline:none; border-radius:3px; padding:2px;">`;
                btn.style.display = 'none';
                const editInput = optLabel.querySelector('input');
                editInput.focus();
                
                const saveLabel = async () => {
                    const newVal = editInput.value.trim();
                    if (newVal && newVal !== originalText) {
                        if(!notionData.optionLabels) notionData.optionLabels = {};
                        notionData.optionLabels[wrap.dataset.val] = newVal;
                        
                        await fetch('/api/schemas/option_labels', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(notionData.optionLabels)
                        });
                        
                        optLabel.innerHTML = newVal;
                        renderTags();
                    } else {
                        optLabel.innerHTML = originalText;
                    }
                    input.focus();
                };
                
                editInput.addEventListener('blur', saveLabel);
                editInput.addEventListener('keydown', (ev) => {
                    if (ev.key === 'Enter') {
                        ev.preventDefault();
                        ev.stopPropagation();
                        editInput.blur();
                    }
                    if (ev.key === 'Escape') {
                        ev.preventDefault();
                        ev.stopPropagation();
                        optLabel.innerHTML = originalText;
                        input.focus();
                    }
                });
            });
            
            wrap.addEventListener('mousedown', (e) => {
                if (e.target.closest('.notion-ms-edit-btn') || e.target.closest('.notion-ms-label-edit')) return;
                e.preventDefault(); // prevent blur
                const val = wrap.dataset.val;
                if (!currentVals.includes(val)) {
                    currentVals.push(val);
                } else {
                    currentVals = currentVals.filter(v => v !== val);
                }
                input.value = '';
                input.dispatchEvent(new Event('input')); // trigger filter update
                renderTags();
                input.focus();
            });
        });

        const saveFn = async () => {
            td.classList.remove('editing');
            
            const originalVals = Array.isArray(row[prop.key]) ? row[prop.key] : (row[prop.key] ? String(row[prop.key]).split(',').map(s=>s.trim()).filter(s=>s) : []);
            if (JSON.stringify(currentVals) === JSON.stringify(originalVals)) {
                td.innerHTML = originalHtml;
                return;
            }

            try {
                const endpoint = tableName === 'songs' ? '/api/songs' : '/api/artists';
                const payload = {};
                payload[prop.key] = currentVals; // Send as array
                
                const res = await fetch(`${endpoint}/${id}`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                if(result.success) {
                    row[prop.key] = currentVals;
                    td.innerHTML = renderCell(prop, row);
                } else {
                    throw new Error(result.error);
                }
            } catch(e) {
                alert('保存失敗: ' + e);
                td.innerHTML = originalHtml;
            }
        };

        input.addEventListener('blur', (e) => {
            // Delay slightly to check where focus moved
            setTimeout(() => {
                if (container.contains(document.activeElement)) {
                    // Focus moved to another input inside the dropdown (like the edit label input)
                    return;
                }
                saveFn();
            }, 10);
        });
        input.addEventListener('keydown', (e) => {
            if(e.key === 'Enter') {
                e.preventDefault(); 
                const visibleOpts = optionWraps.filter(o => o.style.display !== 'none');
                if (input.value && visibleOpts.length === 1 && !currentVals.includes(visibleOpts[0].dataset.val)) {
                    currentVals.push(visibleOpts[0].dataset.val);
                    input.value = '';
                    input.dispatchEvent(new Event('input'));
                    renderTags();
                } else {
                    input.blur(); // Save and exit
                }
            }
            if(e.key === 'Escape') {
                td.innerHTML = originalHtml;
                td.classList.remove('editing');
            }
        });
        
        return;
    }

    let inputHtml = `<input type="text" class="notion-inline-input" value="${row[prop.key] || ''}">`;
    if(prop.type === 'select' && prop.options) {
        inputHtml = `<select class="notion-inline-input"><option value=""></option>${prop.options.map(o => `<option value="${o}" ${row[prop.key]===o?'selected':''}>${o}</option>`).join('')}</select>`;
    }
    
    td.innerHTML = inputHtml;
    const input = td.querySelector('.notion-inline-input, select');
    input.focus();
    
    const saveFn = async () => {
        td.classList.remove('editing');
        let newVal = input.value;
        if(newVal === String(row[prop.key] || '')) {
            td.innerHTML = originalHtml;
            return;
        }
        
        try {
            const endpoint = tableName === 'songs' ? '/api/songs' : '/api/artists';
            const payload = {};
            payload[prop.key] = newVal;
            
            const res = await fetch(`${endpoint}/${id}`, {
                method: 'PATCH',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const result = await res.json();
            if(result.success) {
                row[prop.key] = newVal;
                td.innerHTML = renderCell(prop, row);
            } else {
                throw new Error(result.error);
            }
        } catch(e) {
            alert('保存失敗: ' + e);
            td.innerHTML = originalHtml;
        }
    };
    
    input.addEventListener('blur', saveFn);
    input.addEventListener('keydown', (e) => {
        if(e.key === 'Enter') input.blur();
        if(e.key === 'Escape') {
            td.innerHTML = originalHtml;
            td.classList.remove('editing');
        }
    });
}



window.openSchemaManager = function() {
    const viewDef = databaseViews[currentViewKey];
    if(!viewDef) return;

    const overlay = document.createElement('div');
    overlay.className = 'notion-prop-modal-overlay';
    
    // The 9 supported types
    const types = [
        { id: 'text', label: 'テキスト' },
        { id: 'number', label: '数値' },
        { id: 'select', label: '選択' },
        { id: 'multiselect', label: 'マルチセレクト' },
        { id: 'date', label: '日付' },
        { id: 'checkbox', label: 'チェックボックス' },
        { id: 'url', label: 'URL' },
        { id: 'relation', label: 'リレーション' },
        { id: 'rollup', label: 'ロールアップ' }
    ];
    
    const listHtml = types.map(t => `
        <div class="notion-prop-item" data-type="${t.id}">
            <div class="notion-prop-icon">${NOTION_ICONS[t.id] || NOTION_ICONS['text']}</div>
            <span>${t.label}</span>
        </div>
    `).join('');

    overlay.innerHTML = `
        <div class="notion-prop-modal" onclick="event.stopPropagation()">
            <div class="notion-prop-input-wrap">
                <input type="text" class="notion-prop-input" placeholder="プロパティ名" autofocus>
            </div>
            <div class="notion-prop-list">
                ${listHtml}
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    
    const input = overlay.querySelector('.notion-prop-input');
    input.focus();
    
    // Close on click outside
    overlay.addEventListener('click', () => {
        document.body.removeChild(overlay);
    });
    
    // Item click
    overlay.querySelectorAll('.notion-prop-item').forEach(item => {
        item.addEventListener('click', () => {
            const name = input.value.trim() || '新規プロパティ';
            const type = item.getAttribute('data-type');
            document.body.removeChild(overlay);
            
            fetch('/api/schemas', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    target_table: viewDef.target_table,
                    key: 'custom_' + Date.now(),
                    label: name,
                    type: type
                })
            }).then(() => {
                initNotionUI();
            });
        });
    });
};


window.openViewConfig = async function() {
    const viewDef = databaseViews[currentViewKey];
    if(!viewDef) return;
    
    const allProps = getPropertiesForTable(viewDef.target_table);
    
        let currentProps = viewDef.config.properties || allProps.map(p => ({key: p.key, visible: true}));
    let newProps = await window.showPropertyVisibilityModal(allProps, currentProps);
    if(newProps) {
        viewDef.config.properties = newProps;
        
        let typeRes = await window.customPrompt("ビュータイプ (table または board):", viewDef.type);
        if(typeRes === 'table' || typeRes === 'board') {
            viewDef.type = typeRes;
            if(typeRes === 'board') {
                viewDef.config.board_group_by = await window.customPrompt("Boardのグループ化キー (select または relationのキー):", viewDef.config.board_group_by || 'tag_a');
            }
        }
        
        fetch('/api/views_config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(viewDef)
        }).then(() => initNotionUI());
    }
};

window.addNewRow = async function() {
    const viewDef = databaseViews[currentViewKey];
    const endpoint = viewDef.target_table === 'songs' ? '/api/songs' : '/api/artists';
    
    const res = await fetch(endpoint, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({}) });
    if(res.ok) {
        initNotionUI();
    }
};

window.createNewView = async function() {
    const name = await window.customPrompt("新しいビューの名前:");
    if(!name) return;
    const target = await window.customPrompt("対象テーブル (songs または artists):", "songs");
    
    fetch('/api/views_config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            target_table: target,
            name: name,
            type: 'table',
            config: {}
        })
    }).then(() => initNotionUI());
};

function renderBoard(viewDef, data, allProps) {
    const groupByKey = viewDef.config.board_group_by || 'tag_a';
    const groupProp = allProps.find(p => p.key === groupByKey);
    
    let groups = {};
    if(groupProp && groupProp.options) {
        groupProp.options.forEach(opt => groups[opt] = []);
    }
    groups['No Group'] = [];
    
    data.forEach(row => {
        let val = row[groupByKey];
        if(!val) groups['No Group'].push(row);
        else if(groups[val]) groups[val].push(row);
        else groups['No Group'].push(row); // fallback
    });
    
    let html = '<div class="notion-board-container" style="display:flex; gap: 20px; overflow-x: auto; padding: 20px;">';
    
    Object.keys(groups).forEach(gKey => {
        html += `<div class="notion-board-column" data-group="${gKey}" style="width: 250px; background: #f7f7f5; border-radius: 5px; padding: 10px;">`;
        html += `<h3 style="margin-top:0; font-size: 14px; color: #37352f;">${gKey} <span style="color:#999;">${groups[gKey].length}</span></h3>`;
        html += `<div class="notion-board-cards" data-group="${gKey}" ondragover="event.preventDefault();" ondrop="dropBoardCard(event, '${gKey}')" style="min-height: 100px;">`;
        
        groups[gKey].forEach(row => {
            html += `<div class="notion-board-card" draggable="true" ondragstart="dragBoardCard(event, ${row.id})" style="background: white; padding: 10px; margin-bottom: 8px; border-radius: 3px; box-shadow: rgba(15, 15, 15, 0.1) 0px 0px 0px 1px; cursor: grab;">`;
            html += `<strong>${row.title || row.name || '無題'}</strong>`;
            html += `</div>`;
        });
        
        html += `</div></div>`;
    });
    
    html += '</div>';
    return html;
}

window.dragBoardCard = function(e, id) {
    e.dataTransfer.setData('text/plain', id);
};

window.dropBoardCard = async function(e, newGroup) {
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain');
    if(!id) return;
    
    const viewDef = databaseViews[currentViewKey];
    const groupByKey = viewDef.config.board_group_by;
    const endpoint = viewDef.target_table === 'songs' ? '/api/songs' : '/api/artists';
    
    let val = newGroup === 'No Group' ? null : newGroup;
    
    try {
        const payload = {};
        payload[groupByKey] = val;
        
        const res = await fetch(`${endpoint}/${id}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if(res.ok) {
            initNotionUI();
        }
    } catch(err) {
        alert("更新エラー: " + err);
    }
};

window.searchArtistYoutube = function(name) {
    window.location.hash = '#youtube';
    navigate();
    setTimeout(() => {
        const input = document.getElementById('yt-search-keyword');
        if(input) {
            input.value = name;
            searchYoutube();
        }
    }, 100); // small delay to ensure DOM is ready
};


let currentConfigColKey = null;
let currentConfigTableName = null;

window.editColumnLabel = function(tableName, colKey, oldLabel, event) {
    if(window.notionUIMode === 'original') return; // Do not allow editing in original mode
    
    currentConfigTableName = tableName;
    currentConfigColKey = colKey;
    
    let modal = document.getElementById('notion-prop-config-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'notion-prop-config-modal';
        modal.className = 'notion-prop-config-modal';
        document.body.appendChild(modal);
        
        // click outside to close
        document.addEventListener('click', (e) => {
            if (modal.style.display === 'flex' && !modal.contains(e.target) && !e.target.closest('.notion-th')) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Get property details
    const viewDef = databaseViews[currentViewKey];
    const allProps = getPropertiesForTable(tableName);
    const prop = allProps.find(p => p.key === colKey);
    if (!prop) return;
    
    // Parse options (settings)
    let settings = {};
    if (prop.options) {
        try { settings = JSON.parse(prop.options) || {}; } catch(e) {}
    }
    
    // Build UI
    let bodyHtml = '';
    
    if (prop.type === 'number_float' || prop.type === 'number_integer') {
        const format = settings.format || 'number';
        bodyHtml += `
            <div class="notion-prop-config-group">
                <label>数値の形式</label>
                <select id="prop-cfg-format">
                    <option value="number" ${format==='number'?'selected':''}>数値</option>
                    <option value="comma" ${format==='comma'?'selected':''}>カンマ区切り</option>
                    <option value="percent" ${format==='percent'?'selected':''}>パーセント</option>
                    <option value="currency" ${format==='currency'?'selected':''}>通貨 (¥)</option>
                </select>
            </div>
        `;
    } else if (prop.type === 'relation_read' || prop.type === 'relation_write') {
        const targetDb = settings.target_db || (tableName === 'songs' ? 'artists' : 'songs');
        const limit = settings.limit || 'multiple';
        bodyHtml += `
            <div class="notion-prop-config-group">
                <label>関連付け先</label>
                <select id="prop-cfg-target-db">
                    <option value="songs" ${targetDb==='songs'?'selected':''}>曲DB</option>
                    <option value="artists" ${targetDb==='artists'?'selected':''}>歌手DB</option>
                </select>
            </div>
            <div class="notion-prop-config-group">
                <label>制限</label>
                <select id="prop-cfg-limit">
                    <option value="multiple" ${limit==='multiple'?'selected':''}>複数選択可能</option>
                    <option value="single" ${limit==='single'?'selected':''}>1つのみ</option>
                </select>
            </div>
        `;
    } else if (prop.type === 'formula') {
        const expr = settings.expression || '';
        const propsTags = allProps.map(p => `<span class="notion-tag" style="cursor:pointer;" onclick="insertToFormula('prop(\\'${p.label}\\')')">${p.label}</span>`).join(' ');
        bodyHtml += `
            <div class="notion-prop-config-group">
                <label>関数の式</label>
                <textarea id="prop-cfg-expr" placeholder="例: if(prop('views') > 1000, '人気', '')" style="min-height:60px;">${expr}</textarea>
            </div>
            <div class="notion-prop-config-group">
                <label style="margin-bottom:4px; display:block;">プロパティ (クリックして挿入)</label>
                <div style="display:flex; flex-wrap:wrap; gap:4px; max-height:100px; overflow-y:auto; padding-top:4px;">
                    ${propsTags}
                </div>
            </div>
        `;
    } else if (prop.type === 'rollup') {
        const targetProp = settings.target_prop || '';
        const calc = settings.calculate || 'original';
        const relatedTable = tableName === 'songs' ? 'artists' : 'songs';
        const relatedProps = getPropertiesForTable(relatedTable);
        const targetPropOptions = relatedProps.map(p => `<option value="${p.key}" ${targetProp === p.key ? 'selected' : ''}>${p.label}</option>`).join('');

        bodyHtml += `
            <div class="notion-prop-config-group">
                <label>リレーション先</label>
                <input type="text" id="prop-cfg-rel-prop" value="${tableName === 'songs' ? '歌手DB' : '曲DB'}" disabled>
            </div>
            <div class="notion-prop-config-group">
                <label>対象プロパティ</label>
                <select id="prop-cfg-target-prop" class="notion-input">
                    ${targetPropOptions}
                </select>
            </div>
            <div class="notion-prop-config-group">
                <label>計算方法</label>
                <select id="prop-cfg-calc">
                    <option value="original" ${calc==='original'?'selected':''}>元の値の表示</option>
                    <option value="sum" ${calc==='sum'?'selected':''}>合計</option>
                    <option value="average" ${calc==='average'?'selected':''}>平均</option>
                    <option value="max" ${calc==='max'?'selected':''}>最大</option>
                    <option value="min" ${calc==='min'?'selected':''}>最小</option>
                    <option value="count_all" ${calc==='count_all'?'selected':''}>空ではない件数</option>
                </select>
            </div>
        `;
    } else if (prop.type === 'select' || prop.type === 'multi_select') {
        const optsStr = settings.choices ? settings.choices.join(', ') : '';
        bodyHtml += `
            <div class="notion-prop-config-group">
                <label>オプション一覧 (カンマ区切り)</label>
                <input type="text" id="prop-cfg-choices" value="${optsStr}" placeholder="例: Pop, Rock, Jazz">
            </div>
        `;
    } else {
        bodyHtml += `<div style="font-size:12px; color:#888;">このタイプには固有の設定項目はありません。</div>`;
    }
    
    modal.innerHTML = `
        <div class="notion-prop-config-header">
            ${getPropertyIcon(prop.type)}
            <input type="text" id="prop-cfg-label" value="${prop.label}">
        </div>
        <div class="notion-prop-config-body">
            <div class="notion-prop-config-group">
                <label>プロパティタイプ</label>
                <input type="text" value="${prop.type}" disabled>
            </div>
            ${bodyHtml}
        </div>
        <div class="notion-prop-config-footer">
            <button class="notion-btn-primary" onclick="saveColumnConfig()">保存</button>
        </div>
    `;
    
    // Position modal
    const rect = event.currentTarget.getBoundingClientRect();
    modal.style.left = `${rect.left}px`;
    modal.style.top = `${rect.bottom + 4}px`;
    modal.style.display = 'flex';
};

window.saveColumnConfig = async function() {
    if(!currentConfigColKey || !currentConfigTableName) return;
    const modal = document.getElementById('notion-prop-config-modal');
    
    const newLabel = document.getElementById('prop-cfg-label').value;
    const allProps = getPropertiesForTable(currentConfigTableName);
    const prop = allProps.find(p => p.key === currentConfigColKey);
    
    let settings = {};
    if (prop.options) {
        try { settings = JSON.parse(prop.options) || {}; } catch(e) {}
    }
    
    if (prop.type === 'number_float' || prop.type === 'number_integer') {
        settings.format = document.getElementById('prop-cfg-format').value;
    } else if (prop.type === 'relation_read' || prop.type === 'relation_write') {
        settings.target_db = document.getElementById('prop-cfg-target-db').value;
        settings.limit = document.getElementById('prop-cfg-limit').value;
    } else if (prop.type === 'formula') {
        settings.expression = document.getElementById('prop-cfg-expr').value;
    } else if (prop.type === 'rollup') {
        settings.relation_prop = document.getElementById('prop-cfg-rel-prop').value;
        settings.target_prop = document.getElementById('prop-cfg-target-prop').value;
        settings.calculate = document.getElementById('prop-cfg-calc').value;
    } else if (prop.type === 'select' || prop.type === 'multi_select') {
        const str = document.getElementById('prop-cfg-choices').value;
        settings.choices = str.split(',').map(s => s.trim()).filter(s => s);
    }
    
    // If it's a custom schema, we can save to DB. For hardcoded, we save to localStorage or DB if supported.
    // For simplicity, we'll send it to /api/schemas/update_property.
    
    try {
        const res = await fetch('/api/schemas/update_property', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                target_table: currentConfigTableName,
                key: currentConfigColKey,
                label: newLabel,
                options: JSON.stringify(settings)
            })
        });
        const data = await res.json();
        if (data.success) {
            modal.style.display = 'none';
            // Also save label locally to not wait for reload
            if (newLabel !== prop.label) {
                let saved = {};
                try { saved = JSON.parse(localStorage.getItem('customLabels') || '{}'); } catch(e) {}
                if(!saved[currentConfigTableName]) saved[currentConfigTableName] = {};
                saved[currentConfigTableName][currentConfigColKey] = newLabel;
                localStorage.setItem('customLabels', JSON.stringify(saved));
            }
            // Update in memory options
            prop.options = JSON.stringify(settings);
            
            // Re-render
            const content = document.getElementById('notion-view-content');
            if (databaseViews[currentViewKey]) {
                const targetTable = databaseViews[currentViewKey].target_table;
                const endpoint = targetTable === 'songs' ? '/api/database_view/songs' : '/api/database_view/artists';
                const resp = await fetch(endpoint);
                const tableData = await resp.json();
                renderTable(databaseViews[currentViewKey], tableData, allProps);
            }
        } else {
            alert('設定の保存に失敗しました: ' + data.error);
        }
    } catch(e) {
        alert('通信エラー: ' + e);
    }
};

window.getSelectedIds = function() {
    const checkboxes = document.querySelectorAll('.notion-row-select:checked');
    return Array.from(checkboxes).map(cb => {
        const tr = cb.closest('tr');
        return parseInt(tr.getAttribute('data-id'));
    });
};

window.bulkDelete = async function() {
    const ids = getSelectedIds();
    if(ids.length === 0) return;
    
    const viewDef = databaseViews[currentViewKey];
    if(!confirm(`選択した${ids.length}件を削除しますか？`)) return;
    
    const endpoint = viewDef.target_table === 'songs' ? '/api/songs/' : '/api/artists/';
    
    try {
        for(let id of ids) {
            await fetch(endpoint + id, { method: 'DELETE' });
        }
        await fetchNotionData();
        renderCurrentView();
    } catch(e) {
        alert('削除エラー: ' + e);
    }
};

window.bulkMerge = async function() {
    const ids = getSelectedIds();
    if(ids.length < 2) return;
    
    const targetId = ids[0];
    const targetRow = notionData.songs.find(s => s.id === targetId);
    
    let newTitle = prompt('統合後の曲名を入力してください:', targetRow.title || '');
    if(newTitle === null) return; // Cancelled
    
    try {
        const res = await fetch('/api/songs/merge', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                source_ids: ids,
                target_id: targetId,
                new_title: newTitle,
                main_artist_id: targetRow.main_artist_id,
                sub_artist_ids: []
            })
        });
        const data = await res.json();
        if(data.success) {
            await fetchNotionData();
            renderCurrentView();
            alert('曲を統合しました。');
        } else {
            alert('統合エラー: ' + data.error);
        }
    } catch(e) {
        alert('通信エラー: ' + e);
    }
};


const NOTION_ICONS = {
    'title': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M2.5 4h9v1.5h-9zM2.5 7h9v1.5h-9zM2.5 10h6v1.5h-6z"></path></svg>',
    'text': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M2.5 4h9v1.5h-9zM2.5 7h9v1.5h-9zM2.5 10h6v1.5h-6z"></path></svg>',
    'number': '<div style="font-weight:600;font-size:12px;opacity:0.6;width:14px;text-align:center;">#</div>',
    'select': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M7 12A5 5 0 1 1 7 2a5 5 0 0 1 0 10zm0-1.5A3.5 3.5 0 1 0 7 3.5a3.5 3.5 0 0 0 0 7zM5 6l2 3 2-3H5z"></path></svg>',
    'multiselect': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M1 3h12v1.5H1V3zm0 3.25h12v1.5H1v-1.5zm0 3.25h12V11H1V9.5z"></path></svg>',
    'date': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M11 2h-1V1h-1.5v1h-3V1H4v1H3c-.8 0-1.5.7-1.5 1.5v8c0 .8.7 1.5 1.5 1.5h8c.8 0 1.5-.7 1.5-1.5v-8C12.5 2.7 11.8 2 11 2zm0 9.5H3V5h8v6.5z"></path></svg>',
    'checkbox': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M2 2v10h10V2H2zm8.5 3.5L6 10 3.5 7.5l1-1L6 8l3.5-3.5 1 1z"></path></svg>',
    'url': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M8.5 4H10A3 3 0 1 1 10 10H8.5v-1.5H10A1.5 1.5 0 1 0 10 5.5H8.5V4zM5.5 10H4A3 3 0 1 1 4 4h1.5v1.5H4A1.5 1.5 0 1 0 4 8.5h1.5V10zM4 6h6v1.5H4V6z"></path></svg>',
    'relation': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M10.5 3.5l-4 4-1-1 4-4H6.5v-1.5h5.5v5.5H10.5v-3zM2 12V2h3v1.5H3.5v7h7V9H12v3H2z"></path></svg>',
    'rollup': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M12.5 11.5l-3-3a4.5 4.5 0 1 0-1 1l3 3 1-1zM6.5 9.5a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"></path></svg>'
};

function getPropertyIcon(type) {
    if(type === 'title') return '';
    if(NOTION_ICONS[type]) return NOTION_ICONS[type];
    if(type === 'number_float') return NOTION_ICONS['number'];
    if(type === 'relation_read') return NOTION_ICONS['relation'];
    if(type === 'checkbox_3state') return NOTION_ICONS['checkbox'];
    return NOTION_ICONS['text']; // default
}



// --- Formula Evaluator ---
function evaluateFormula(expr, row, allProps) {
    if(!expr || typeof expr !== 'string') return '';
    try {
        // Simple string replacements for Notion-like syntax
        // prop("Name") -> row.key
        let parsed = expr;
        
        // Match prop("...") or prop('...')
        parsed = parsed.replace(/prop\(['"]([^'"]+)['"]\)/g, (match, label) => {
            const propDef = allProps.find(p => p.label === label || p.key === label);
            if(propDef) {
                let val = row[propDef.key];
                if(val === undefined || val === null) return 'null';
                if(typeof val === 'string') return `"${val.replace(/"/g, '\"')}"`;
                return val;
            }
            return 'null';
        });
        
        // and, or
        parsed = parsed.replace(/\band\b/gi, '&&');
        parsed = parsed.replace(/\bor\b/gi, '||');
        
        // if(cond, true, false)
        // This is tricky with simple regex if there are nested ifs. 
        // For a simple case: if(a, b, c) -> (a ? b : c)
        // We can do a rudimentary parsing for `if(...)`
        while(parsed.includes('if(')) {
            parsed = parsed.replace(/if\(([^,]+),([^,]+),([^)]+)\)/gi, '($1 ? $2 : $3)');
        }
        
        // Evaluate
        // Using Function constructor is safer than eval, but still has risks. In a local UI, it's fine.
        const func = new Function(`return ${parsed};`);
        return func();
    } catch(e) {
        console.warn("Formula evaluation error:", e, expr);
        return 'Error';
    }
}


window.openViewEditMenu = function(key) {
    const view = databaseViews[key];
    if (!view) return;
    
    const existing = document.getElementById('view-edit-modal');
    if (existing) existing.remove();
    
    const modalHtml = `
        <div id="view-edit-modal" style="position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); z-index: 10000; display:flex; align-items:center; justify-content:center;">
            <div class="modal-content" style="width: 300px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 1px solid var(--border-color);">
                <h3 style="margin-top:0; font-size: 16px; margin-bottom: 16px; color: var(--text-primary);">ビュー設定</h3>
                <div class="form-group" style="margin-bottom: 16px;">
                    <label style="display:block; margin-bottom: 8px; font-size: 12px; color: var(--text-secondary);">ビュー名</label>
                    <input type="text" id="view-edit-name" class="notion-input" style="width: 100%; box-sizing: border-box;" value="${view.name}">
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <button class="notion-btn notion-btn-danger" onclick="deleteView('${key}')" style="color: var(--danger-color); border-color: var(--danger-color);">削除</button>
                    <div style="display: flex; gap: 8px;">
                        <button class="notion-btn" onclick="document.getElementById('view-edit-modal').remove()">キャンセル</button>
                        <button class="notion-btn-primary" onclick="renameView('${key}')" style="background: var(--primary-color); color: white; border: none; padding: 4px 12px; border-radius: 4px; cursor: pointer;">保存</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
};

window.renameView = async function(key) {
    const newName = document.getElementById('view-edit-name').value.trim();
    if (!newName) return;
    const view = databaseViews[key];
    if (newName === view.name) {
        document.getElementById('view-edit-modal').remove();
        return;
    }
    
    try {
        const configStr = view.config ? (typeof view.config === 'string' ? view.config : JSON.stringify(view.config)) : '{}';
        const res = await fetch('/api/views_config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                view_id: key,
                target_table: view.target_table,
                name: newName,
                type: view.type,
                config_str: configStr
            })
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById('view-edit-modal').remove();
            await fetchNotionData();
            renderNotionContainer();
        } else {
            alert('保存エラー: ' + data.error);
        }
    } catch(e) {
        alert('通信エラー: ' + e);
    }
};

window.deleteView = async function(key) {
    if (Object.keys(databaseViews).length <= 1) {
        alert('最後のビューは削除できません。');
        return;
    }
    if (!confirm('本当にこのビューを削除しますか？')) return;
    
    try {
        const res = await fetch('/api/views_config/' + key, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            document.getElementById('view-edit-modal').remove();
            
            if (currentViewKey === key) {
                const remainingKeys = Object.keys(databaseViews).filter(k => k !== key);
                currentViewKey = remainingKeys[0];
                const url = new URL(window.location);
                url.searchParams.set('view', currentViewKey);
                window.history.pushState({}, '', url);
            }
            
            await fetchNotionData();
            renderNotionContainer();
        } else {
            alert('削除エラー: ' + data.error);
        }
    } catch(e) {
        alert('通信エラー: ' + e);
    }
};

window.insertToFormula = function(text) {
    const ta = document.getElementById('prop-cfg-expr');
    if (!ta) return;
    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    const val = ta.value;
    ta.value = val.substring(0, start) + text + val.substring(end);
    ta.selectionStart = ta.selectionEnd = start + text.length;
    ta.focus();
};
