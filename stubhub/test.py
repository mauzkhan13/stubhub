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
import requests

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    url = "https://www.stubhub.ie/euro-2024-tickets/grouping/1507012/?wcpb=4"
    page.goto(url)
    print("The Main URL is opened in the Browser")
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
    for link in divs[:7]:
        url = link.get('href')
        complete_url = base_url + url
        events_links.append(complete_url)
    print(f"Total Number of Event Links: {len(events_links)}")
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
                    print("Scroll Page is clicking")
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
    return re.sub(r'\s+', ' ', text).strip()

def ticket_info(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    card_elements = soup.select('ul.RoyalTicketList__container > li')
    category = []
    ticket_prices = []
    sets_information = []
    tickets_number = []
    event_name = []
    scrape_time = []

    scrape_times = datetime.now().strftime('%H:%M:%S, %d-%m-%Y')
    scrape_time.append(scrape_times)
    event_name.append(driver.find_element(By.XPATH, '//h1').text.strip())
    
    for card_element in card_elements:
        element = html.fromstring(str(card_element))
        cat = card_element.select_one('div.SectionRowSeat__sectionTitle.RoyalTicketListPanel__SectionName')
        category_text = clean_text(cat.text.strip()) if cat else 'N/A'
        category.append(category_text)

        sets_info = card_element.select('span.SectionRowSeat__row')
        if sets_info:
            cleaned_sets_info = ' '.join([clean_text(set_no.text) for set_no in sets_info])
            sets_information.append(cleaned_sets_info)
        else:
            sets_information.append('N/A')

        price = card_element.select_one('div.PriceDisplay__price')
        price_text = clean_text(price.text.strip()) if price else 'N/A'
        ticket_prices.append(price_text)

        tickets = element.xpath('//div[@class="RoyalTicketListPanel__SecondaryInfo"]/text()[normalize-space()]')
        if tickets:
            cleaned_tickets = ' '.join([clean_text(ticket.strip()) if isinstance(ticket, str) else clean_text(ticket.strip()) for ticket in tickets])
            tickets_number.append(cleaned_tickets)
        else:
            tickets_number.append('N/A')

    return event_name,scrape_time, category, ticket_prices, sets_information, tickets_number

def json_data(event_name,scrape_time, category, ticket_prices, sets_information, tickets_number):
    
    print("Total Numbers of category", len(category))
    event_df = pd.DataFrame(zip(event_name,scrape_time), columns=['Event Name', 'Scraped Time'])
    event_data = json.loads(event_df.to_json(orient='records'))

    df = pd.DataFrame(zip(category, ticket_prices, sets_information, tickets_number), columns=['Category', 'Ticket Prices', 'Set information', 'Ticket Number'])
    new_data = json.loads(df.to_json(orient='records'))
    
    json_data_cleaned_str = json.dumps(new_data).replace('\\u20ac', '').replace('\\u00a', ' ').replace('\\', '').replace('\xa0','')

    json_data_cleaned = json.loads(json_data_cleaned_str)
    
    combined_data = event_data + json_data_cleaned
    
    final_json_data = json.dumps(combined_data)
    
    final_json_data_cleaned = final_json_data.replace('\n', '')
    print(final_json_data_cleaned)

    # save_data_url = 'https://pinhouse.seatpin.com/api/bot-webhook'
    # headers = {'Content-Type': 'application/json'}
    # response = requests.post(save_data_url, data=final_json_data_cleaned, headers=headers)
    # if response.status_code == 200:
    #     print(f'Data successfully sent to the server.{response.status_code}')
    # else:
    #     print(f'Failed to send data. Status code: {response.status_code}, Response: {response.text}')
   
    return True
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

            event_name,scrape_time, category, ticket_prices, sets_information, tickets_number = ticket_info(driver)
            json_data(event_name, scrape_time,category, ticket_prices, sets_information, tickets_number)
            
        driver.quit()
