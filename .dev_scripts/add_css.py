with open('core/static/css/notion.css', 'r', encoding='utf-8') as f:
    content = f.read()

styles = """
/* Bulk Action Bar */
.notion-bulk-action-bar {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background-color: #2f3437;
    color: white;
    padding: 12px 24px;
    border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 16px;
    z-index: 1000;
    font-size: 14px;
    transition: opacity 0.2s, transform 0.2s;
    opacity: 0;
    pointer-events: none;
}
.notion-bulk-action-bar.visible {
    opacity: 1;
    pointer-events: auto;
    transform: translateX(-50%) translateY(-10px);
}
.notion-bulk-btn {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.3);
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background 0.1s;
}
.notion-bulk-btn:hover {
    background: rgba(255,255,255,0.1);
}
.notion-bulk-btn.delete {
    color: #eb5757;
    border-color: rgba(235, 87, 87, 0.3);
}
.notion-bulk-btn.delete:hover {
    background: rgba(235, 87, 87, 0.1);
}
"""

if '.notion-bulk-action-bar' not in content:
    with open('core/static/css/notion.css', 'a', encoding='utf-8') as f:
        f.write(styles)
    print("Added styles")
else:
    print("Styles already exist")
