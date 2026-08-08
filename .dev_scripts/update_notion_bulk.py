import codecs
import re

with codecs.open('core/static/js/notion_ui.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add Bulk Action Bar HTML to renderNotionContainer
html_injection = """        </div>
        
        <div id="notion-bulk-action-bar" class="notion-bulk-action-bar">
            <span id="notion-bulk-count">0件選択中</span>
            <button class="notion-bulk-btn delete" onclick="bulkDelete()">削除</button>
            <button id="notion-bulk-btn-merge" class="notion-bulk-btn" onclick="bulkMerge()">曲統合</button>
        </div>
    `;"""

if '<div id="notion-bulk-action-bar"' not in content:
    content = content.replace('        </div>\n    `;', html_injection)


# 2. Update attachTableEvents to handle checkboxes
attach_old = """function attachTableEvents(viewDef, data, allProps) {
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
}"""

attach_new = """function attachTableEvents(viewDef, data, allProps) {
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
}"""

if attach_old in content:
    content = content.replace(attach_old, attach_new)


# 3. Add bulk logic functions
bulk_logic = """
function getSelectedIds() {
    const checkboxes = document.querySelectorAll('.notion-row-select:checked');
    return Array.from(checkboxes).map(cb => {
        const tr = cb.closest('tr');
        return parseInt(tr.getAttribute('data-id'));
    });
}

function updateBulkActionBar(tableName) {
    const bar = document.getElementById('notion-bulk-action-bar');
    const countSpan = document.getElementById('notion-bulk-count');
    const mergeBtn = document.getElementById('notion-bulk-btn-merge');
    if(!bar) return;
    
    const count = getSelectedIds().length;
    if (count > 0) {
        countSpan.innerText = count + '件選択中';
        bar.classList.add('visible');
        if (tableName === 'songs' && count >= 2) {
            mergeBtn.style.display = 'inline-block';
        } else {
            mergeBtn.style.display = 'none';
        }
    } else {
        bar.classList.remove('visible');
    }
}

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
"""

if 'function updateBulkActionBar' not in content:
    content += bulk_logic

with codecs.open('core/static/js/notion_ui.js', 'w', 'utf-8') as f:
    f.write(content)

print("Updated notion_ui.js!")
