import random
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, Response, jsonify

app = Flask(__name__)

default_colors = {
    "BACKGROUND": "#000000", "FOREGROUND": "#0088FF", "HICOLOR1": "#00BB66",
    "HICOLOR2": "#0066CC", "CONSOLECOLOR": "#000000", "CURSORCOLOR": "#00BB66",
    "INFOCOLOR": "#0088FF", "WARNCOLOR": "#00AA55", "ERRORCOLOR": "#CC3333",
    "ACCENTCOLOR": "#00AA55", "ACCENTALTCOLOR": "#0066CC", "EMPHASISCOLOR": "#00AA55"
}

TRACKER_ROWS = [f"{i:02X}" for i in range(0x10)]
TRACKER_COLS = 8


@app.route('/')
def index():
    return render_template(
        'index.html',
        colors=default_colors,
        tracker_rows=TRACKER_ROWS,
        tracker_cols=TRACKER_COLS,
    )


@app.route('/import', methods=['POST'])
def import_theme():
    if 'file' not in request.files: return "No file", 400
    file = request.files['file']
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        imported_colors = {}
        for color in root.findall('Color'):
            name = color.get('name')
            value = color.get('value')
            if name in default_colors: imported_colors[name] = value
        return jsonify(imported_colors)
    except: return "Invalid file", 500


@app.route('/randomize')
def randomize():
    def r_c(): return "#%06x" % random.randint(0, 0xFFFFFF)
    bg = r_c()
    fg = "#FFFFFF" if sum(int(bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) < 380 else "#000000"
    return jsonify({k: r_c() for k in default_colors.keys()} | {"BACKGROUND": bg, "FOREGROUND": fg, "EMPHASISCOLOR": fg})


@app.route('/download', methods=['POST'])


def download():
    name = request.form.get('theme_name', 'custom').strip() or "custom"
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<THEME>\n  <Font value="#1" />\n'
    for k in default_colors.keys():
        xml += f'  <Color name="{k}" value="{request.form.get(k, default_colors[k]).upper()}" />\n'
    xml += '</THEME>'


    return Response(xml, mimetype='application/octet-stream', headers={"Content-disposition": f"attachment; filename={name}.ptt"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
