from pathlib import Path
from PIL import Image
from collections import Counter
import colorsys
import hashlib
import json

paths = [Path('assets/work/oven-guy-wordmark.png'), Path('assets/work/oven-guy-icon.png')]
images = [Image.open(p).convert('RGBA') for p in paths]
def rgbhex(c):
    return '#' + ''.join(f'{v:02x}' for v in c)
def lum(c):
    v = [x / 255 for x in c]
    linear = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in v]
    return sum(a*b for a,b in zip(linear, [.2126,.7152,.0722]))
def contrast(a,b):
    x,y = sorted([lum(a),lum(b)])
    return (y+.05)/(x+.05)
def mix(a,b,t):
    return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))

edge = Counter()
for image in images:
    for x in range(image.width):
        for y in (0, image.height-1):
            p = image.getpixel((x,y))
            if p[3] > 200:
                edge[tuple(min(255, round(v/8)*8) for v in p[:3])] += 1
    for y in range(image.height):
        for x in (0, image.width-1):
            p = image.getpixel((x,y))
            if p[3] > 200:
                edge[tuple(min(255, round(v/8)*8) for v in p[:3])] += 1
background = edge.most_common(1)[0][0] if edge else (35,35,35)
dark = lum(background) < .3
ink = (245,245,245) if dark else (25,25,25)
if contrast(ink,background) < 4.5:
    ink = max([(255,255,255),(0,0,0)],key=lambda c:contrast(c,background))
accent = None
for image in images:
    sample = image.copy()
    sample.thumbnail((320,160))
    candidates = Counter()
    for r,g,b,a in sample.getdata():
        _,sat,value = colorsys.rgb_to_hsv(r/255,g/255,b/255)
        if a > 200 and sat > .4 and .22 < value < .99:
            candidates[tuple(min(255,round(v/12)*12) for v in (r,g,b))] += 1
    if candidates:
        accent = candidates.most_common(1)[0][0]
        break
accent_origin = 'dominant saturated wordmark colour; icon used only if wordmark has no saturated pixels'
if accent is None:
    accent = ink
    accent_origin = 'monochrome logo: neutral accent, no invented colour'
button_ink = max([(255,255,255),(0,0,0)],key=lambda c:contrast(c,accent))
text_accent = accent
for step in range(21):
    candidate = mix(accent,ink,step/20)
    if contrast(candidate,background) >= 4.5:
        text_accent = candidate
        break
