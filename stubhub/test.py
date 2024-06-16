from playwright.sync_api import sync_playwright
import time
import json
from bs4 import BeautifulSoup
import pandas as pd
from lxml import html
from time import sleep
from selenium import webdriver
import threading
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from time import sleep
from bs4 import Tag
from lxml import html
import re
import time
import json
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    url = "https://www.stubhub.ie/euro-2024-tickets/grouping/1507012/?wcpb=4"
    page.goto(url)
    print("The Browser is opened")
    page.wait_for_load_state()
    return browser, page 

def event_urls(page):
    while True:
        sleep(1)
        try:
            cookie_accept_button = page.locator('button:has-text("Accept")')
            if cookie_accept_button.is_visible():
                print("Accepting cookies")
                cookie_accept_button.click()
        except Exception as e:
            print(f"An exception occurred while handling cookie consent: {e}")
        try:
            next_page = page.locator('(//*[contains(text(),"See more events")])[2]')
            if next_page.is_visible():
                next_page.click()
                print("The next page is clicking")
                time.sleep(0.5)
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
    return events_links

def scrolling_page(driver):
    max_retries = 3
    while True:
        try:
            retries = 0
            while retries < max_retries:
                try:
                    scroll_page = driver.find_element(By.XPATH, '//div[@class="RoyalInfiniteScroll__Loader"]/div')
                    scroll_page.click()
                    # print("Scroll Page is clicking")
                    break
                except ElementClickInterceptedException:
                    retries += 1
                    sleep(0.1)
            else:
                pass
        except StaleElementReferenceException:
            pass
        except NoSuchElementException:
            break

def clean_text(text):
    return text.replace('\\u20ac', '').replace('\\u00a', ' ').replace('\\', '').replace('\xa0','')

def ticket_info(driver):
    category = []
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    card_elements = soup.select('ul.RoyalTicketList__container > li')

    for card_element in card_elements:
        cat = card_element.select_one('div.SectionRowSeat__sectionTitle.RoyalTicketListPanel__SectionName')
        category_text = clean_text(cat.text.strip()) if cat else 'N/A'
        category.append(category_text)
    return category

def json_data(category):
    print(len(category))
    df = pd.DataFrame(zip(category), columns=['Category'])
    new_data = json.loads(df.to_json(orient='records'))
    json_data_cleaned = json.dumps(new_data).replace('\\u20ac', '')
    print(json_data_cleaned)

if __name__ == '__main__':
    with sync_playwright() as playwright:
        browser, page = run(playwright)
        urls = event_urls(page)
        browser.close()

        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_argument('--headless')
        options.add_argument('--window-size=1920,1080')
        options.binary_location = '/usr/bin/google-chrome'
        driver = webdriver.Chrome(options=options)
        print("Selenium Browser Opened")
        
        for index, url in enumerate(urls):
            print(f"Processing the URL No: {index}")
            driver.get(url)
            print(f"Processing URL: {url}")
            scrolling_page(driver)
            category = ticket_info(driver)
            json_data(category)
        driver.quit()
