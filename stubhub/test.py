import threading
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from bs4 import BeautifulSoup
from lxml import html
from time import sleep
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
import pymysql
from datetime import datetime
import re
import time
import json
import os
import requests

def get_browser():
    chromedriver_path = ChromeDriverManager().install()
   
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--headless')
    options.binary_location = '/usr/bin/chromedriver' 
    try:
        driver = webdriver.Chrome(options=options)
    except:
        driver = webdriver.Chrome(service=ChromeService(chromedriver_path), options=options)
        print(f"ChromeDriver installed at: {chromedriver_path}")
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # try:
    # driver = webdriver.Chrome(options=options)
    #     print('driver is working')
    # except:
        # print('Need to install chrome driver is working')
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=options)
    # print('driver is working')
    # driver = webdriver.Chrome(options=options)
    # url = 'https://www.stubhub.ie/euro-2024-tickets/grouping/1507012/?wcpb=4'
    # driver.get(url)
    # print("Browser is successfully opened")
    driver.maximize_window()
    
    return driver

def event_urls():
    event_links = []
    conn = pymysql.connect(
        host='localhost',
        user='stubhub_user',
        password='Stubhub358*',
        database='stubhub'
    )
        
    cursor = conn.cursor()
    query = "SELECT * FROM urls"
    cursor.execute(query)
    rows = cursor.fetchall()
    
    for row in rows:
        url = row[1]  
        event_links.append(url)
    
    # for url in event_urls:
    #     print(url)
    print(f"Total event URLs fetched: {len(event_links)}")
    cursor.close()
    conn.close()
    
    return event_links
    

def scrolling_page(browser):
    max_retries = 3
    while True:
        try:
            retries = 0
            while retries < max_retries:
                try:
                    scroll_page = browser.find_element(By.XPATH, '//div[@class="RoyalInfiniteScroll__Loader"]/div')
                    # print('scrolling')
                    scroll_page.click()
                    break
                except ElementClickInterceptedException:
                    try:
                        back_to_tickets = browser.find_element(By.XPATH, '//div[contains(text(),"Back to tickets")]')
                        back_to_tickets.click()
                        print("Clicked on Back to Tickets")
                    except (NoSuchElementException, StaleElementReferenceException):
                        pass
                    retries += 1
                    sleep(0.3)
            else:
                pass
        except StaleElementReferenceException:
            pass
        except NoSuchElementException:
            break

# def clean_text(text):
#     return text.replace('\\u20ac', '').replace('\\u00a', ' ').replace('\\', '').replace('\xa0','')

# def ticket_info(browser):

#     soup = BeautifulSoup(browser.page_source, 'html.parser')
#     card_elements = soup.select('ul.RoyalTicketList__container > li')
#     category = []
#     ticket_prices = []
#     sets_information = []
#     tickets_number = []
#     for card_element in card_elements:
#         element = html.fromstring(str(card_element))

#         cat = card_element.select_one('div.SectionRowSeat__sectionTitle.RoyalTicketListPanel__SectionName')
#         category_text = clean_text(cat.text.strip()) if cat else 'N/A'
#         category.append(category_text)

#         sets_info = card_element.select('span.SectionRowSeat__row')
#         if sets_info:
#             cleaned_sets_info = ' '.join([clean_text(set_no.text.replace('0','').strip()) for set_no in sets_info])
#             sets_information.append(cleaned_sets_info)
#         else:
#             sets_information.append('N/A')

#         price = card_element.select_one('div.PriceDisplay__price')
#         price_text = clean_text(price.text.strip()) if price else 'N/A'
#         ticket_prices.append(price_text)

#         tickets = element.xpath('//div[@class="RoyalTicketListPanel__SecondaryInfo"]/text()[normalize-space()]')
#         if tickets:
#             cleaned_tickets = ' '.join([clean_text(ticket.strip()) if isinstance(ticket, str) else clean_text(ticket.strip()) for ticket in tickets])
#             tickets_number.append(cleaned_tickets)
#         else:
#             tickets_number.append('N/A')

#     return category, ticket_prices, sets_information, tickets_number

# def json_data(url, category, ticket_prices, sets_information, tickets_number):
#     print(f"Total Numbers of category", len(category), {url})
#     df = pd.DataFrame(zip(category, ticket_prices, sets_information, tickets_number), columns=['Category', 'Ticket Prices', 'Set information', 'Ticket Number'])

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

def json_data(url,event_name,scrape_time, category, ticket_prices, sets_information, tickets_number):
    print(f"Total Numbers of category", len(category), {url})
    event_df = pd.DataFrame(zip(event_name,scrape_time), columns=['Event Name', 'Scraped Time'])
    event_data = json.loads(event_df.to_json(orient='records'))

    df = pd.DataFrame(zip(category, ticket_prices, sets_information, tickets_number), columns=['Category', 'Ticket Prices', 'Set information', 'Ticket Number'])
    new_data = json.loads(df.to_json(orient='records'))
    
    json_data_cleaned_str = json.dumps(new_data).replace('\\u20ac', '').replace('\\u00a', ' ').replace('\\', '').replace('\xa0','')

    json_data_cleaned = json.loads(json_data_cleaned_str)
    
    combined_data = event_data + json_data_cleaned
    
    final_json_data = json.dumps(combined_data)
    
    final_json_data_cleaned = final_json_data.replace('\n', '')
    # print(final_json_data_cleaned)

    save_data_url = 'https://pinhouse.seatpin.com/api/bot-webhook'
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(save_data_url, data=final_json_data_cleaned, headers=headers)
    if response.status_code == 200:
        print(f'Data successfully sent to the server.{response.status_code}')
    else:
        print(f'Failed to send data. Status code: {response.status_code}, Response: {response.text}')
    return True

def process_url(index, url):
    print(f"Processing URL No {index}: {url}")
    browser = get_browser()
    try:
        browser.get(url)
        # print(f"Successfully opened URL: {url}")
        
        scrolling_page(browser)
        # print("Finished scrolling the page")
        event_name,scrape_time, category, ticket_prices, sets_information, tickets_number = ticket_info(browser)
        # category, ticket_prices, sets_information, tickets_number = ticket_info(browser)
        # print("Extracted ticket information")
        
        # json_data(url, category, ticket_prices, sets_information, tickets_number)
        json_data(url,event_name,scrape_time, category, ticket_prices, sets_information, tickets_number)
        # print("Processed ticket information into JSON")
        
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
    finally:
        browser.quit()

def main():
    urls = event_urls()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_url, index, url) for index, url in enumerate(urls)]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()




