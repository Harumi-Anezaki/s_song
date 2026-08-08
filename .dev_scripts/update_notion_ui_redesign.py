import codecs
import re

with codecs.open('core/static/js/notion_ui.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update renderNotionContainer
render_container_old = r"""        <div class="notion-header">
            <div class="notion-tabs">
                \$\{Object\.keys\(databaseViews\)\.map\(key => `
                    <div class="notion-tab \$\{key === currentViewKey \? 'active' : ''\}" onclick="switchNotionView\('\$\{key\}'\)">
                        \$\{databaseViews\[key\]\.name\}
                    </div>
                `\)\.join\(''\)\}
                <div class="notion-tab" onclick="createNewView\(\)">{</div>
            </div>
            <div class="notion-toolbar">
                <button class="notion-btn" onclick="addNewRow\(\)">{VKR[h</button>
                <button class="notion-btn" onclick="deleteSelectedRows\(\)">폜</button>
                <span style="border-left: 1px solid #ccc; margin: 0 8px;"></span>
                <button class="notion-btn" onclick="openSchemaManager\(\)">{ǉ \(Schema\)</button>
                <button class="notion-btn" onclick="openViewConfig\(\)">r[ݒ</button>
            </div>
        </div>"""

render_container_new = """        <div class="notion-header">
            <div class="notion-tabs">
                ${Object.keys(databaseViews).map(key => `
                    <div class="notion-tab ${key === currentViewKey ? 'active' : ''}" onclick="switchNotionView('${key}')">
                        <svg viewBox="0 0 14 14" style="width:14px;height:14px;fill:currentColor;opacity:0.6;"><path d="M1.5 1.5v11h11v-11h-11zM11.5 2.5v3h-3.5v-3h3.5zM7 2.5v3h-4.5v-3h4.5zM2.5 6.5h4.5v5h-4.5v-5zM8 11.5v-5h3.5v5h-3.5z"></path></svg>
                        ${databaseViews[key].name}
                    </div>
                `).join('')}
                <div class="notion-tab" onclick="createNewView()">＋</div>
            </div>
            <div class="notion-toolbar">
                <button class="notion-btn" title="絞り込み (Filter)">≡</button>
                <button class="notion-btn" title="並び替え (Sort)">⇅</button>
                <button class="notion-btn" title="自動化 (Lightning)">⚡</button>
                <button class="notion-btn" title="検索 (Search)">🔍</button>
                <button class="notion-btn" onclick="openViewConfig()" title="設定 (Settings)">⧂</button>
                <button class="notion-btn-primary" onclick="addNewRow()">新規 ⌄</button>
            </div>
        </div>"""

content = re.sub(r'        <div class="notion-header">.*?</div>\s*</div>', render_container_new, content, flags=re.DOTALL)


# 2. Add function to get icon for property
icon_func = """
function getPropertyIcon(type) {
    if (type === 'title') return '<div style="font-weight:600;font-size:12px;opacity:0.6;font-family:serif;width:14px;text-align:center;">Aa</div>';
    if (type === 'multiselect') return '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M1 3h12v1.5h-12v-1.5zM1 6.25h12v1.5h-12v-1.5zM1 9.5h12v1.5h-12v-1.5z"></path></svg>';
    if (type === 'select') return '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M7 10l-4-5h8z"></path></svg>';
    if (type === 'number' || type === 'number_float' || type === 'formula_trend') return '<div style="font-weight:600;font-size:12px;opacity:0.6;width:14px;text-align:center;">#</div>';
    if (type === 'date') return '<div style="font-size:12px;opacity:0.6;width:14px;text-align:center;">🕒</div>';
    if (type === 'relation' || type === 'relation_read') return '<div style="font-size:12px;opacity:0.6;width:14px;text-align:center;">↗</div>';
    if (type === 'checkbox' || type === 'checkbox_3state') return '<svg viewBox="0 0 14 14" class="notion-th-icon"><path d="M1 1v12h12v-12h-12zM12 12h-10v-10h10v10zM10.5 4.5l-4 4.5-2.5-2.5-1 1 3.5 3.5 5-5.5z"></path></svg>';
    return '<div style="font-size:12px;opacity:0.6;width:14px;text-align:center;">≡</div>';
}
"""

if 'function getPropertyIcon' not in content:
    content += icon_func


# 3. Update renderTable
renderTable_old = r"""    visibleProps.forEach\(prop => \{
        html \+= `<th class="notion-th" data-key="\$\{prop\.key\}" draggable="true" onclick="editColumnLabel\('\$\{viewDef\.target_table\}', '\$\{prop\.key\}', '\$\{prop\.label\.replace\('/g, "\\\\'\)"\)'\)">\$\{prop\.label\}</th>`;
    \}\);
    html \+= '</tr></thead><tbody>';"""

renderTable_new = """    visibleProps.forEach(prop => {
        html += `<th class="notion-th" data-key="${prop.key}" draggable="true" onclick="editColumnLabel('${viewDef.target_table}', '${prop.key}', '${prop.label.replace(/'/g, "\\'")}')">
            <div class="notion-th-content">
                ${getPropertyIcon(prop.type)}
                ${prop.label}
            </div>
        </th>`;
    });
    html += '<th class="notion-th" style="width:40px;text-align:center;cursor:pointer;" onclick="openSchemaManager()">＋</th>';
    html += '<th class="notion-th" style="width:40px;text-align:center;">...</th>';
    html += '</tr></thead><tbody>';"""

content = re.sub(r'    visibleProps\.forEach\(prop => \{.*?html \+= \'</tr></thead><tbody>\';', renderTable_new, content, flags=re.DOTALL)


# 4. Update renderTable rows for empty TDs
row_old = r"""        visibleProps\.forEach\(prop => \{
            html \+= `<td class="notion-td" data-key="\$\{prop\.key\}">\$\{renderCell\(prop, row\)\}</td>`;
        \}\);
        html \+= '</tr>';"""

row_new = """        visibleProps.forEach(prop => {
            html += `<td class="notion-td" data-key="${prop.key}">${renderCell(prop, row)}</td>`;
        });
        html += '<td class="notion-td"></td><td class="notion-td"></td>';
        html += '</tr>';"""

content = re.sub(r'        visibleProps\.forEach\(prop => \{.*?html \+= \'</tr>\';', row_new, content, flags=re.DOTALL)


# 5. Update renderCell title icon
renderCell_old = r"""    if \(prop\.type === 'title'\) \{
        return `<span class="notion-title-text">\$\{val \|\| ''\}</span>`;
    \}"""

renderCell_new = """    if (prop.type === 'title') {
        return `<div style="display:flex; align-items:center; gap:6px;"><span style="opacity:0.5;">📄</span><span class="notion-title-text" style="font-weight:500;">${val || ''}</span></div>`;
    }"""

content = re.sub(r'    if \(prop\.type === \'title\'\) \{.*?\}', renderCell_new, content, flags=re.DOTALL)

with codecs.open('core/static/js/notion_ui.js', 'w', 'utf-8') as f:
    f.write(content)

print("Updated notion_ui.js UI!")
