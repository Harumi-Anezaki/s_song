import os

def replace_in_file(filepath, target_bytes, replacement_bytes):
    with open(filepath, 'rb') as f:
        content = f.read()
    
    if target_bytes in content:
        content = content.replace(target_bytes, replacement_bytes)
        with open(filepath, 'wb') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"Target not found in {filepath}")

app_target = b"""    if (hash === 'database' || databaseViews[hash]) {
        viewContent.style.display = 'none';
        notionRoot.style.display = 'flex';
        // Initialize notion UI if it's the first time
        if (typeof initNotionUI === 'function') {
            initNotionUI();
        }
    } else {"""

app_repl = b"""    if (hash === 'database' || hash === 'dbviewer' || databaseViews[hash]) {
        viewContent.style.display = 'none';
        notionRoot.style.display = 'flex';
        let newMode = (hash === 'dbviewer') ? 'original' : 'linked';
        // Initialize notion UI if it's the first time
        if (typeof initNotionUI === 'function') {
            initNotionUI(newMode);
        }
    } else {"""

replace_in_file('core/static/js/app.js', app_target, app_repl)

notion_target = b"""async function initNotionUI() {
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

notion_repl = b"""async function initNotionUI(mode) {
    window.notionUIMode = mode || 'linked';
    await fetchNotionData();
    
    if (window.notionUIMode === 'original') {
        const songsProps = getPropertiesForTable('songs').map(p => ({key: p.key, visible: true}));
        const artistsProps = getPropertiesForTable('artists').map(p => ({key: p.key, visible: true}));
        databaseViews = {
            'original_songs': {
                id: 'original_songs',
                name: '\\xe6\\x9b\\xb2_\\xe5\\x8e\\x9f\\xe6\\x9c\\xac',
                type: 'table',
                target_table: 'songs',
                config: { properties: songsProps, sorts: [], filters: [] }
            },
            'original_artists': {
                id: 'original_artists',
                name: '\\xe6\\xad\\x8c\\xe6\\x89\\x8b_\\xe5\\x8e\\x9f\\xe6\\x9c\\xac',
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
}"""

replace_in_file('core/static/js/notion_ui.js', notion_target, notion_repl)
