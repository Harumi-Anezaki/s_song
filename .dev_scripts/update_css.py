import codecs

with codecs.open('core/static/css/notion.css', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update tabs
content = content.replace(""".notion-tab {
    padding: 6px 12px;
    cursor: pointer;
    font-size: 14px;
    color: #555;
    border-bottom: 2px solid transparent;
}""", """.notion-tab {
    padding: 6px 12px;
    cursor: pointer;
    font-size: 14px;
    color: rgba(55, 53, 47, 0.65);
    border-radius: 6px;
    transition: background 120ms ease-in 0s;
    display: flex;
    align-items: center;
    gap: 6px;
}""")

content = content.replace(""".notion-tab.active {
    font-weight: 600;
    color: #333;
    border-bottom: 2px solid #333;
}""", """.notion-tab.active {
    font-weight: 500;
    color: #37352f;
    background: rgba(15, 15, 15, 0.05);
}""")

content = content.replace(""".notion-tabs {
    display: flex;
    gap: 16px;
    border-bottom: 1px solid #f0f0f0;
}""", """.notion-tabs {
    display: flex;
    gap: 4px;
    /* no bottom border to match notion */
}""")

# 2. Update Toolbar and Button
content = content.replace(""".notion-toolbar {
    display: flex;
    gap: 8px;
}""", """.notion-toolbar {
    display: flex;
    gap: 4px;
    align-items: center;
    margin-left: auto; /* Push to right */
}
.notion-header {
    border-bottom: 1px solid rgba(233, 233, 231, 1);
    padding: 12px 24px;
    background: #fff;
    display: flex;
    flex-direction: row; /* Horizontal layout */
    align-items: center;
    gap: 8px;
}
""")

content = content.replace(""".notion-btn {
    background: none;
    border: none;
    padding: 4px 8px;
    font-size: 13px;
    color: #555;
    cursor: pointer;
    border-radius: 4px;
}""", """.notion-btn {
    background: none;
    border: none;
    padding: 4px 8px;
    font-size: 14px;
    color: rgba(55, 53, 47, 0.65);
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
}
.notion-btn-primary {
    background: #2eaadc;
    color: white;
    border: none;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 4px;
}
.notion-btn-primary:hover {
    background: #0091df;
}
""")

# 3. Update Th and Td
content = content.replace(""".notion-th, .notion-th-checkbox, .notion-td, .notion-td-checkbox {
    border: 1px solid #e9e9e9;
    padding: 8px;
    vertical-align: middle;
}""", """.notion-th, .notion-th-checkbox, .notion-td, .notion-td-checkbox {
    border: 1px solid rgba(233, 233, 231, 1);
    padding: 8px 12px;
    vertical-align: middle;
}""")

content = content.replace(""".notion-th, .notion-th-checkbox {
    position: sticky;
    top: 0;
    background: #fbfbfb;
    color: #666;
    font-weight: 500;
    z-index: 10;
    resize: horizontal;
    overflow: hidden;
}""", """.notion-th, .notion-th-checkbox {
    position: sticky;
    top: 0;
    background: #fff;
    color: rgba(55, 53, 47, 0.65);
    font-weight: normal;
    font-size: 13px;
    z-index: 10;
    resize: horizontal;
    overflow: hidden;
    cursor: pointer;
    display: table-cell; /* to allow SVG and text alignment */
}
.notion-th:hover {
    background: rgba(15, 15, 15, 0.05);
}
.notion-th-content {
    display: flex;
    align-items: center;
    gap: 6px;
}
.notion-th-icon {
    width: 14px;
    height: 14px;
    fill: rgba(55, 53, 47, 0.45);
}
""")

# 4. Update notion-tag to match Pill
content = content.replace(""".notion-tag {
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 12px;
    margin-right: 4px;
    display: inline-block;
    color: #fff;
}""", """.notion-tag {
    border-radius: 12px;
    padding: 2px 8px;
    font-size: 12px;
    margin-right: 4px;
    display: inline-block;
    color: #37352f;
    background: rgba(227, 226, 224, 0.5); /* Default gray */
    border: 1px solid transparent;
}""")

with codecs.open('core/static/css/notion.css', 'w', 'utf-8') as f:
    f.write(content)
print("CSS updated")
