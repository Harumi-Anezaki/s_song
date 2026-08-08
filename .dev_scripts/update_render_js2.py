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

m = re.search(r'function renderNotionContainer\(\)\s*\{', text)
if m:
    pos = m.end()
    injection = "\n    const root = document.getElementById('notion-root');\n    if(window.notionUIMode === 'original') root.classList.add('notion-mode-original'); else root.classList.remove('notion-mode-original');"
    text = text[:pos] + injection + text[pos:]
    text = text.replace('\n', '\r\n')
    with open('core/static/js/notion_ui.js', 'wb') as f:
        f.write(text.encode(enc, errors='replace'))
    print("Injected into renderNotionContainer")
