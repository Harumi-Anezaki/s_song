import os

def replace_in_file(filepath, target_str, repl_str):
    with open(filepath, 'rb') as f:
        content = f.read()
        
    # try utf-8 decode
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

app_target = """    if (hash === 'database' || databaseViews[hash]) {
        viewContent.style.display = 'none';
        notionRoot.style.display = 'flex';
        // Initialize notion UI if it's the first time
        if (typeof initNotionUI === 'function') {
            initNotionUI();
        }
    } else {"""

app_repl = """    if (hash === 'database' || hash === 'dbviewer' || databaseViews[hash]) {
        viewContent.style.display = 'none';
        notionRoot.style.display = 'flex';
        let newMode = (hash === 'dbviewer') ? 'original' : 'linked';
        // Initialize notion UI if it's the first time
        if (typeof initNotionUI === 'function') {
            initNotionUI(newMode);
        }
    } else {"""

replace_in_file('core/static/js/app.js', app_target, app_repl)

