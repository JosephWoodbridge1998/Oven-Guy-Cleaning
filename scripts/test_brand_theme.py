from pathlib import Path
from playwright.sync_api import sync_playwright
import json

results = []
Path('/tmp/brand-theme-checks').mkdir(exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for width, height in [(320, 700), (390, 844), (1440, 1000)]:
        page = browser.new_page(viewport={'width': width, 'height': height})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(Path('index.html').resolve().as_uri(), wait_until='load')
        page.locator('footer').scroll_into_view_if_needed()
        page.wait_for_function('Array.from(document.images).every(i => i.complete)')
        result = page.evaluate('''() => ({
            noOverflow: document.documentElement.scrollWidth <= innerWidth,
            background: getComputedStyle(document.body).backgroundColor,
            imagesLoaded: Array.from(document.images).every(i => i.naturalWidth > 0),
            anchorsValid: Array.from(document.querySelectorAll('a[href^="#"]')).every(a => document.querySelector(a.getAttribute('href'))),
            testimonials: document.querySelectorAll('blockquote').length,
            requiredFields: document.querySelectorAll('[required]').length,
            gallery: !!document.querySelector('#work'),
            themeLoaded: !!document.querySelector('link[href="theme.css"]').sheet
        })''')
        page.locator('.review-archive summary').click()
        result['reviewsExpand'] = page.locator('.review-archive').get_attribute('open') is not None
        page.locator('.review-archive summary').click()
        result['pageErrors'] = errors
        result['viewport'] = f'{width}x{height}'
        assert result['noOverflow'] and result['imagesLoaded'] and result['anchorsValid'] and result['gallery'] and result['themeLoaded'] and result['reviewsExpand'], result
        assert result['background'] == 'rgb(35, 35, 35)' and result['testimonials'] == 17 and result['requiredFields'] == 5 and not errors, result
        page.evaluate('window.scrollTo(0,0)')
        page.screenshot(path=f'/tmp/brand-theme-checks/preview-{width}.png', full_page=True)
        results.append(result)
        page.close()
    browser.close()
Path('THEME_TEST_RESULTS.json').write_text(json.dumps({'browser': 'Chromium', 'checks': results, 'scope': 'Local browser smoke tests; not cross-browser or complete accessibility certification. No emails sent and no live deployment verified.'}, indent=2) + '\n', encoding='utf-8')
