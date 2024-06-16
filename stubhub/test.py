from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)  # Use headless mode for server
    page = browser.new_page()

    url = "https://www.stubhub.ie/euro-2024-tickets/grouping/1507012/?wcpb=4"
    page.goto(url)
    f("The Browser is opened")
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
                f("The next page is clicking")
                time.sleep(1)
            else:
                break
        except Exception as e:
            print(f"An exception occurred: {e}")
            break
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
