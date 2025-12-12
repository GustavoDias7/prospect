from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from core import models
from django.core.management.base import BaseCommand
import urllib.parse
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import re

class Command(BaseCommand):
    def handle(self, *args, **options):
        options = Options()
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(652, 768 - 20)
        driver.set_window_position(0, 0)

        driver.get("https://lite.duckduckgo.com/lite/")
        search = input("Search: ")
        sites = [
            "site:instagram.com", 
            "-site:instagram.com/p/", 
            "-site:instagram.com/reel/", 
            "-site:instagram.com/reels/", 
            "-site:instagram.com/stories/"
        ]
        query = f"{search} {' '.join(sites)}"
        
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
        
        not_contacted = models.InteractionStatus.objects.get(name="Not contacted")
        while continue_script.lower() == "y":
            print(f"Page {counter_page}")
            
            # check bot page
            try:
                driver.find_element(By.CSS_SELECTOR, '.anomaly-modal__title')
                input("Bot page, press enter to continue")      
            except:
                pass
            
            body = driver.find_element(By.TAG_NAME, "body")
            soup = BeautifulSoup(body.get_attribute("outerHTML"))
            
            # contacts = []
            for link in soup.find_all('a', class_='result-link'):
                href = urllib.parse.urlparse(link.get("href"))
                business = models.Business()
                username = href.path.split("/")[1]
                if username in ("reel", "tv", "c", "p", "stories"): continue
                business.instagram_username = username
                
                td = link.parent
                tr = td.parent
                tr_next = tr.next_sibling.next_sibling
                result_snippet = tr_next.find("td", class_="result-snippet")
                result_snippet_text = result_snippet.get_text()
                
                pattern = r'([\d,.]+K?)[ ]*Followers'
                matches = re.search(pattern, result_snippet_text)
                
                if matches:
                    followers = matches.group(1)
                    if "K" in followers:
                        number = followers.replace("K", "")
                        business.followers = int(number) * 1000
                    else:
                        number = followers.replace(",", "")
                        business.followers = int(number)
                    
                try:
                    business.save()
                    interaction = models.Interaction()
                    interaction.status = not_contacted
                    interaction.business = business
                    interaction.save()
                except Exception as e:
                    print(e)
                
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

