import random
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, Response, jsonify

app = Flask(__name__)

default_colors = {
    "BACKGROUND": "#008080", "FOREGROUND": "#000000", "HICOLOR1": "#FFFFFF",
    "HICOLOR2": "#C0C0C0", "CONSOLECOLOR": "#000080", "CURSORCOLOR": "#000000",
    "INFOCOLOR": "#000080", "WARNCOLOR": "#808000", "ERRORCOLOR": "#800000",
    "ACCENTCOLOR": "#FFFFFF", "ACCENTALTCOLOR": "#C0C0C0", "EMPHASISCOLOR": "#000000"
}


@app.route('/')
def index():
    return render_template('index.html', colors=default_colors)


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
