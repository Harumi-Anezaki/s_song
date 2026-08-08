import codecs
import re

# 1. Update app.js
with codecs.open('core/static/js/app.js', 'r', 'utf-8') as f:
    app_js = f.read()

nav_old = """    if (hash === 'database' || databaseViews[hash]) {
        viewContent.style.display = 'none';
        notionRoot.style.display = 'flex';
        // Initialize notion UI if it's the first time
        if (typeof initNotionUI === 'function') {
            initNotionUI();
        }
    } else {"""
nav_new = """    if (hash === 'database' || hash === 'dbviewer' || databaseViews[hash]) {
        viewContent.style.display = 'none';
        notionRoot.style.display = 'flex';
        
        let newMode = (hash === 'dbviewer') ? 'original' : 'linked';
        
        if (typeof initNotionUI === 'function') {
            window.notionUIMode = newMode;
            initNotionUI(newMode);
        }
    } else {"""

app_js = app_js.replace(nav_old, nav_new)
with codecs.open('core/static/js/app.js', 'w', 'utf-8') as f:
    f.write(app_js)

# 2. Update notion_ui.js
with codecs.open('core/static/js/notion_ui.js', 'r', 'utf-8') as f:
    notion_js = f.read()

init_old = """async function initNotionUI() {
    await fetchNotionData();
    
    if (Object.keys(databaseViews).length === 0) {
        // Create default views if none exist
        await createDefaultViews();
    }
    
    // routing check
    const urlParams = new URLSearchParams(window.location.search);
    const viewParam = urlParams.get('view');
    if (viewParam && databaseViews[viewParam]) {
        currentViewKey = viewParam;
    } else {
        currentViewKey = Object.keys(databaseViews)[0];
    }
    
    renderNotionContainer();
}"""

init_new = """async function initNotionUI(mode) {
    window.notionUIMode = mode;
    await fetchNotionData();
    
    if (mode === 'original') {
        // DB原本モード: 曲と歌手の固定ビューを生成（全カラム強制表示）
        const songsProps = getPropertiesForTable('songs').map(p => ({key: p.key, visible: true}));
        const artistsProps = getPropertiesForTable('artists').map(p => ({key: p.key, visible: true}));
        
        databaseViews = {
            'original_songs': {
                id: 'original_songs',
                name: '曲_原本',
                type: 'table',
                target_table: 'songs',
                config: { properties: songsProps, sorts: [], filters: [] }
            },
            'original_artists': {
                id: 'original_artists',
                name: '歌手_原本',
                type: 'table',
                target_table: 'artists',
                config: { properties: artistsProps, sorts: [], filters: [] }
            }
        };
        // URLのhashを使ってViewを記憶しない（単純に最初のViewを表示）
        if (!currentViewKey || !databaseViews[currentViewKey]) {
            currentViewKey = 'original_songs';
        }
    } else {
        // リンクドDBモード: サーバーから取得したビューを使用
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
}"""

notion_js = notion_js.replace(init_old, init_new)

# Disable adding views in original mode
add_view_old = """            <div class="view-tab" onclick="createNewView()" style="color: var(--text-gray);">
                +
            </div>"""
add_view_new = """            ${window.notionUIMode === 'original' ? '' : `
            <div class="view-tab" onclick="createNewView()" style="color: var(--text-gray);">
                +
            </div>`}"""
notion_js = notion_js.replace(add_view_old, add_view_new)

# Disable filter and properties buttons in original mode
tools_old = """        <div class="notion-view-tools" style="display:flex; gap:16px;">
            <div class="tool-btn" onclick="toggleFilterModal()">
                <svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M1 2.5h12v1.5H1zM3 6.5h8v1.5H3zM5.5 10.5h3v1.5h-3z"></path></svg>
                tB^[ <span id="filter-count" style="color: var(--text-gray); font-size: 12px; margin-left:4px;"></span>
            </div>
            <div class="tool-btn" onclick="toggleSortModal()">
                <svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M2.5 1h1.5v12h-1.5zM6 3.5h7v1.5H6zM6 6.5h5v1.5H6zM6 9.5h3v1.5H6z"></path></svg>
                \[g <span id="sort-count" style="color: var(--text-gray); font-size: 12px; margin-left:4px;"></span>
            </div>
            <div class="tool-btn" onclick="togglePropsModal()">
                <svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M2 3.5h10v1.5H2zM2 6.5h10v1.5H2zM2 9.5h10v1.5H2z"></path></svg>
                vpeB
            </div>
            <div class="tool-btn" onclick="openGlobalSearch()">
                <svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M6 1a5 5 0 1 0 3.1 8.9l3.2 3.2 1-1-3.2-3.2A5 5 0 0 0 6 1zm0 1.5a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7z"></path></svg>
                
            </div>
        </div>"""

tools_new = """        <div class="notion-view-tools" style="display:flex; gap:16px;">
            ${window.notionUIMode === 'original' ? '' : `
            <div class="tool-btn" onclick="toggleFilterModal()">
                <svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M1 2.5h12v1.5H1zM3 6.5h8v1.5H3zM5.5 10.5h3v1.5h-3z"></path></svg>
                フィルター <span id="filter-count" style="color: var(--text-gray); font-size: 12px; margin-left:4px;"></span>
            </div>
            <div class="tool-btn" onclick="toggleSortModal()">
                <svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M2.5 1h1.5v12h-1.5zM6 3.5h7v1.5H6zM6 6.5h5v1.5H6zM6 9.5h3v1.5H6z"></path></svg>
                ソート <span id="sort-count" style="color: var(--text-gray); font-size: 12px; margin-left:4px;"></span>
            </div>
            <div class="tool-btn" onclick="togglePropsModal()">
                <svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M2 3.5h10v1.5H2zM2 6.5h10v1.5H2zM2 9.5h10v1.5H2z"></path></svg>
                プロパティ
            </div>`}
            <div class="tool-btn" onclick="openGlobalSearch()">
                <svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M6 1a5 5 0 1 0 3.1 8.9l3.2 3.2 1-1-3.2-3.2A5 5 0 0 0 6 1zm0 1.5a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7z"></path></svg>
                検索
            </div>
        </div>"""

# Ensure the encoding is correct for the template literal string replace
# Since original string has mojibake, we'll use a regex search for the block
m = re.search(r'<div class="notion-view-tools"[^>]*>.*?</svg>\s*[^<]*\s*</div>\s*</div>', notion_js, re.DOTALL)
if m:
    notion_js = notion_js.replace(m.group(0), tools_new)

with codecs.open('core/static/js/notion_ui.js', 'w', 'utf-8') as f:
    f.write(notion_js)

print("Updated Notion modes")
