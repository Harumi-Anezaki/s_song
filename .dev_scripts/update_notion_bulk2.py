import codecs
import re

with codecs.open('core/static/js/notion_ui.js', 'r', 'utf-8') as f:
    content = f.read()

target = r'<div id="notion-view-content" class="notion-view-content"></div>\s*`;'
replace = """<div id="notion-view-content" class="notion-view-content"></div>
        
        <div id="notion-bulk-action-bar" class="notion-bulk-action-bar">
            <span id="notion-bulk-count">0件選択中</span>
            <button class="notion-bulk-btn delete" onclick="bulkDelete()">削除</button>
            <button id="notion-bulk-btn-merge" class="notion-bulk-btn" onclick="bulkMerge()">曲統合</button>
        </div>
    `;"""

if re.search(target, content):
    content = re.sub(target, replace, content)
    with codecs.open('core/static/js/notion_ui.js', 'w', 'utf-8') as f:
        f.write(content)
    print("Injected bulk action bar HTML!")
else:
    print("Target not found.")
