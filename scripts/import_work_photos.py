from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps
import csv
import hashlib
import io
import json
import time

photos = {
    'before': 'https://static.wixstatic.com/media/d64147_1a35035c2ac44fd899fb063850225e44~mv2.jpg',
    'after': 'https://static.wixstatic.com/media/d64147_1347fda6c62d4386ab4cdbee171e85ff~mv2.jpg',
}
validated = {}
records = []
for stage, url in photos.items():
    for attempt in range(3):
        try:
            request = Request(url, headers={'User-Agent': 'OvenGuyConceptAssetImport/1.0'})
            with urlopen(request, timeout=45) as response:
                if response.status != 200:
                    raise ValueError(f'Unexpected HTTP status: {response.status}')
                raw = response.read(12000001)
            if len(raw) > 12000000:
                raise ValueError('Image exceeds 12 MB import limit')
            with Image.open(io.BytesIO(raw)) as probe:
                probe.verify()
            with Image.open(io.BytesIO(raw)) as original:
                if original.width < 100 or original.height < 100:
                    raise ValueError('Image too small for gallery')
                image = ImageOps.exif_transpose(original).convert('RGB')
                image.thumbnail((1400, 1400))
                encoded = io.BytesIO()
                image.save(encoded, 'JPEG', quality=90, optimize=True)
                validated[stage] = encoded.getvalue()
                records.append({'stage': stage, 'source': url, 'width': image.width, 'height': image.height, 'sha256': hashlib.sha256(raw).hexdigest(), 'file': f'assets/work/oven-door-{stage}.jpg'})
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

page_path = Path('index.html')
page = page_path.read_text(encoding='utf-8')
marker = '<!-- original-work-gallery -->'
if marker not in page:
    anchor = '<section id="prices" class="prices">'
    if page.count(anchor) != 1:
        raise ValueError('Expected price-section insertion point not found; no website changes written')
    gallery = '''<!-- original-work-gallery --><section id="work"><div class="wrap"><p class="eyebrow">The work</p><h2>See the difference.</h2><p class="intro">Original oven-door photographs labelled before and after on the business's saved Prices page. Labels follow that source; no treatment duration or additional result guarantee is implied.</p><div class="split work-gallery"><figure><a href="assets/work/oven-door-before.jpg"><img src="assets/work/oven-door-before.jpg" alt="Oven door before cleaning, as labelled on the original business website" loading="lazy" decoding="async"></a><figcaption>Before cleaning</figcaption></figure><figure><a href="assets/work/oven-door-after.jpg"><img src="assets/work/oven-door-after.jpg" alt="Oven door after cleaning, as labelled on the original business website" loading="lazy" decoding="async"></a><figcaption>After cleaning</figcaption></figure></div><p class="note">Open either photograph to view the original-size imported image. These are the business's existing portfolio images, not stock photographs.</p></div></section>'''
    page = page.replace(anchor, gallery + anchor, 1)
    page = page.replace('<a href="#reviews">Reviews</a>', '<a href="#work">Our work</a><a href="#reviews">Reviews</a>', 1)
    style = '''.work-gallery figure{margin:0;border:1px solid #dcded3;border-radius:8px;overflow:hidden;background:#fffefa}.work-gallery a{display:block}.work-gallery img{display:block;width:100%;height:auto;aspect-ratio:642/436;object-fit:contain;background:#e9e9e1}.work-gallery figcaption{padding:15px 20px;font-weight:700;font-size:14px}'''
    page = page.replace('</style>', style + '</style>', 1)
    page = page.replace('The saved Prices page labels an oven-door before-and-after pair, but its companion image files were not supplied. Those photographs are not displayed here, and the illustration above is not a cleaning result.', 'Yes. The Our work section displays the original oven-door photos labelled before and after on the saved Prices page. The hero illustration remains original artwork, not a photograph of a cleaning result.')

readme_path = Path('README.md')
readme = readme_path.read_text(encoding='utf-8')
old = 'The original Contact page and saved companion resource folders were not supplied. Therefore social links, original logo and original before/after photographs are not included. Their missing assets are not replaced with fake results.'
new = 'The original Contact page and saved companion resource folders were not supplied. The before/after oven-door photographs were subsequently imported from the original Wix media identifiers embedded in the saved Prices page. Social links and the original logo are still not integrated. Portfolio labels follow the source page; independent verification of the cleaning job is not claimed.'
readme = readme.replace(old, new)
readme = readme.replace('It is self-contained, with embedded CSS, original SVG artwork and a client-side mailto helper.', 'It uses embedded CSS, original SVG artwork, local portfolio photographs in assets/work and a client-side mailto helper. Keep the assets folder with index.html when previewing or publishing.')
section = '\n\n## Imported work photographs\nThe import validates that both downloads decode as images before adding the gallery. IMAGE_IMPORT_RESULTS.json records sources, dimensions and source hashes. Original before/after labels were extracted from the saved Prices page. The existing TEST_RESULTS.json records the earlier pre-gallery browser smoke tests; these image-import checks are not a new full browser audit. This import does not enable hosting.\n'
if '## Imported work photographs' not in readme:
    readme += section

with Path('CONTENT_AUDIT.csv').open(encoding='utf-8', newline='') as stream:
    audit = list(csv.reader(stream))
for row in audit[1:]:
    if row[0] == 'Prices' and row[1] == 'Before/after oven door images':
        row[2] = 'Our work gallery'
        row[3] = 'Imported from original Wix media IDs; source before/after labels retained; downloads validated'
    if row[0] == 'Home and other pages':
        row[3] = 'Original oven-door work photos imported; original logo still absent; proposed wordmark and illustration retained'

assets = Path('assets/work')
assets.mkdir(parents=True, exist_ok=True)
for stage, content in validated.items():
    (assets / f'oven-door-{stage}.jpg').write_bytes(content)
page_path.write_text(page, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
with Path('CONTENT_AUDIT.csv').open('w', encoding='utf-8', newline='') as stream:
    csv.writer(stream).writerows(audit)
Path('IMAGE_IMPORT_RESULTS.json').write_text(json.dumps({'status': 'Both images downloaded and decoded successfully', 'images': records, 'label_basis': 'Original saved Prices page alt labels; not independent job verification', 'browser_testing': 'Not performed by this import'}, indent=2) + '\n', encoding='utf-8')
