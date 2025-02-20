from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from core.models import InstagramContact
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

        input_query = driver.find_element(By.CLASS_NAME, "query")
        input_query.send_keys(query)
        input_query.send_keys(Keys.RETURN)
        time.sleep(3)

        select = Select(driver.find_element(By.CSS_SELECTOR, '.filters select'))
        select.select_by_value('br-pt')

        input_query = driver.find_element(By.CLASS_NAME, "query")
        input_query.send_keys(Keys.RETURN)
        
        continue_script = "y"
        while continue_script.lower() == "y":
            links = driver.find_elements(By.CLASS_NAME, 'result-link')
            contacts = []
            for link in links:
                href = urllib.parse.urlparse(link.get_attribute("href"))
                contact = InstagramContact()
                username = href.path.split("/")[1]
                if username in ("reel", "tv", "c", "p", "stories"): continue
                contact.username = username
                contacts.append(contact)
                
            InstagramContact.objects.bulk_create(contacts, ignore_conflicts=True)
                
            next_form = driver.find_element(By.CLASS_NAME, "next_form")
            next_form.submit()

            time.sleep(3)
            
            continue_script = input("Continue script? [y/n] ")
        
        driver.close()

