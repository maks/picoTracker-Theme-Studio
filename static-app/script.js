// script.js – static replacement for Flask backend

// Default theme colors (copied from app.py)
const defaultColors = {
  BACKGROUND: "#000000",
  FOREGROUND: "#0088FF",
  HICOLOR1: "#00BB66",
  HICOLOR2: "#0066CC",
  CONSOLECOLOR: "#000000",
  CURSORCOLOR: "#00BB66",
  INFOCOLOR: "#0088FF",
  WARNCOLOR: "#00AA55",
  ERRORCOLOR: "#CC3333",
  ACCENTCOLOR: "#00AA55",
  ACCENTALTCOLOR: "#0066CC",
  EMPHASISCOLOR: "#00AA55"
};

// Utility: update CSS variable for a color key
function up(k, v) {
  document.getElementById('pv').style.setProperty('--' + k, v);
}

// Generate a random hex color string
function randColor() {
  return "#" + Math.floor(Math.random() * 0xffffff).toString(16).padStart(6, '0');
}

// Randomize all colors (client‑side equivalent of '/randomize')
function rand() {
  const bg = randColor();
  const brightness = [0, 2, 4].reduce((sum, i) => sum + parseInt(bg.slice(i + 1, i + 3), 16), 0);
  const fg = brightness < 380 ? "#FFFFFF" : "#000000";
  const newColors = {};
  for (const k in defaultColors) {
    newColors[k] = randColor();
  }
  newColors['BACKGROUND'] = bg;
  newColors['FOREGROUND'] = fg;
  // Apply to UI
  for (const k in newColors) {
    const inp = document.getElementById('in_' + k);
    if (inp) inp.value = newColors[k];
    up(k, newColors[k]);
  }
}

// Upload a .ptt file, parse XML and apply colors (client‑side replacement for '/import')
function upload() {
  const file = document.getElementById('fileIn').files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    const parser = new DOMParser();
    const xml = parser.parseFromString(e.target.result, "application/xml");
    const colors = {};
    xml.querySelectorAll('Color').forEach(col => {
      const name = col.getAttribute('name');
      const value = col.getAttribute('value');
      if (name && value && defaultColors.hasOwnProperty(name)) {
        colors[name] = value;
      }
    });
    // Apply imported colors
    for (const k in colors) {
      const inp = document.getElementById('in_' + k);
      if (inp) inp.value = colors[k];
      up(k, colors[k]);
    }
  };
  reader.readAsText(file);
}

// Save current palette to gallery (localStorage)
function saveG() {
  const palette = {};
  document.querySelectorAll('input[type="color"]').forEach(i => {
    palette[i.name] = i.value;
  });
  const name = document.getElementById('tn').value || 'untitled';
  const gallery = JSON.parse(localStorage.getItem('g') || '[]');
  gallery.push({ n: name, c: palette });
  localStorage.setItem('g', JSON.stringify(gallery));
  renderG();
}

// Render gallery thumbnails
function renderG() {
  const container = document.getElementById('gal');
  container.innerHTML = '';
  const gallery = JSON.parse(localStorage.getItem('g') || '[]');
  gallery.forEach((t, i) => {
    const div = document.createElement('div');
    div.className = 'g-item';
    div.style.background = t.c.BACKGROUND;
    div.style.color = t.c.FOREGROUND;
    div.textContent = t.n;
    div.onclick = () => {
      for (const k in t.c) {
        const inp = document.getElementById('in_' + k);
        if (inp) inp.value = t.c[k];
        up(k, t.c[k]);
      }
      document.getElementById('tn').value = t.n;
    };
    container.appendChild(div);
  });
}

// Trigger download of .ptt XML (client‑side replacement for '/download')
function downloadTheme(event) {
  event.preventDefault(); // stop form submission
  const name = (document.getElementById('tn').value || 'custom').trim() || 'custom';
  let xml = `<?xml version="1.0" encoding="UTF-8"?>\n<THEME>\n  <Font value="#1" />\n`;
  for (const k in defaultColors) {
    const value = document.getElementById('in_' + k).value || defaultColors[k];
    xml += `  <Color name="${k}" value="${value.toUpperCase()}" />\n`;
  }
  xml += '</THEME>';
  const blob = new Blob([xml], { type: 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${name}.ptt`;
  a.click();
  URL.revokeObjectURL(url);
}

// Dynamically build color input rows (replaces Jinja loop)
function buildColorInputs() {
  const form = document.getElementById('f');
  // Remove any previously injected rows (keep the first name row)
  const existingRows = Array.from(form.querySelectorAll('.row'));
  existingRows.slice(1).forEach(r => r.remove());
  for (const k in defaultColors) {
    const div = document.createElement('div');
    div.className = 'row';
    const label = document.createElement('span');
    label.textContent = `${k}:`;
    const input = document.createElement('input');
    input.type = 'color';
    input.name = k;
    input.id = 'in_' + k;
    input.value = defaultColors[k];
    input.oninput = () => up(k, input.value);
    div.appendChild(label);
    div.appendChild(input);
    // Insert before the randomize button (which has id="randBtn")
    const randBtn = document.getElementById('randBtn');
    form.insertBefore(div, randBtn);
  }
}

// Init on page load
window.onload = () => {
  // Apply default colors to preview
  for (const k in defaultColors) {
    up(k, defaultColors[k]);
  }
  // Populate preview monitor with tracker rows (static replica of original Jinja output)
  const TRACKER_ROWS = ["00","01","02","03","04","05","06","07","08","09","0A","0B","0C","0D","0E","0F"];
  let previewHTML = `<span class="blue">song sad-fog</span>                         <span class="green">[c++f]</span>`;
  TRACKER_ROWS.forEach((row, idx) => {
    if (idx === 0) {
      previewHTML += `\n<span class="blue">${row}</span>  <span class="cursor blue">00</span>`;
    } else {
      previewHTML += `\n<span class="blue">${row}</span>  <span class="blue">--</span>`;
    }
    // add six placeholder '--' spans
    for (let i = 0; i < 6; i++) {
      previewHTML += `  <span class="blue">--</span>`;
    }
  });
  previewHTML += `\n<span class="blue"></span>`;
  
  previewHTML += `\n<span class="blue">D</span>`;
  previewHTML += `\n<span class="blue">P G</span>`;
  previewHTML += `\n<span class="blue">SCPI</span>`;
  previewHTML += `\n<span class="blue">  TT</span>`;
  document.getElementById('pv').innerHTML = previewHTML;
  buildColorInputs();
  renderG();
};