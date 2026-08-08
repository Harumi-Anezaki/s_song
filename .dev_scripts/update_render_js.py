import re

with open('core/static/js/notion_ui.js', 'rb') as f:
    content = f.read()

try:
    text = content.decode('utf-8')
    enc = 'utf-8'
except:
    text = content.decode('shift_jis', errors='ignore')
    enc = 'shift_jis'

text = text.replace('\r\n', '\n')

render_target = "function renderNotionContainer() {\n    const root = document.getElementById('notion-root');\n    const viewDef = databaseViews[currentViewKey];"
render_repl = "function renderNotionContainer() {\n    const root = document.getElementById('notion-root');\n    if(window.notionUIMode === 'original') root.classList.add('notion-mode-original'); else root.classList.remove('notion-mode-original');\n    const viewDef = databaseViews[currentViewKey];"

if render_target in text:
    text = text.replace(render_target, render_repl)
    text = text.replace('\n', '\r\n')
    with open('core/static/js/notion_ui.js', 'wb') as f:
        f.write(text.encode(enc, errors='replace'))
    print("Updated renderNotionContainer in notion_ui.js")
else:
    print("Not found in notion_ui.js")
