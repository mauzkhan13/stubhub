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
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials

api_file  = {
    "type": "service_account",
    "project_id": "hardy-palace-377114",
    "private_key_id": "051e5ef61c34c36c60c5d790e0b2f53d992ec9a2",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDWqjQytZWczMVz\nbHMg2BfNEskKmOn6jzyxxkBDWtRdyY0Je/LCiJDnNDAQ0+v6+Ve4vE4MxCR7OCHz\nbNX4EJe6WOigjR5T+pWdvdk6TKf1lAnmy4ZG+8KiBKJxnscEcdQSNj/cWf0tpbgM\nL2VKYn2c/xYBC+Rof37C2giJIwYOogUVYbVwYCUrc5NZLnOix1B7YrPAdNxMjiW2\nzCWk07ziihm+fwekZTZpFEY3zG65zz4PEUmqHQ7/JUT/Sa7FO5qb+kkKy39EPl9e\ngEPyBxuGt87tu7Ny8/vJqAGoFDDRuedZkSG3JhX+H/I9b0zXf51QbHiZex3UUJf8\nuixLak97AgMBAAECggEAQXeJEcoFRdvBgBEcD3E32QgYng3ClfKnLQRsRt5lk/DK\n/ZB6mc9yecCVxBwNhO4UTbfICearxZR57jZMDypoS6Gf2I8RJ8Vtab0jib8lHiU2\n29dILU/MrQLC0+n7giSA68j1susS5p/6wGSX/JaK/p1hBZKt5xyy+RPrtH8k8sLx\n0lKevmJ1HsesekK7G4VX/sN9woWj9kk8Uu+664vJXh5X9ospqLXjJHv7lJKiFOl4\n5bK5mB1J1RWpdJqNDasy+jTyQmVKZWeWJlx3NP9oTIxLgRU5/0ymOx9RoMZQ0G6P\nX5r36i/yOlZHJ237vHwD9yj0yqtTlM8slGRj6vZoWQKBgQDr/ym+4pjmsK+F+v9Q\n40zmcRzOZQRxRf26NkKjn63FqSrJ9WGeoz68WegnVafM63ziKhWj63+WMxVYEwCJ\n/BlC0ZwPcvhU1DhT67t8qfSyLJSZALImMrUk74wUshWllPJwXTfCoRVrY2kyQLkL\ncM0AEkt/jx6grI0YdttbItjLZwKBgQDo3Cpl8qDjtDN0qvrsneOTpys1oHVEJz+a\nuWSBqG6+ZRCxcA6Wndchj9FLxPnOMU9nFjXRsSezMsQOCrskZguzzOElTOBV3Jma\nMqEmtd6sxpP5dz4acXWm8GAvNFICGhbkRu13qdLfra0wS1cqEjrgUVERlgWRgYpU\nYJKq5T5izQKBgFdPIWyjfJnsSCOzRn3weeTPeC7LpKcbk9Eufdz3GF0GRvRMuf7s\nuisIwCC9ScVAYgVyOGtalutEnuLktNBX2iikT65PhJwtn2E81zI51nOMlrU8Uqxb\nGjU+An8tm2CVCFSVyClTWw9Nyf9zfoJDCzS5kADzPAuJivHAF0tSSw6FAoGADIyx\nDEWDPkJb85GzbEUmGrMLtRwstbuXxfLv47z8Gu6/c5CieKOREJH7qaW4ANDPgrLD\nu8Vcal/2CPuzEkcdolcMW0JFZNs6vAC2hquOkKkzGGLAyhQLTy/tPx4GvW5ChZL9\nAVH5t2xYxR2KWQ4adjRrthLrwefFWL7LqMIqFpECgYEAlaJ/DqnUIyW7TH+gC1wJ\nyTM+FPYQA6GHGzYFWpfYfWEW59DyXBVhhv/5OocqoT9ntm0Cl3KAP481HmugN2GN\nAA1KoRobvwbcqP3Le8DGDslqsqtAoD0sts1wA3FCgJG8JPDbWdIrcXtzdxubIv+u\nWzBJVidT24oA0PtlqtSwQrM=\n-----END PRIVATE KEY-----\n",
    "client_email": "google-sheet-api@hardy-palace-377114.iam.gserviceaccount.com",
    "client_id": "101013958315517785766",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheet-api%40hardy-palace-377114.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
  }

def get_browser():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--headless')
    options.binary_location = '/usr/bin/google-chrome' 
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    print("Browser is successfully opened")
    return driver

def event_urls():
    global api_file
    events_links = []
    creds = Credentials.from_service_account_info(api_file,
                                                scopes=["https://spreadsheets.google.com/feeds",
                                                        "https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
    spreadsheet_id = '1fGZDIQPdtiS5wOPKmrqaCOScnnS9jTONw3sXOkYq99s'
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.get_worksheet(0)
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
    events_links = df
    print((events_links))
    return events_links
    
def scrolling_page(browser):
    max_retries = 3
    while True:
        try:
            retries = 0
            while retries < max_retries:
                try:
                    scroll_page = browser.find_element(By.XPATH, '//div[@class="RoyalInfiniteScroll__Loader"]/div')
                    # print('Scrolling')
                    scroll_page.click()
                    break
                except ElementClickInterceptedException:
                    try:
                        back_to_tickets = browser.find_element(By.XPATH, '//div[contains(text(),"Back to tickets")]')
                        back_to_tickets.click()
                        print("Clicked on Back to Tickets")
                    except (NoSuchElementException, StaleElementReferenceException):
                        print('back_to_tickets')
                        pass
                    retries += 1
                    sleep(0.3)
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
    # print(final_json_data_cleaned)

    save_data_url = 'https://pinhouse.seatpin.com/api/bot-webhook'
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(save_data_url, data=final_json_data_cleaned, headers=headers)
    if response.status_code == 200:
        print(f'Data successfully sent to the server.{response.status_code}')
    else:
        print(f'Failed to send data. Status code: {response.status_code}, Response: {response.text}')
    return True

if __name__ == '__main__':
    urls = event_urls()
    browser = get_browser()
    for url in urls[:1]:
        browser.get(url)
        scrolling_page(browser)
        event_name,scrape_time, category, ticket_prices, sets_information, tickets_number = ticket_info(browser)
        json_data(event_name,scrape_time, category, ticket_prices, sets_information, tickets_number)
        
    browser.quit()
# def process_event(url):
#     browser = get_browser()  # Instantiate a new browser
#     browser.get(url)
#     scrolling_page(browser)
#     category, ticket_prices, sets_information, tickets_number = ticket_info(browser)
#     success = json_data(category, ticket_prices, sets_information, tickets_number)
#     browser.quit()

#     if success:
#         print(f"Processing for URL {url} is complete.")
#     else:
#         print(f"Failed to extract JSON data for URL {url}.")
    
# if __name__ == '__main__':
#     urls = event_urls(get_browser())  # Instantiate a single browser instance

#     # Define the maximum number of threads
#     max_threads = 1

#     with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
#         executor.map(process_event, urls)

#     print("All event URLs have been processed.")
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
