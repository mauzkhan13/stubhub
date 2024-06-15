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
import threading
import concurrent.futures
import requests

def get_browser():
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
    url = 'https://www.stubhub.ie/euro-2024-tickets/grouping/1507012/?wcpb=4'
    driver.get(url)
    print("Browser is successfully opened")
    return driver

def event_urls(browser):
    wait = WebDriverWait(browser, 10)  # Wait up to 10 seconds
        
    # Dismiss the cookie modal overlay if it exists
    try:
        cookie_overlay = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'cookieModal__overlay')))
        browser.execute_script("arguments[0].click();", cookie_overlay)
        print("Dismissed the cookie modal overlay.")
    except TimeoutException:
        print("Cookie modal overlay not found.")
    
    next_page = wait.until(EC.element_to_be_clickable((By.XPATH, '(//*[contains(text(),"See more events")])[2]')))
    print("Element found, attempting to click...")
    next_page.click()
    print("Clicked successfully.")
        
    events_links = []
    soup = BeautifulSoup(browser.page_source, 'lxml')
    divs = soup.find_all('a', {'class': 'cbt-redirection__link EventItem__TitleLink'})
    base_url = 'https://www.stubhub.ie/'
    for link in divs:
        url = link.get('href')
        complete_url = base_url + url
        events_links.append(complete_url)
    print("Total Number of Event Links:", len(events_links))
    return events_links

def scrolling_page(browser):
    max_retries = 3
    while True:
        try:
            retries = 0
            while retries < max_retries:
                try:
                    scroll_page = browser.find_element(By.XPATH, '//div[@class="RoyalInfiniteScroll__Loader"]/div')
                    scroll_page.click()
                    break
                except ElementClickInterceptedException:
                    retries += 1
                    sleep(0.3)
            else:
                pass
        except StaleElementReferenceException:
            pass
        except NoSuchElementException:
            break

def clean_text(text):
    return text.replace('\\u20ac', '').replace('\\u00a', ' ').replace('\\', '').replace('\xa0','')

def ticket_info(browser):
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    card_elements = soup.select('ul.RoyalTicketList__container > li')

    category = []
    ticket_prices = []
    sets_information = []
    tickets_number = []

    for card_element in card_elements:
        element = html.fromstring(str(card_element))

        cat = card_element.select_one('div.SectionRowSeat__sectionTitle.RoyalTicketListPanel__SectionName')
        category_text = clean_text(cat.text.strip()) if cat else 'N/A'
        category.append(category_text)

        sets_info = card_element.select('span.SectionRowSeat__row')
        if sets_info:
            cleaned_sets_info = ' '.join([clean_text(set_no.text.replace('0','').strip()) for set_no in sets_info])
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

    return category, ticket_prices, sets_information, tickets_number

def json_data(category, ticket_prices, sets_information, tickets_number):
    
    df = pd.DataFrame(zip(category, ticket_prices, sets_information, tickets_number), columns=['Category', 'Ticket Prices', 'Set information', 'Ticket Number'])
    file_path = r"C:\Users\Mauz Khan\Desktop\stubhub.json"
    new_data = json.loads(df.to_json(orient='records'))

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    combined_data = existing_data + new_data

    json_data_cleaned = json.dumps(combined_data).replace('\\u20ac', '').replace('\\u00a', ' ').replace('\\', '').replace('\xa0','')

    with open(file_path, 'w') as f:
        f.write(json_data_cleaned)
    return True


def process_event(url):
    browser = get_browser()  # Instantiate a new browser
    browser.get(url)
    scrolling_page(browser)
    category, ticket_prices, sets_information, tickets_number = ticket_info(browser)
    success = json_data(category, ticket_prices, sets_information, tickets_number)
    browser.quit()

    if success:
        print(f"Processing for URL {url} is complete.")
    else:
        print(f"Failed to extract JSON data for URL {url}.")
    
if __name__ == '__main__':
    urls = event_urls(get_browser())  # Instantiate a single browser instance

    # Define the maximum number of threads
    max_threads = 1

    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        executor.map(process_event, urls)

    print("All event URLs have been processed.")
# if __name__ == '__main__':
#     browser = get_browser()
#     urls = event_urls(browser)
#     browser.quit()

#     threads = []
#     for index, url in enumerate(urls):
#         thread = threading.Thread(target=process_event, args=(index, url))
#         threads.append(thread)
#         thread.start()

#     for thread in threads:
#         thread.join()
