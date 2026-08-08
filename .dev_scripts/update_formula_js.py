import codecs
import re

with codecs.open('core/static/js/notion_ui.js', 'r', 'utf-8') as f:
    js = f.read()

formula_js = """
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
                if(typeof val === 'string') return `"${val.replace(/"/g, '\\"')}"`;
                return val;
            }
            return 'null';
        });
        
        // and, or
        parsed = parsed.replace(/\\band\\b/gi, '&&');
        parsed = parsed.replace(/\\bor\\b/gi, '||');
        
        // if(cond, true, false)
        // This is tricky with simple regex if there are nested ifs. 
        // For a simple case: if(a, b, c) -> (a ? b : c)
        // We can do a rudimentary parsing for `if(...)`
        while(parsed.includes('if(')) {
            parsed = parsed.replace(/if\\(([^,]+),([^,]+),([^)]+)\\)/gi, '($1 ? $2 : $3)');
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
"""

if 'function evaluateFormula' not in js:
    js += '\n' + formula_js


# Update renderCell to use formula
renderCell_old = r"""    if \(prop\.type === 'title'\) \{
        return `<div style="display:flex; align-items:center; gap:6px;"><span style="opacity:0.5;">📄</span><span class="notion-title-text" style="font-weight:500;">\$\{val \|\| ''\}</span></div>`;
    \} else if \(prop\.type === 'select'\) \{"""

renderCell_new = """    if (prop.type === 'title') {
        return `<div style="display:flex; align-items:center; gap:6px;"><span style="opacity:0.5;">📄</span><span class="notion-title-text" style="font-weight:500;">${val || ''}</span></div>`;
    } else if (prop.type === 'formula') {
        // Evaluate formula
        const allProps = getPropertiesForTable(databaseViews[currentViewKey].target_table);
        const expr = prop.options && prop.options.expression ? prop.options.expression : '';
        const res = evaluateFormula(expr, row, allProps);
        return res !== null && res !== undefined ? res : '';
    } else if (prop.type === 'select') {"""

js = re.sub(renderCell_old, renderCell_new, js, flags=re.DOTALL)


# Update NOTION_ICONS to include formula
icons_old = r"""    'rollup': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M12\.5 11\.5l-3-3a4\.5 4\.5 0 1 0-1 1l3 3 1-1zM6\.5 9\.5a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"></path></svg>'\n\};"""
icons_new = """    'rollup': '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M12.5 11.5l-3-3a4.5 4.5 0 1 0-1 1l3 3 1-1zM6.5 9.5a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"></path></svg>',
    'formula': '<div style="font-weight:600;font-size:12px;opacity:0.6;width:14px;text-align:center;">Σ</div>'
};"""

js = js.replace(icons_old, icons_new)

# Add formula to schema manager
schema_types_old = r"\{ id: 'rollup', label: 'ロールアップ' \}"
schema_types_new = "{ id: 'rollup', label: 'ロールアップ' },\n        { id: 'formula', label: '関数 (Formula)' }"
js = js.replace(schema_types_old, schema_types_new)


# Update editColumnLabel to handle formula edits
edit_old = r"""window\.editColumnLabel = async function\(targetTable, key, currentLabel\) \{
    let newLabel = await window\.customPrompt\("カラム名を変更:", currentLabel\);
    if\(!newLabel \|\| newLabel === currentLabel\) return;"""

edit_new = """window.editColumnLabel = async function(targetTable, key, currentLabel) {
    const allProps = getPropertiesForTable(targetTable);
    const prop = allProps.find(p => p.key === key);
    
    let newLabel = await window.customPrompt("カラム名を変更:", currentLabel);
    if(!newLabel) return;
    
    let newExpr = null;
    if (prop && prop.type === 'formula') {
        let currentExpr = prop.options && prop.options.expression ? prop.options.expression : '';
        newExpr = await window.customPrompt("関数の式 (Formula) を編集:\\n例: if(prop('A') < 10, 'Yes', 'No')", currentExpr);
    }
    
    if(newLabel === currentLabel && (newExpr === null || (prop.options && newExpr === prop.options.expression))) return;
"""

js = re.sub(edit_old, edit_new, js, flags=re.DOTALL)

# Update fetch body in editColumnLabel
fetch_old = r"""    fetch\('/api/schemas/update', \{
        method: 'POST',
        headers: \{'Content-Type': 'application/json'\},
        body: JSON\.stringify\(\{
            target_table: targetTable,
            key: key,
            label: newLabel
        \}\)
    \}\)"""

fetch_new = """    let bodyData = {
        target_table: targetTable,
        key: key,
        label: newLabel
    };
    if (prop && prop.type === 'formula') {
        bodyData.options = { expression: newExpr };
    }
    
    fetch('/api/schemas/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(bodyData)
    })"""

js = re.sub(fetch_old, fetch_new, js, flags=re.DOTALL)

with codecs.open('core/static/js/notion_ui.js', 'w', 'utf-8') as f:
    f.write(js)

print("Updated JS with formula parsing and UI")
