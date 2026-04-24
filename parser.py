from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

START_URL = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/'


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(START_URL, timeout=60000)
        await page.wait_for_timeout(3000)

        elements = page.locator('a')
        count = await elements.count()

        links = []

        for i in range(count):
            href = await elements.nth(i).get_attribute('href')

            if href and '/d/uk/obyavlenie/' in href:
                if href.startswith('/'):
                    href = 'https://www.olx.ua' + href
                links.append(href)
        unique_links = list(dict.fromkeys(links))

        for link in unique_links:
            print(link)

        print(f'Total links {len(unique_links)}')

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())