from pathlib import Path
import re

path = Path('index.html')
page = path.read_text(encoding='utf-8')
link = '<link rel="stylesheet" href="theme.css">'
if link not in page:
    if page.count('</head>') != 1:
        raise ValueError('Expected one head closing tag')
    page = page.replace('</head>', link + '</head>', 1)

colors = {
    '#c5cdb9': '#111111',
    '#28342c': '#181818',
    '#d1d7cd': '#c9c9c9',
    '#59665c': '#555555',
    '#273b2c': '#450000',
    '#e1ebd7': '#ffffff',
    '#12231a': '#111111',
    '#334e3e': '#353535',
    '#8fa795': '#bdbdbd',
    '#e5e9df': '#eeeeee',
    '#fffefa': '#ffffff',
}
def recolor(match):
    svg = match.group(0)
    for old, new in colors.items():
        svg = svg.replace(old, new)
    return svg
page = re.sub(r'<svg\b[^>]*>.*?</svg>', recolor, page, flags=re.S)
path.write_text(page, encoding='utf-8')
