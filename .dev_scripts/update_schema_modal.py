import codecs
import re

# 1. Update notion.css
with codecs.open('core/static/css/notion.css', 'r', 'utf-8') as f:
    css_content = f.read()

new_css = """
/* Property Create Modal */
.notion-prop-modal-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: transparent; /* Click outside to close */
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
}
.notion-prop-modal {
    background: white;
    border-radius: 6px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1), 0 0 0 1px rgba(0,0,0,0.05);
    width: 240px;
    max-height: 400px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif;
}
.notion-prop-input-wrap {
    padding: 8px;
    border-bottom: 1px solid rgba(233, 233, 231, 1);
}
.notion-prop-input {
    width: 100%;
    border: none;
    outline: none;
    padding: 4px;
    font-size: 14px;
    background: transparent;
}
.notion-prop-list {
    overflow-y: auto;
    padding: 6px 0;
}
.notion-prop-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    cursor: pointer;
    font-size: 14px;
    color: #37352f;
    transition: background 20ms ease-in 0s;
}
.notion-prop-item:hover {
    background: rgba(15, 15, 15, 0.05);
}
.notion-prop-icon {
    width: 16px;
    height: 16px;
    fill: rgba(55, 53, 47, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
}
"""

if '.notion-prop-modal' not in css_content:
    with codecs.open('core/static/css/notion.css', 'a', 'utf-8') as f:
        f.write(new_css)


# 2. Update notion_ui.js
with codecs.open('core/static/js/notion_ui.js', 'r', 'utf-8') as f:
    js_content = f.read()

icons_js = """
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
    if(NOTION_ICONS[type]) return NOTION_ICONS[type];
    if(type === 'title') return NOTION_ICONS['text'];
    if(type === 'number_float' || type === 'formula_trend') return NOTION_ICONS['number'];
    if(type === 'relation_read') return NOTION_ICONS['relation'];
    if(type === 'checkbox_3state') return NOTION_ICONS['checkbox'];
    return NOTION_ICONS['text']; // default
}
"""

# Replace old getPropertyIcon
old_icon_func = re.search(r'function getPropertyIcon\(type\) \{.*?\n\}', js_content, re.DOTALL)
if old_icon_func:
    js_content = js_content.replace(old_icon_func.group(0), icons_js)
elif 'const NOTION_ICONS' not in js_content:
    js_content += '\n' + icons_js

modal_js = """
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
"""

# Replace old openSchemaManager
old_schema_func = re.search(r'window\.openSchemaManager = async function\(\) \{.*?\n\};', js_content, re.DOTALL)
if old_schema_func:
    js_content = js_content.replace(old_schema_func.group(0), modal_js)
elif 'window.openSchemaManager = function()' not in js_content:
    js_content += '\n' + modal_js

with codecs.open('core/static/js/notion_ui.js', 'w', 'utf-8') as f:
    f.write(js_content)

print("Updated schema modal!")
