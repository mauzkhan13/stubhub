import threading
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
from seleniumwire import webdriver
import time
from colorama import Fore
import undetected_chromedriver as uc
from selenium_stealth import stealth
def get_browser():
    chromedriver_path = ChromeDriverManager().install()
    
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-logging')
    options.add_argument('--enable-automation')
    options.add_argument('--log-level=3')
    options.add_argument('--v=99') 
    options.add_argument('--headless')
    options.binary_location = '/usr/bin/chromedriver' 
    options.add_experimental_option('prefs', {
        'profile.managed_default_content_settings.images': 1,
        'profile.managed_default_content_settings.stylesheets': 2,
        'profile.managed_default_content_settings.plugins': 2,
        'profile.managed_default_content_settings.popups': 2,
        'profile.managed_default_content_settings.geolocation': 2,
        'profile.managed_default_content_settings.notifications': 2,
        'profile.managed_default_content_settings.mouselock': 2,
        'profile.managed_default_content_settings.pointerLock': 2,
        'profile.managed_default_content_settings.webusb': 2,
        'profile.managed_default_content_settings.webxr': 2,
    
    })
    # options.page_load_strategy = 'eager'
    try:
        driver = uc.Chrome(options=options)
    except:
        driver = uc.Chrome(service=ChromeService(chromedriver_path))
        print(f"ChromeDriver installed at: {chromedriver_path}")
    
    driver.execute_script("window.stop();")
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    while driver.execute_script("return document.readyState") != "complete":
        pass
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
                        # print("Clicked on Back to Tickets")
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

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()


def ticket_info(driver):

    category,ticket_prices,sets_information,tickets_number,event_name,scrape_time = [],[],[],[],[],[]
    event_date,event_time, venue, city, city_shortcode = [], [], [], [], []
    
    # sleep(3)
    
    wait = WebDriverWait(driver, 5)
    try:
        accept_cookies = wait.until( EC.visibility_of_element_located((By.XPATH, '//span[contains(text(),"Accept All")]')))
        accept_cookies.click()
        # print('Cookies are accepted...')
    except Exception:
        pass
        
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    card_elements = soup.select('ul.RoyalTicketList__container > li')

    scrape_times = datetime.now().strftime('%H:%M:%S, %d-%m-%Y')
    scrape_time.append(scrape_times)

    

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

        event_date.append(driver.find_element(By.XPATH, '//div[@class="event-info"]/span').text)
    
        event_time.append(driver.find_element(By.XPATH, '//div[@class="event-info"]/time').text)
        event_name.append(driver.find_element(By.XPATH, '//h1').text.strip())
        texts = driver.find_element(By.XPATH, '//div[@class="event-info"]/span[2]').text
        if texts:
            text_split = texts.split(',')
            
            if len(text_split) > 0:
                text1 = text_split[0]
                venue.append(text1.replace('at', '').strip())
            else:
                venue.append('N/A')
            
            if len(text_split) > 1:
                text2 = text_split[1]
                city.append(text2.strip())
            else:
                city.append('N/A')
            
            if len(text_split) > 2:
                text3 = text_split[2]
                city_shortcode.append(text3.strip())
            else:
                city_shortcode.append('N/A')
        else:
            venue.append('N/A')
            city.append('N/A')
            city_shortcode.append('N/A')
        

    return event_name,event_date,event_time, venue, city, city_shortcode,scrape_time, category, ticket_prices, sets_information, tickets_number


def json_data(url,event_name,event_date,event_time, venue, city, city_shortcode,scrape_time, category, ticket_prices, sets_information, tickets_number):
    print(Fore.WHITE + f"Total Numbers of category", len(category), {url})
    event_df = pd.DataFrame(zip(event_name,event_date, event_time,venue, city, city_shortcode,scrape_time), columns=['Event Name', 'Event Date','Event Time','Venue','City','City Short Code','Scraped Time'])
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
    sleep(1)
    response = requests.post(save_data_url, data=final_json_data_cleaned, headers=headers)
    if response.status_code == 200:
        print(f'Data successfully sent to the server.{response.status_code}')
    else:
        print(f'Failed to send data. Status code: {response.status_code}, Response: {response.text}')
    return True

def process_url(index, url):
    print(Fore.YELLOW +f"Processing URL No {index}: {url}")
    browser = get_browser()
    try:
        browser.get(url)
        scrolling_page(browser)
        event_name,event_date,event_time, venue, city, city_shortcode,scrape_time, category, ticket_prices, sets_information, tickets_number = ticket_info(browser)
        json_data(url,event_name,event_date,event_time, venue, city, city_shortcode,scrape_time, category, ticket_prices, sets_information, tickets_number)
    except Exception as e:
        print(Fore.RED +f"Error processing URL {url}: {e}")
    finally:
        browser.quit()

def main():
    urls = event_urls()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_url, index, url) for index, url in enumerate(urls)]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = end_time - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(Fore.GREEN + f"Total time to complete: {int(hours)}:{int(minutes)}:{seconds:.2f}")




