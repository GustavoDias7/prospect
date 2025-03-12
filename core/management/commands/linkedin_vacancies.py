from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from core import models
from django.core.management.base import BaseCommand
import urllib.parse
from django.conf import settings
from selenium.webdriver.support.ui import Select
from prospect.utils import open_tab, close_tab, has_term

class Command(BaseCommand):
    def handle(self, *args, **options):
        options = Options()
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(652, 768 - 20)
        driver.set_window_position(0, 0)

        driver.get("https://lite.duckduckgo.com/lite/")
        search = input("Search: ")
        site_flag = "www.linkedin.com/jobs/view"
        query = f"{search} site:{site_flag}"
        
        auto_continue = input("Auto continue? [y/n] ")
        
        pages = int(input("Pages: ") or 10)

        input_query = driver.find_element(By.CLASS_NAME, "query")
        input_query.send_keys(query)
        input_query.send_keys(Keys.RETURN)
        time.sleep(3)

        select = Select(driver.find_element(By.CSS_SELECTOR, '.filters select'))
        select.select_by_value('br-pt')
        time.sleep(3)

        input_query = driver.find_element(By.CLASS_NAME, "query")
        input_query.send_keys(Keys.RETURN)
        time.sleep(3)
        
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
            
            # get vacancy links and set to model
            links = driver.find_elements(By.CSS_SELECTOR, f'a[href*="{site_flag}]"')
            vacancies = []
            for link in links:
                href = link.get_attribute("href")
                title = link.get_attribute("innerText")
                vacancy = models.Vacancy()
                
                print("href:", href)
                
                vacancy.name = title.replace(" - LinkedIn", "")
                
                back_end_terms = ("back end", "backend", "back-end")
                fullstack_terms = ("full stack", "fullstack", "full-stack")
                front_end_terms = ("front end", "frontend", "front-end")
                
                if has_term(title, back_end_terms):
                    vacancy.category = models.VacancyCategory.objects.get(name="Back-End")
                elif has_term(title, fullstack_terms):
                    vacancy.category = models.VacancyCategory.objects.get(name="FullStack")
                elif has_term(title, front_end_terms):
                    vacancy.category = models.VacancyCategory.objects.get(name="Front-End")
                
                # back_end_terms = ("back end", "backend", "back-end")
                # fullstack_terms = ("full stack", "fullstack", "full-stack")
                
                # if has_term(title, back_end_terms):
                #     vacancy.modality = models.VacancyModality.objects.get(name="Back-End")
                # elif has_term(title, fullstack_terms):
                #     vacancy.modality = models.VacancyModality.objects.get(name="FullStack")
                    
                clt_terms = ("CLT",)
                pj_terms = ("PJ",)
                if has_term(title, clt_terms):
                    vacancy.hiring = models.VacancyHiring.objects.get(name="CLT")
                elif has_term(title, pj_terms):
                    vacancy.hiring = models.VacancyHiring.objects.get(name="PJ")
                    
                junior_terms = ("Junior", "Jr")
                pleno_terms = ("Pleno", "Pl")
                senior_terms = ("Senior", "Sr")
                
                if has_term(title, junior_terms):
                    vacancy.level = models.VacancyLevel.objects.get(name="Junior")
                elif has_term(title, pleno_terms):
                    vacancy.level = models.VacancyLevel.objects.get(name="Pleno")
                elif has_term(title, senior_terms):
                    vacancy.level = models.VacancyLevel.objects.get(name="Senior")
                
                parsed_link = urllib.parse.urlparse(href)
                job_view = parsed_link.path.split("/")
                vacancy.job_view = job_view[3]
                
                vacancies.append(vacancy)
                
            # create vacancies
            models.Vacancy.objects.bulk_create(vacancies, ignore_conflicts=True)
                
            next_form = driver.find_element(By.CLASS_NAME, "next_form")
            next_form.submit()
            
            time.sleep(2)
            
            # check for no results.
            try:
                no_results = driver.find_element(By.CSS_SELECTOR, '.no-results')
                if no_results: break
            except:
                pass
            
            counter = counter + 1
            counter_page = counter_page + 1
            if counter > pages:
                continue_script = input(f"More {pages} pages? [y/n] ")
                counter = 1
            else:
                if auto_continue.lower() == "y":
                    time.sleep(5)
                else:
                    input("Press enter to continue ")
        
        driver.close()


