from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from core import models
from django.core.management.base import BaseCommand
import urllib.parse
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        options = Options()
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(652, 768 - 20)
        driver.set_window_position(0, 0)

        driver.get("https://www.linkedin.com")
        
        time.sleep(5)
        
        # form = driver.find_element(By.CLASS_NAME, "login__form")
        # username = driver.find_element(By.ID, "username")
        # password = driver.find_element(By.ID, "password")
        
        # if settings.LINKEDIN_USERNAME and settings.LINKEDIN_PASSWORD:
        #     if username and password and form:
        #         username.send_keys(settings.LINKEDIN_USERNAME)
        #         password.send_keys(settings.LINKEDIN_PASSWORD)
        #         form.submit()
        #     else:
        #         print(form, username, password)
        #         return
        # else:
        #     print("Missing LinkedIn credentials")
        #     return
        
        time.sleep(5)
        
        search = input("Search: ")
        if search == "": search = "(desenvolvedor OR programador) AND (django OR flask)"
        
        def get_query(page: int) -> str:
            return f"https://www.linkedin.com/search/results/people/?keywords={search}&page={page}"
        
        driver.get(get_query(1))
        
        time.sleep(5)

        page = 1
        continue_script = "y"
        while continue_script.lower() == "y":
            links_selector = "ul div > span > span > a[href*='www.linkedin.com/in/']"
            links = driver.find_elements(By.CSS_SELECTOR, links_selector)
            contacts = []
            for link in links:
                href = urllib.parse.urlparse(link.get_attribute("href"))
                contact = models.LinkedInContact()
                username = href.path.split("/")[2]
                contact.username = username
                contacts.append(contact)
                
            models.LinkedInContact.objects.bulk_create(contacts, ignore_conflicts=True)
            
            page = page + 1
            driver.get(get_query(page))

            time.sleep(2)
            
            continue_script = input("Continue script? [y/n] ")
        
        driver.close()

