from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

START_URL = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/'
PAGES = 1
LIMIT_ADS = 5


async def parse_ad(browser, link):
    ad_page = await browser.new_page()

    await ad_page.goto(link, timeout=60000)
    await ad_page.wait_for_timeout(3000)

    price = ''
    object_type = ''



    if await ad_page.locator('[data-testid="ad-price-container"]').count() > 0:
        price = await ad_page.locator('[data-testid="ad-price-container"]').inner_text()

    params = ad_page.locator('p[data-nx-name="P3"]')
    count = await params.count()

    for i in range(count):
        text = await params.nth(i).inner_text()

        if "Вид об'єкта:" in text:
            object_type = text.replace("Вид об'єкта:", "").strip()
            break


    ad_data = {'url': link, 'price': price, 'object_type': object_type}

    await ad_page.close()

    return ad_data

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        all_links = []

        for page_number in range(1, PAGES+1):
            if page_number == 1:
                url = START_URL
            else:
                url = f'{START_URL}?page={page_number}'
            print(f'Opening page {page_number}: {url}')

            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)

            elements = page.locator('a')
            count = await elements.count()

            page_links = []

            for i in range(count):
                href = await elements.nth(i).get_attribute('href')

                if href and '/obyavlenie/' in href:
                    if href.startswith('/'):
                        href = 'https://www.olx.ua' + href
                    href = href.split('?')[0]
                    page_links.append(href)
            page_links = list(dict.fromkeys(page_links))

            print(f'Count links on page {page_number}: {len(page_links)}')

            all_links.extend(page_links)

        unique_links = list(dict.fromkeys(all_links))

        print(f'All links:')

        for num, link in enumerate(unique_links, start=1):
            print(f'{num}. {link}')

        print(f'Total links: {len(unique_links)}')

        data_ads = []

        for link in unique_links[:LIMIT_ADS]:
            data_ad = await parse_ad(browser, link)
            data_ads.append(data_ad)

        for ad in data_ads:
            print(ad)

        await page.close()
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())