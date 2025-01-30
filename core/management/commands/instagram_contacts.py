from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from core.models import InstagramContact
from django.core.management.base import BaseCommand
import urllib.parse


class Command(BaseCommand):
    def handle(self, *args, **options):
        options = Options()
        driver = webdriver.Firefox(options=options)

        driver.get("https://lite.duckduckgo.com/lite/")
        search = input("Search: ")
        query = f"{search} site:instagram.com"

        input_query = driver.find_element(By.CLASS_NAME, "query")
        input_query.send_keys(query)
        input_query.send_keys(Keys.RETURN)

        time.sleep(3)

        continue_script = "y"
        while continue_script == "y":
            if continue_script.lower() == "y":
                
                links = driver.find_elements(By.CLASS_NAME, 'result-link')
                contacts = []
                for link in links:
                    href = urllib.parse.urlparse(link.get_attribute("href"))
                    contact = InstagramContact()
                    contact.username = href.path.split("/")[1]
                    contacts.append(contact)
                
                InstagramContact.objects.bulk_create(contacts, ignore_conflicts=True)
                    
                next_form = driver.find_element(By.CLASS_NAME, "next_form")
                next_form.submit()

                time.sleep(3)
            else:
                driver.close()
                break
            
            continue_script = input("Continue script? [y/n] ")

