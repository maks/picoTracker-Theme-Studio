import random
# import xml.etree.ElementTree as ET
import defusedxml.ElementTree as ET
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
    """Render the main theme editor interface for the picoTracker Theme Studio.
    Provides initial tracker data and default color values to populate the page.

    Returns:
        The rendered index.html template with tracker layout metadata and color
        configuration injected into the template context.
    """
    return render_template(
        'index.html',
        colors=default_colors,
        tracker_rows=TRACKER_ROWS,
        tracker_cols=TRACKER_COLS,
    )


@app.route('/import', methods=['POST'])
def import_theme():
    """Import a theme definition from an uploaded XML file and extract theme colors.
    Returns a JSON mapping of recognized color names to their imported values.

    Args:
        file: The uploaded XML file containing theme color definitions, provided
            as part of the multipart form data in the current request.

    Returns:
        A JSON response with imported color values and HTTP 200 status if the file
        is valid, or a plain text error message with an appropriate HTTP status code
        if the upload is missing or invalid.
    """
    if 'file' not in request.files:
        return "No file", 400

    file = request.files['file']

    try:
        tree = ET.parse(file)
        root = tree.getroot()
        imported_colors = {}
        for color in root.findall('Color'):
            name = color.get('name')
            value = color.get('value')
            if name in default_colors:
                imported_colors[name] = value
        return jsonify(imported_colors)
    except ImportError:
        return "Invalid file", 500


@app.route('/randomize')
def randomize():
    """Generate a randomized set of theme colors for the picoTracker interface.
    Returns a JSON payload of new color values with readable foreground contrast.

    Returns:
        A JSON response mapping each theme color name to a randomly generated
        hex value, with BACKGROUND randomized and FOREGROUND/EMPHASISCOLOR
        adjusted to maintain sufficient contrast.
    """
    def r_c():
        return "#%06x" % random.randint(0, 0xFFFFFF)
    bg = r_c()
    fg = "#FFFFFF" if sum(int(bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) < 380 else "#000000"
    return jsonify({k: r_c() for k in default_colors.keys()} | {"BACKGROUND": bg, "FOREGROUND": fg, "EMPHASISCOLOR": fg})


@app.route('/download', methods=['POST'])
def download():
    """Create a downloadable XML theme file from submitted color values.
    Builds a theme definition using form data and returns it as a file attachment.

    Args:
        theme_name: Optional name used to construct the downloaded theme filename,
            provided via the form data along with individual color values.

    Returns:
        A Flask Response object containing the generated XML theme as an
        'application/octet-stream' attachment with a .ptt filename.
    """
    name = request.form.get('theme_name', 'custom').strip() or "custom"
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<THEME>\n  <Font value="#1" />\n'
    for k in default_colors.keys():
        xml += f'  <Color name="{k}" value="{request.form.get(k, default_colors[k]).upper()}" />\n'
    xml += '</THEME>'
    return Response(xml, mimetype='application/octet-stream', headers={"Content-disposition": f"attachment; filename={name}.ptt"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
