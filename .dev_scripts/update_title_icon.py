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

# Find getPropertyIcon
target_str = """function getPropertyIcon(type) {
    if(NOTION_ICONS[type]) return NOTION_ICONS[type];
    if(type === 'title') return NOTION_ICONS['text'];"""

repl_str = """function getPropertyIcon(type) {
    if(type === 'title') return '';
    if(NOTION_ICONS[type]) return NOTION_ICONS[type];"""

if target_str in text:
    text = text.replace(target_str, repl_str)
    text = text.replace('\n', '\r\n')
    with open('core/static/js/notion_ui.js', 'wb') as f:
        f.write(text.encode(enc, errors='replace'))
    print("Updated getPropertyIcon in notion_ui.js")
else:
    print("Target not found. Doing a fallback replace.")
    fallback_target = "if(type === 'title') return NOTION_ICONS['text'];"
    fallback_repl = "if(type === 'title') return '';"
    if fallback_target in text:
        text = text.replace(fallback_target, fallback_repl)
        text = text.replace('\n', '\r\n')
        with open('core/static/js/notion_ui.js', 'wb') as f:
            f.write(text.encode(enc, errors='replace'))
        print("Updated getPropertyIcon with fallback")
    else:
        print("Still not found.")
