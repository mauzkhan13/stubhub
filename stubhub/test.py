from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

def run(playwright):
    browser = playwright.chromium.launch(headless=True)  # Use headless mode for server
    page = browser.new_page()

    url = "https://www.stubhub.ie/euro-2024-tickets/grouping/1507012/?wcpb=4"
    page.goto(url)
    print("The Browser is opened")
    page.wait_for_load_state()
    time.sleep(1)

    # Check and handle cookie consent modal
    try:
        cookie_accept_button = page.locator('button:has-text("Accept")')
        if cookie_accept_button.is_visible():
            cookie_accept_button.click()
            time.sleep(1)
    except Exception as e:
        print(f"An exception occurred while handling cookie consent: {e}")

    while True:
        try:
            next_page = page.locator('(//*[contains(text(),"See more events")])[2]')
            if next_page.is_visible():
                next_page.click()
                print("The next page is clicking")
                time.sleep(1)
            else:
                break
        except Exception as e:
            print(f"An exception occurred: {e}")
            break

    events_links = []
    html_content = page.content()
    soup = BeautifulSoup(html_content, 'lxml')
    divs = soup.find_all('a', {'class': 'cbt-redirection__link EventItem__TitleLink'})
    base_url = 'https://www.stubhub.ie/'
    for link in divs:
        url = link.get('href')
        complete_url = base_url + url
        events_links.append(complete_url)
    print(len(events_links))
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
