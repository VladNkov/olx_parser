from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import re
from write_to_gsheet import write_ads_in_google_sheet


START_URL = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/'
PAGES = 1
LIMIT_ADS = 5


async def collecting_links(page):
    all_links = []

    for page_number in range(1, PAGES + 1):
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

    return unique_links


async def parse_ad(browser, link):
    ad_page = await browser.new_page()

    await ad_page.goto(link, timeout=60000)
    await ad_page.wait_for_timeout(3000)


    price = ''
    data_parametrs ={}

    match = re.search(r'-(ID[^./?]+)\.html', link)
    ad_id = match.group(1) if match else ''

    price_selectors = ['[data-testid="ad-price-container"]', '[data-testid="ad-price"]', 'h3',]

    for selector in price_selectors:
        if await ad_page.locator(selector).count() > 0:
            price = await ad_page.locator(selector).first.inner_text()
            break

    params = ad_page.locator('p[data-nx-name="P3"]')
    count = await params.count()

    for i in range(count):
        text = await params.nth(i).inner_text()

        if ":" in text:
            key, value = text.split(':', 1)
            data_parametrs[key.strip()] = value.strip()

    ad_data = {'ad_id': ad_id,
               'price': price,
               'object_type': data_parametrs.get("Вид об'єкта", ''),
               'bilding_name': data_parametrs.get("Назва ЖК", ''),
               'floor': data_parametrs.get("Поверх", ''),
               'start_year': data_parametrs.get("Рік введення в експлуатацію", ''),
               'total_floor': data_parametrs.get("Поверховість", ''),
               'area': data_parametrs.get('Загальна площа', ''),
               'kitchen_area': data_parametrs.get("Площа кухні", ''),
               'walls_type': data_parametrs.get("Тип стін", ''),
               'class': data_parametrs.get("Клас житла", ''),
               'rooms': data_parametrs.get("Кількість кімнат", ''),
               'plan': data_parametrs.get("Планування", ''),
               'vc': data_parametrs.get("Cанвузол", ''),
               'heating': data_parametrs.get("Опалення", ''),
               'repair': data_parametrs.get("Ремонт", ''),
               'furniture': data_parametrs.get("Меблювання", ''),
               'tehniks': data_parametrs.get("Побутова техніка", ''),
               'multimedia': data_parametrs.get("Мультимедіа", ''),
               'comfort': data_parametrs.get("Комфорт", ''),
               'сommunications': data_parametrs.get("Комунікації", ''),
               'infrastructure': data_parametrs.get("Інфраструктура", ''),
               'landscape': data_parametrs.get("Ландшафт", ''),
               'incl': data_parametrs.get("Інклюзивність", ''),
               'url': link,}

    await ad_page.close()

    return ad_data

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        unique_links = await collecting_links(page)

        print(f'All links:')

        for num, link in enumerate(unique_links, start=1):
            print(f'{num}. {link}')

        print(f'Total links: {len(unique_links)}')

        data_ads = []

        for link in unique_links[:LIMIT_ADS]:
            ad = await parse_ad(browser, link)
            data_ads.append(ad)

        for ad in data_ads:
            print(ad)

        write_ads_in_google_sheet(data_ads)

        await page.close()
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())