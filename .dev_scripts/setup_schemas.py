import codecs
import re
import sqlite3
import json

# 1. Add /api/schemas/update to app.py
with codecs.open('core/app.py', 'r', 'utf-8') as f:
    app_py = f.read()

update_api = """
@app.route('/api/schemas/update', methods=['POST'])
def api_update_schema():
    data = request.json
    try:
        with get_db() as conn:
            # Check if exists
            row = conn.execute("SELECT * FROM custom_schemas WHERE target_table = ? AND key = ?", (data['target_table'], data['key'])).fetchone()
            if row:
                options_str = json.dumps(data.get('options', [])) if data.get('options') else row['options']
                conn.execute("UPDATE custom_schemas SET label = ?, options = ? WHERE id = ?", (data['label'], options_str, row['id']))
            else:
                # If it's a base schema, we can't update it in DB unless we create it as a custom schema override.
                # Actually, we can just insert it as a custom schema override!
                import uuid
                new_id = f"schema_{uuid.uuid4().hex[:8]}"
                options_str = json.dumps(data.get('options', [])) if data.get('options') else None
                conn.execute(\"\"\"
                    INSERT INTO custom_schemas (id, target_table, key, label, type, options)
                    VALUES (?, ?, ?, ?, ?, ?)
                \"\"\", (new_id, data['target_table'], data['key'], data['label'], data.get('type', 'text'), options_str))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""

if '/api/schemas/update' not in app_py:
    app_py = app_py.replace("@app.route('/api/views_config', methods=['GET'])", update_api + "\n@app.route('/api/views_config', methods=['GET'])")
    with codecs.open('core/app.py', 'w', 'utf-8') as f:
        f.write(app_py)


# 2. Update editColumnLabel in notion_ui.js
with codecs.open('core/static/js/notion_ui.js', 'r', 'utf-8') as f:
    js = f.read()

edit_old = r"""window\.editColumnLabel = function\(tableName, colKey, oldLabel\) \{
    let newLabel = prompt\('新しく入力してください:', oldLabel\);
    if \(newLabel && newLabel !== oldLabel\) \{
        let saved = \{\};
        try \{ saved = JSON\.parse\(localStorage\.getItem\('customLabels'\) \|\| '\{\}'\); \} catch\(e\) \{\}
        if\(!saved\[tableName\]\) saved\[tableName\] = \{\};
        saved\[tableName\]\[colKey\] = newLabel;
        localStorage\.setItem\('customLabels', JSON\.stringify\(saved\)\);
        
        // Also update viewDef.config.properties label if present
        const viewDef = databaseViews\[currentViewKey\];
        if \(viewDef && viewDef\.config\.properties\) \{
             const vp = viewDef\.config\.properties\.find\(p => p\.key === colKey\);
             if\(vp\) vp\.label = newLabel;
        \}
        renderCurrentView\(\);
    \}
\};"""

edit_new = """window.editColumnLabel = async function(tableName, colKey, oldLabel) {
    const allProps = getPropertiesForTable(tableName);
    const prop = allProps.find(p => p.key === colKey);
    
    let newLabel = await window.customPrompt("カラム名を変更:", oldLabel);
    if(!newLabel) return;
    
    let newExpr = null;
    let isFormula = prop && (prop.type === 'formula' || prop.type === 'formula_trend' || colKey === 'is_outdated');
    
    if (isFormula) {
        let currentExpr = prop.options && prop.options.expression ? prop.options.expression : '';
        // For is_outdated default formula
        if (!currentExpr && colKey === 'is_outdated') {
            currentExpr = 'if(prop("total_views") < prop("view_threshold") && prop("views_per_day") < prop("vpd_threshold"), "時代遅れ", "")';
        }
        newExpr = await window.customPrompt("関数の式 (Formula) を編集:\\n例: if(prop('A') < 10, 'Yes', 'No')", currentExpr);
    }
    
    // Save locally for quick update
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem('customLabels') || '{}'); } catch(e) {}
    if(!saved[tableName]) saved[tableName] = {};
    saved[tableName][colKey] = newLabel;
    localStorage.setItem('customLabels', JSON.stringify(saved));
    
    // Also save expression locally for quick update
    if (isFormula && newExpr !== null) {
        let savedExpr = {};
        try { savedExpr = JSON.parse(localStorage.getItem('customExpr') || '{}'); } catch(e) {}
        if(!savedExpr[tableName]) savedExpr[tableName] = {};
        savedExpr[tableName][colKey] = newExpr;
        localStorage.setItem('customExpr', JSON.stringify(savedExpr));
    }
    
    // Update view config label
    const viewDef = databaseViews[currentViewKey];
    if (viewDef && viewDef.config.properties) {
         const vp = viewDef.config.properties.find(p => p.key === colKey);
         if(vp) vp.label = newLabel;
    }
    
    // Sync with backend (will create custom schema override)
    let bodyData = {
        target_table: tableName,
        key: colKey,
        label: newLabel,
        type: isFormula ? 'formula' : (prop ? prop.type : 'text')
    };
    if (isFormula && newExpr !== null) {
        bodyData.options = { expression: newExpr };
    }
    
    fetch('/api/schemas/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(bodyData)
    });
    
    renderCurrentView();
};"""

js = re.sub(edit_old, edit_new, js, flags=re.DOTALL)


# Update getPropertiesForTable to load formula overrides from localstorage or custom schemas
props_old = r"""    let saved = \{\};
    try \{ saved = JSON\.parse\(localStorage\.getItem\('customLabels'\) \|\| '\{\}'\); \} catch\(e\) \{\}
    if\(saved\[tableName\]\) \{
        props = props\.map\(p => \{
            if\(saved\[tableName\]\[p\.key\]\) \{
                return \{\.\.\.p, label: saved\[tableName\]\[p\.key\]\};
            \}
            return p;
        \}\);
    \}
    
    return props;"""

props_new = """    let saved = {};
    try { saved = JSON.parse(localStorage.getItem('customLabels') || '{}'); } catch(e) {}
    let savedExpr = {};
    try { savedExpr = JSON.parse(localStorage.getItem('customExpr') || '{}'); } catch(e) {}
    
    props = props.map(p => {
        let newP = {...p};
        // Override label
        if(saved[tableName] && saved[tableName][p.key]) {
            newP.label = saved[tableName][p.key];
        }
        // Override expression for formula
        if(savedExpr[tableName] && savedExpr[tableName][p.key]) {
            newP.options = newP.options || {};
            newP.options.expression = savedExpr[tableName][p.key];
            if(p.type === 'formula_trend') newP.type = 'formula';
        }
        return newP;
    });
    
    // Deduplicate custom_schemas overrides (if custom_schema has same key as baseSchema)
    let finalProps = [];
    let keys = new Set();
    for(let p of props.reverse()) { // reverse so custom_schemas take precedence
        if(!keys.has(p.key)) {
            keys.add(p.key);
            finalProps.unshift(p);
        }
    }
    
    return finalProps;"""

js = re.sub(props_old, props_new, js, flags=re.DOTALL)

with codecs.open('core/static/js/notion_ui.js', 'w', 'utf-8') as f:
    f.write(js)


# 3. Seed database schemas
import uuid
def insert_schema(conn, target, key, label, type, expression=None):
    # Check if exists
    exists = conn.execute("SELECT 1 FROM custom_schemas WHERE target_table=? AND key=?", (target, key)).fetchone()
    if exists: return
    new_id = f"schema_{uuid.uuid4().hex[:8]}"
    options = json.dumps({"expression": expression}) if expression else None
    conn.execute("INSERT INTO custom_schemas (id, target_table, key, label, type, options) VALUES (?, ?, ?, ?, ?, ?)",
                 (new_id, target, key, label, type, options))

with sqlite3.connect('data/app.db') as conn:
    # Artists table
    insert_schema(conn, 'artists', 'name', '名前', 'title')
    insert_schema(conn, 'artists', 'rating', '歌手_好き度', 'number')
    insert_schema(conn, 'artists', 'singability', '歌手_歌いやすさ', 'number')
    insert_schema(conn, 'artists', 'main_songs', '歌手_曲(メイン)', 'relation')
    insert_schema(conn, 'artists', 'sub_songs', '歌手_曲(サブ)', 'relation')
    
    # We will compute total_views and views_per_day dynamically in evaluateFormula or JS
    insert_schema(conn, 'artists', 'total_views_calc', '歌手_再生数', 'rollup')
    insert_schema(conn, 'artists', 'vpd_calc', '歌手_回/日', 'rollup')
    
    # Thresholds are just returned from backend
    insert_schema(conn, 'artists', 'view_threshold', '歌手_再生数_上位70%', 'formula', 'prop("view_threshold")')
    insert_schema(conn, 'artists', 'vpd_threshold', '歌手_回/日_上位70%', 'formula', 'prop("vpd_threshold")')
    
    # Songs table "流行" formula
    # "if(prop('total_views') < prop('view_threshold') and prop('views_per_day') < prop('vpd_threshold'), '時代遅れ', '')"
    trend_expr = 'if(prop("total_views") < prop("view_threshold") && prop("views_per_day") < prop("vpd_threshold"), "時代遅れ", "")'
    insert_schema(conn, 'songs', 'is_outdated', '流行', 'formula', trend_expr)
    
    conn.commit()

print("App update complete")
