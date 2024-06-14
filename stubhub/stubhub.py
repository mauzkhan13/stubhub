
from selenium import webdriver
import threading
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException,StaleElementReferenceException
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from time import sleep
from bs4 import Tag
from lxml import html
import re

def get_browser():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--headless')
    
    website = "https://www.stubhub.ie/euro-2024-tickets/grouping/1507012/?wcpb=4"
    grid_url = "http://localhost:4444/wd/hub"
    driver = webdriver.Remote(command_executor=grid_url, options=options)
    driver.get(website)
    driver.maximize_window()
    print("Browser is successfully opened")
    return driver

def event_urls(browser): 
    while True:
        try:
            
            next_page = browser.find_element(By.XPATH, '(//*[contains(text(),"See more events")])[2]')
            next_page.click()
            sleep(1)
        except (NoSuchElementException, TimeoutException):
            break

    events_links = []
    soup = BeautifulSoup(browser.page_source, 'lxml')
    divs = soup.find_all('a', {'class': 'cbt-redirection__link EventItem__TitleLink'})
    base_url = 'https://www.stubhub.ie/'
    for link in divs[:1]:
        url = link.get('href')
        complete_url = base_url + url
        events_links.append(complete_url)
        print("Scraped all Events Link")
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
    
    file_path = r"C:\Users\Mauz Khan\Desktop\StubHub.json"
    
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
        
    print("The scraper is successfully finished")

if __name__ == '__main__':
    browser = get_browser()
    urls = event_urls(browser)
    browser.quit() 

    for url in urls:
        
        browser = get_browser()
        browser.get(url)
        scrolling_page(browser)
        category, ticket_prices, sets_information, tickets_number = ticket_info(browser)
        json_data(category, ticket_prices, sets_information, tickets_number)
        browser.quit() 
