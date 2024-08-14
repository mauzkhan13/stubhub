import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from bs4 import BeautifulSoup
from lxml import html
from time import sleep



def get_browser():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--headless')
    # options.binary_location = '/usr/bin/google-chrome' 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    # driver = webdriver.Chrome(options=options)
    # url = 'https://www.stubhub.ie/euro-2024-tickets/grouping/1507012/?wcpb=4'
    # driver.get(url)
    driver.maximize_window()
    print("Browser is successfully opened")
    return driver

def event_urls():
    global api_file
    event_links = []

    creds = Credentials.from_service_account_info(api_file,
                                                scopes=["https://spreadsheets.google.com/feeds",
                                                        "https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
    spreadsheet_id = '1fGZDIQPdtiS5wOPKmrqaCOScnnS9jTONw3sXOkYq99s'
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.get_worksheet(0)
    records = worksheet.get_all_records()

    event_links = [record['URL'] for record in records]
    print(f"Total event URLs fetched: {len(event_links)}")
    return event_links
    
  

def scrolling_page(browser):
    max_retries = 3
    while True:
        try:
            retries = 0
            while retries < max_retries:
                try:
                    scroll_page = browser.find_element(By.XPATH, '//div[@class="RoyalInfiniteScroll__Loader"]/div')
                    print('scrolling')
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
    print("Total Numbers of category", len(category))
    df = pd.DataFrame(zip(category, ticket_prices, sets_information, tickets_number), columns=['Category', 'Ticket Prices', 'Set information', 'Ticket Number'])


def process_url(index, url):
    print(f"Thread {threading.current_thread().name} processing index {index}: {url}")
    browser = get_browser()
    try:
        browser.get(url)
        scrolling_page(browser)
        category, ticket_prices, sets_information, tickets_number = ticket_info(browser)
        json_data(category, ticket_prices, sets_information, tickets_number)
    finally:
        browser.quit()
    print(f"Thread {threading.current_thread().name} finished processing index {index}")

def main():
    urls = event_urls()
    
    # print(f"URLs retrieved: {urls}") 
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(process_url, index, url) for index, url in enumerate(urls)]
        # futures = [executor.submit(process_url, urls) for i in range(len(urls))]
        concurrent.futures.wait(futures)
if __name__ == "__main__":
    main()

