from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from core.models import Business
from django.core.management.base import BaseCommand
import urllib.parse
from selenium.webdriver.support.ui import Select

class Command(BaseCommand):
    def handle(self, *args, **options):
        options = Options()
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(652, 768 - 20)
        driver.set_window_position(0, 0)

        driver.get("https://lite.duckduckgo.com/lite/")
        search = input("Search: ")
        query = f"{search} site:instagram.com"
        
        pages = int(input("Pages: ")) or 10

        input_query = driver.find_element(By.CLASS_NAME, "query")
        input_query.send_keys(query)
        input_query.send_keys(Keys.RETURN)
        time.sleep(3)

        select = Select(driver.find_element(By.CSS_SELECTOR, '.filters select'))
        select.select_by_value('br-pt')
        time.sleep(1)

        input_query = driver.find_element(By.CLASS_NAME, "query")
        input_query.send_keys(Keys.RETURN)
        
        continue_script = "y"
        counter = 1
        counter_page = 1
        while continue_script.lower() == "y":
            print(f"Page {counter_page}")
            
            # check bot page
            try:
                driver.find_element(By.CSS_SELECTOR, '.anomaly-modal__title')
                input("Bot page, press enter to continue")      
            except:
                pass
            
            links = driver.find_elements(By.CLASS_NAME, 'result-link')
            contacts = []
            for link in links:
                href = urllib.parse.urlparse(link.get_attribute("href"))
                contact = Business()
                username = href.path.split("/")[1]
                if username in ("reel", "tv", "c", "p", "stories"): continue
                contact.username = username
                contacts.append(contact)
                
            Business.objects.bulk_create(contacts, ignore_conflicts=True)
                
            next_form = driver.find_element(By.CLASS_NAME, "next_form")
            next_form.submit()
            
            counter = counter + 1
            counter_page = counter_page + 1
            if counter > pages:
                continue_script = input(f"More {pages} pages? [y/n] ")
                counter = 1
            else:
                time.sleep(4)
        
        driver.close()

