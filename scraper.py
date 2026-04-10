import re
import json
import time
import random
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

STORE_URL = "https://www.amazon.com/stores/WhisperEarCare/page/9D65D8CD-B63E-4951-B285-B66A1188EEC6"
OUTPUT_CSV = "amazon_whisper_store_products.csv"

def clean_text(value):
    if not value:
        return None
    return re.sub(r"\s+", " ", value).strip()

def clean_link(url):
    if not url:
        return None
    m = re.search(r"/dp/([A-Z0-9]{10})", url)
    if m:
        return f"https://www.amazon.com/dp/{m.group(1)}"
    m = re.search(r"/gp/product/([A-Z0-9]{10})", url)
    if m:
        return f"https://www.amazon.com/dp/{m.group(1)}"
    return url.split("?")[0]

def extract_asin_from_url(url):
    if not url:
        return None
    m = re.search(r"/dp/([A-Z0-9]{10})", url)
    if m:
        return m.group(1)
    m = re.search(r"/gp/product/([A-Z0-9]{10})", url)
    if m:
        return m.group(1)
    return None

def safe_inner_text(page, selector):
    try:
        el = page.locator(selector).first
        if el.count() > 0:
            return clean_text(el.inner_text(timeout=3000))
    except:
        return None
    return None

def safe_attr(page, selector, attr):
    try:
        el = page.locator(selector).first
        if el.count() > 0:
            value = el.get_attribute(attr, timeout=3000)
            return clean_text(value)
    except:
        return None
    return None

def extract_price(page):
    selectors = [
        "span.a-price span.a-offscreen",
        "#corePriceDisplay_desktop_feature_div span.a-offscreen",
        "#corePrice_feature_div span.a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#price_inside_buybox"
    ]
    for selector in selectors:
        value = safe_inner_text(page, selector)
        if value:
            return value
    return None

def extract_rating(page):
    candidates = [
        "#acrPopover",
        "span[data-hook='rating-out-of-text']",
        "i[data-hook='average-star-rating'] span",
    ]
    for selector in candidates:
        text = safe_inner_text(page, selector)
        if text:
            m = re.search(r"([0-9.]+)", text)
            if m:
                return m.group(1)
    return None

def extract_review_count(page):
    text = safe_inner_text(page, "#acrCustomerReviewText")
    if text:
        m = re.search(r"([\d,]+)", text)
        if m:
            return m.group(1).replace(",", "")
    return None

def extract_main_image(page):
    for selector, attr in [
        ("#landingImage", "src"),
        ("#landingImage", "data-old-hires"),
        ("#imgTagWrapperId img", "src"),
        ("#imgTagWrapperId img", "data-old-hires"),
    ]:
        value = safe_attr(page, selector, attr)
        if value:
            return value
    return None

def extract_asin(page, url):
    asin = safe_attr(page, "input#ASIN", "value")
    if asin:
        return asin
    asin = extract_asin_from_url(url)
    if asin:
        return asin
    body_text = page.locator("body").inner_text(timeout=3000)
    m = re.search(r"\b([A-Z0-9]{10})\b", body_text)
    return m.group(1) if m else None

def extract_sales_rank(page):
    try:
        bullets = page.locator("#detailBullets_feature_div li").all_inner_texts()
        for txt in bullets:
            if "Best Sellers Rank" in txt:
                return clean_text(txt)
    except:
        pass

    try:
        table_text = page.locator("#productDetails_detailBullets_sections1").inner_text(timeout=3000)
        m = re.search(r"Best Sellers Rank\s*(.*)", table_text)
        if m:
            return clean_text(m.group(0))
    except:
        pass

    try:
        body = page.locator("body").inner_text(timeout=3000)
        m = re.search(r"Best Sellers Rank\s*[:#]?\s*(.*?)(?:Customer Reviews|Date First Available|Manufacturer|ASIN)", body, re.S)
        if m:
            return clean_text(m.group(1))
    except:
        pass

    return None

def wait_for_product_page(page):
    possible = ["#productTitle", "#landingImage", "input#ASIN"]
    for selector in possible:
        try:
            page.wait_for_selector(selector, timeout=8000)
            return True
        except PlaywrightTimeoutError:
            continue
    return False

def scrape_store_product_links(page):
    page.goto(STORE_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)

    for _ in range(8):
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(1500)

    hrefs = page.eval_on_selector_all(
        "a[href]",
        "els => els.map(a => a.href)"
    )

    product_links = set()
    for href in hrefs:
        if not href:
            continue
        if "/dp/" in href or "/gp/product/" in href:
            product_links.add(clean_link(href))

    return sorted(product_links)

def scrape_product(page, url):
    result = {
        "product_name": None,
        "main_photo": None,
        "asin": None,
        "star_rating": None,
        "review_count": None,
        "sales_rank": None,
        "price": None,
        "direct_link": clean_link(url),
        "source_url": url,
        "error": None,
    }

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(random.randint(2000, 4000))

        if not wait_for_product_page(page):
            result["error"] = "Product selectors not found"
            return result

        result["product_name"] = safe_inner_text(page, "#productTitle")
        result["main_photo"] = extract_main_image(page)
        result["asin"] = extract_asin(page, url)
        result["star_rating"] = extract_rating(page)
        result["review_count"] = extract_review_count(page)
        result["sales_rank"] = extract_sales_rank(page)
        result["price"] = extract_price(page)

        if result["asin"]:
            result["direct_link"] = f"https://www.amazon.com/dp/{result['asin']}"

    except Exception as e:
        result["error"] = str(e)

    return result

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)
        context = browser.new_context(
            viewport={"width": 1440, "height": 2200},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = context.new_page()

        print("Collecting product links from store page...")
        product_links = scrape_store_product_links(page)
        print(f"Found {len(product_links)} product links")

        rows = []
        for i, link in enumerate(product_links, start=1):
            print(f"[{i}/{len(product_links)}] Scraping {link}")
            row = scrape_product(page, link)
            rows.append(row)
            time.sleep(random.uniform(2, 5))

        browser.close()

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(df.to_string())
    print(f"Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()