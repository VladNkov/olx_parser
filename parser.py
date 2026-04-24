from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

START_URL = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/'
PAGES = 2


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
            print(f'open page {page_number}: {url}')

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
                    page_links.append(href)
            page_links = list(dict.fromkeys(page_links))

            print(f'links on page {page_number}: {len(page_links)}')

            all_links.extend(page_links)

        unique_links = list(dict.fromkeys(all_links))

        print(f'all links:')

        for link in unique_links:
            print(link)

        print(f'Total links: {len(unique_links)}')

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())