panel = mix(background,ink,.065)
muted = mix(background,ink,.76)
line = mix(background,ink,.25)
header = background
alternate = mix(background,(0,0,0) if dark else (255,255,255),.15)
tokens = {'background':rgbhex(background),'panel':rgbhex(panel),'ink':rgbhex(ink),'accent':rgbhex(accent),'buttonInk':rgbhex(button_ink),'textAccent':rgbhex(text_accent),'muted':rgbhex(muted),'line':rgbhex(line),'header':rgbhex(header),'alternate':rgbhex(alternate)}
css = ':root{color-scheme:' + ('dark' if dark else 'light') + ';' + ''.join('--logo-'+k+':'+v+';' for k,v in tokens.items()) + '}\n'
css += '''body{background:var(--logo-background);color:var(--logo-ink);font-family:Arial,Helvetica,sans-serif;-webkit-font-smoothing:antialiased}
header{background:var(--logo-header);border-color:var(--logo-line);box-shadow:0 5px 24px #00000012}
.notice{background:var(--logo-alternate);color:var(--logo-muted);font-size:10px;letter-spacing:1px}
.nav{padding:18px 0;gap:30px}.brand span,h1 em{color:var(--logo-textAccent)}
header .brand.brand-logo{gap:14px;flex-shrink:0;align-items:center}
header .brand-logo .brand-icon{width:64px;height:76px;object-fit:contain}
header .brand-logo .brand-wordmark{width:230px;height:76px;object-fit:contain}
nav{gap:24px}nav a{color:var(--logo-ink);font-weight:600;font-size:12px;letter-spacing:.25px}nav a:hover{color:var(--logo-textAccent)}
.hero{grid-template-columns:.95fr 1.05fr;gap:48px;padding:76px 0 84px;align-items:center}
h1{font-size:clamp(44px,5.6vw,76px);line-height:1.07;letter-spacing:-2.7px;font-weight:800}
h2{font-weight:750;letter-spacing:-1.3px}h3{font-weight:700;line-height:1.35}
.lead{font-size:17px;line-height:1.8}.lead,.intro,.small,.note,.card p,details p{color:var(--logo-muted)}
.eyebrow,.num,.dark .num{color:var(--logo-textAccent)}.eyebrow{letter-spacing:2.2px}
.button{background:var(--logo-accent);border-color:var(--logo-accent);color:var(--logo-buttonInk);border-radius:7px;padding:14px 24px;font-weight:700}
.button:hover{filter:brightness(.92)}.button.secondary{background:transparent;border-color:var(--logo-line);color:var(--logo-ink)}
.button.secondary:hover{background:var(--logo-panel);filter:none}.actions{gap:13px}
.pill{background:var(--logo-panel);color:var(--logo-ink);border:1px solid var(--logo-line);letter-spacing:.4px}
.strip{background:var(--logo-alternate);color:var(--logo-muted);border-color:var(--logo-line);padding:23px 0}
.card,.price-list,.form,.work-gallery figure{background:var(--logo-panel);color:var(--logo-ink);border-color:var(--logo-line);border-radius:10px}
.card{padding:30px}.card a{color:var(--logo-textAccent);font-weight:700}.prices,.dark,.reviews{background:var(--logo-alternate);color:var(--logo-ink)}
.dark p{color:var(--logo-muted)}.row,details,.step{border-color:var(--logo-line)}.row{padding:19px 0}.row strong{color:var(--logo-ink)}
input,textarea{background:var(--logo-background);color:var(--logo-ink);border-color:var(--logo-line);border-radius:6px}input::placeholder,textarea::placeholder{color:var(--logo-muted)}
.links small,footer{color:var(--logo-muted)}.links a:hover{color:var(--logo-textAccent)}
footer{background:var(--logo-header);border-color:var(--logo-line)}
.hero .hero-pair{gap:16px;align-items:start}.hero .hero-pair figure{background:var(--logo-panel);border:1px solid var(--logo-line);border-radius:12px;box-shadow:0 12px 32px #00000018}
.hero .hero-pair figure:last-child{border-color:var(--logo-accent)}.hero .hero-pair img,.work-gallery img{background:var(--logo-background)}
.hero .hero-pair figcaption,.work-gallery figcaption{background:var(--logo-panel);color:var(--logo-ink);border-color:var(--logo-line);letter-spacing:.4px}
.hero .hero-pair figcaption{padding:15px;font-size:12px;text-transform:uppercase}
blockquote{font-size:15px;line-height:1.85}cite{color:var(--logo-textAccent)}
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible{outline:3px solid var(--logo-textAccent);outline-offset:4px}
.skip{background:var(--logo-ink);color:var(--logo-background)}
@media(max-width:900px){.nav{flex-wrap:wrap;gap:16px}nav{flex-wrap:wrap}.hero{gap:30px}}
@media(max-width:760px){header .brand-logo .brand-icon{width:44px;height:54px}header .brand-logo .brand-wordmark{width:min(190px,58vw);height:54px}.nav{padding:14px 0}.hero{grid-template-columns:1fr;padding:42px 0 52px;gap:32px}h1{letter-spacing:-1.8px}.hero .hero-pair{max-width:500px;margin:auto;width:100%;grid-template-columns:1fr}nav{gap:18px}.card{padding:24px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''
Path('theme.css').write_text(css,encoding='utf-8')
report = {'tokens':tokens,'accentBasis':accent_origin,'backgroundBasis':'most common opaque perimeter colour from uploaded branding; charcoal fallback for fully transparent edges','assets':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'contrast':{'body':contrast(ink,background),'button':contrast(button_ink,accent),'accentOnBackground':contrast(text_accent,background)},'artwork':'Original images are unchanged; no filters, cropping or recolouring'}
Path('BRAND_THEME_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
