from playwright.sync_api import sync_playwright
import os
import sys

# Path to the deployed dashboard
path = '/home/kimm/projects/amazon/deploy-whisper-dashboard/index.html'
if not os.path.exists(path):
    print('Path does not exist:', path)
    sys.exit(1)

print('Testing path:', path)
url = 'file://' + path

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        errors = []
        page.on('console', lambda msg: print('BROWSER CONSOLE:', msg.text))
        page.on('pageerror', lambda err: print('BROWSER ERROR:', err.message))
        
        try:
            page.goto(url, wait_until='networkidle', timeout=5000)
        except Exception as e:
            print('Goto err:', e)
            
        page.wait_for_timeout(2000)
        print('Playwright test finished.')
        browser.close()

if __name__ == '__main__':
    run()
