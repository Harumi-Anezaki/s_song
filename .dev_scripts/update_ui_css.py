import os
import re

def replace_in_file(filepath, target_str, repl_str):
    with open(filepath, 'rb') as f:
        content = f.read()
    try:
        text = content.decode('utf-8')
        enc = 'utf-8'
    except:
        text = content.decode('shift_jis', errors='ignore')
        enc = 'shift_jis'
        
    text = text.replace('\r\n', '\n')
    
    if target_str in text:
        text = text.replace(target_str, repl_str)
        text = text.replace('\n', '\r\n')
        with open(filepath, 'wb') as f:
            f.write(text.encode(enc, errors='replace'))
        print(f"Updated {filepath}")
    else:
        print(f"Target not found in {filepath}")

add_view_target = """            <div class="view-tab" onclick="createNewView()" style="color: var(--text-gray);">
                +
            </div>"""

add_view_repl = """            ${window.notionUIMode === 'original' ? '' : `
            <div class="view-tab" onclick="createNewView()" style="color: var(--text-gray);">
                +
            </div>`}"""

replace_in_file('core/static/js/notion_ui.js', add_view_target, add_view_repl)

# For tools, we will use regex replacement directly on text
with open('core/static/js/notion_ui.js', 'rb') as f:
    content = f.read()
try:
    text = content.decode('utf-8')
    enc = 'utf-8'
except:
    text = content.decode('shift_jis', errors='ignore')
    enc = 'shift_jis'

text = text.replace('\r\n', '\n')

m = re.search(r'<div class="notion-view-tools"[^>]*>.*?</svg>\s*[^<]*\s*</div>\s*</div>', text, re.DOTALL)
if m:
    tools_block = m.group(0)
    # We want to wrap filter, sort, properties with ${window.notionUIMode === 'original' ? '' : ` ... `}
    # It's safer to just dynamically add a class or style, but we can also just do the template literal string replace.
    # Actually, simpler: in renderNotionContainer, just hide them with CSS!
    pass

# Simpler way to hide UI elements in original mode:
# Add a class to notionRoot or handle it in JS.
# Let's just add it to renderNotionContainer:
render_target = """function renderNotionContainer() {
    const root = document.getElementById('notion-root');
    const viewDef = databaseViews[currentViewKey];"""
    
render_repl = """function renderNotionContainer() {
    const root = document.getElementById('notion-root');
    const viewDef = databaseViews[currentViewKey];
    if (window.notionUIMode === 'original') {
        root.classList.add('notion-mode-original');
    } else {
        root.classList.remove('notion-mode-original');
    }"""

if render_target in text:
    text = text.replace(render_target, render_repl)
    text = text.replace('\n', '\r\n')
    with open('core/static/js/notion_ui.js', 'wb') as f:
        f.write(text.encode(enc, errors='replace'))
    print("Updated renderNotionContainer")
