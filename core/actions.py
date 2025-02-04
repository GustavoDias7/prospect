from django.contrib import admin, messages
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import urllib.parse
import requests
from prospect.utils import (get_phone, has_string_in_list)
from . import models
from datetime import datetime, timedelta
from django.utils import timezone

@admin.action(description="Get data from the Facebook page", permissions=["change"])
def get_datas(modeladmin, request, queryset):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("start-maximized")
    driver = webdriver.Firefox(options=options)
    
    for query in queryset:
        try:
            driver.get(query.get_facebook())
            
            time.sleep(3)
            
            html_source = driver.execute_script("return document.body.outerHTML;")
            soup = BeautifulSoup(html_source, "html.parser")
            body = soup.get_text(separator="|")
            
            # print("body:", body)
            
            position = body.find("Advertising") # to remove other invalid links to website field
            body = body[:position]
            
            # print("soup:", soup)
            # print("body:", body)
            
            # find page name
            page_name = soup.find(name="h1")
            if page_name:
                query.name = page_name.get_text()
            else:
                print("name not found")

            # find phone number 
            phone_pattern = r'\(\d{2}\)\s?\d{4,5}-\d{4}'
            phone = re.search(phone_pattern, body)
            if phone:
                query.whatsapp = re.sub(r"\D", "", phone.group())
            else:
                print("phone not found")
            
            # find e-mail address
            email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
            email = re.search(email_pattern, body)
            if email:
                query.email = email.group()
            else:
                print("email not found")
            
            # find address
            address_pattern = r'(?<=\|)[^|]*\bBrazil\b[^|]*(?=\|)'
            address = re.search(address_pattern, body)
            if address:
                query.address = address.group()
            else:
                print("address not found")
            
            # find website url
            website_pattern = r'(?<=\|)((https?://)?(www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,})(?:/[^|?]*)?(?:\?[^|]*)?(?=\|)'
            website = re.search(website_pattern, body)
            if website:
                query.website = website.group()
            else:
                print("website not found")
            
            # find instagram username
            instagram_pattern = r'@([A-Za-z0-9._]+)'
            instagram = re.search(instagram_pattern, body)
            if instagram:
                insta = instagram.group()
                if email and insta not in email.group():
                    query.instagram = insta.replace("@", "")
                elif not email: 
                    query.instagram = insta.replace("@", "")
            else:
                print("instagram not found")
                
            query.save()
        except Exception as e:
            print(e)
            messages.error(request, str(e))
    
    driver.close()

@admin.action(description="Disqualify contact", permissions=["change"])
def disqualify(modeladmin, request, queryset):
    queryset.update(qualified=False)
                
@admin.action(description="Qualify contact", permissions=["change"])
def qualify(modeladmin, request, queryset):
    queryset.update(qualified=True)
                
@admin.action(description="It was contacted", permissions=["change"])
def contacted(modeladmin, request, queryset):
    queryset.update(contacted=True)
                
@admin.action(description="Archive contact", permissions=["change"])
def archive(modeladmin, request, queryset):
    queryset.update(archived=True)
    
@admin.action(description="Has menu", permissions=["change"])
def has_menu(modeladmin, request, queryset):
    queryset.update(menu=True)
    
@admin.action(description="Has no menu", permissions=["change"])
def not_menu(modeladmin, request, queryset):
    queryset.update(menu=False)

@admin.action(description="Get data from the Instagram page", permissions=["change"])
def get_instagram_data(modeladmin, request, queryset):
    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.instagram.com/")
    
    time.sleep(5)
    
    form = driver.find_element(By.ID, "loginForm")
    username = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
    password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    
    username.send_keys("saudavel_por_inteiro")
    password.send_keys("maissaude")
    form.submit()
            
    time.sleep(10)
    for query in queryset:
            
        driver.get(query.get_instagram_link())
            
        time.sleep(10)
    
        # name
        title = driver.find_element(By.TAG_NAME, "title")
        if title:
            title = title.get_attribute("innerText")
            
            if "@" in title:
                name = re.search(r"(.*?)\s?\(@", title)
                if name:
                    query.name = name.group(1)
                    
        role_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
        if role_buttons:
            # open "more" button from bio
            for role_button in role_buttons:
                outer_text = role_button.get_attribute("outerText")
                if not outer_text: continue
                if "more" in outer_text:
                    role_button.click()
                    break
            
            # get number from bio
            for role_button in role_buttons:
                try:
                    # more button does not exist -> StaleElementReferenceException
                    outer_text = role_button.get_attribute("outerText")
                except:
                    continue
                
                if not outer_text: continue
                
                phone_number = get_phone(outer_text)
                if phone_number:
                    query.phone = phone_number
                    break
        
        highlights = driver.find_elements(By.CSS_SELECTOR, "section ul > li [role='button']")
        if highlights:
            for highlight in highlights:
                try:
                    outer_text = highlight.get_attribute("outerText")
                except:
                    continue
                
                if not outer_text: continue
                
                menu_terms = ["catálogo", "cardápio", "menu", "pratos", "pizzas"]
                has_menu_in_highlight = has_string_in_list(outer_text, menu_terms)
                if has_menu_in_highlight:
                    query.menu = True
                    break
                    
        # open link modals
        buttons = driver.find_elements(By.TAG_NAME, "button")
        if buttons:
            for button in buttons:
                outer_text = button.get_attribute("outerText")
                if " + " in outer_text:
                    button.click()
                    break
        
        # website
        links_to_redirect = driver.find_elements(By.CSS_SELECTOR, "a[href*='l.instagram.com']")
        if links_to_redirect:
            websites = models.Website.objects.all()
            for link in links_to_redirect:
                href = urllib.parse.urlparse(link.get_attribute("href"))
                query_params = urllib.parse.parse_qs(href.query)
                u_value = query_params.get('u', [None])[0]
                website = urllib.parse.unquote(u_value).split('?')[0]
                query.website = website
                
                stop_bitly = False
                if "bit.ly" in website:
                    response = requests.get(query.website)
                    redirect_website = response.url
                    for ws in websites:
                        if ws.website in redirect_website:
                            if ws.whatsapp:
                                whatsapp_number = get_phone(redirect_website)
                                if whatsapp_number and len(whatsapp_number) >= 8:
                                    query.phone = whatsapp_number
                                    query.website = None
                                    stop_bitly = True
                            elif ws.qualified == False:
                                query.qualified = False
                                query.website = redirect_website
                                stop_bitly = True
                
                if not stop_bitly:
                    for ws in websites:
                        if website and ws.website in website:
                            if ws.whatsapp:
                                whatsapp_number = get_phone(u_value)
                                if whatsapp_number and len(whatsapp_number) >= 8:
                                    query.phone = whatsapp_number
                                    query.website = None
                            elif ws.qualified == False:
                                query.qualified = False
                            elif ws.linktree:
                                driver.execute_script("window.open('');")
                                driver.switch_to.window(driver.window_handles[1]) 
                                driver.get(website)
                                time.sleep(3)
                                
                                linktree_links = driver.find_elements(By.CSS_SELECTOR, "a")
                                for lt_link in linktree_links:
                                    lt_href = lt_link.get_attribute("href")
                                    
                                    for ws2 in websites:
                                        if lt_href and ws2.website in lt_href:
                                            if ws2.whatsapp:
                                                whatsapp_number = get_phone(u_value)
                                                if whatsapp_number and len(whatsapp_number) >= 8:
                                                    query.phone = whatsapp_number
                                                    query.website = None
                                            elif ws2.qualified == False:
                                                query.qualified = False
                                                query.website = website
                                                        
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                    
        
        posts = driver.find_elements(By.CSS_SELECTOR, "main > div > div > div a")
        if posts:
            for post in posts:
                text_post = post.get_attribute("text")
                if "Pinned" not in text_post:
                    driver.execute_script("arguments[0].click();", post)
                    
                    try:
                        js_last_post_element = driver.find_element(By.CSS_SELECTOR, "a > span > time")
                    except:
                        js_last_post_element = None
                        
                    if js_last_post_element:
                        js_last_post = js_last_post_element.get_attribute("dateTime")
                        last_post = datetime.fromisoformat(js_last_post.replace("Z", "+00:00"))
                        query.last_post = last_post
                        limit_datetime = timezone.now() - timedelta(days=365)
                        if last_post <= limit_datetime:
                            query.qualified = False
                    break
        
        query.save()
    
    driver.close()


@admin.action(description="Handle bitly and linktree urls", permissions=["change"])
def handle_bitly_linktree(modeladmin, request, queryset):
    # options = Options()
    # driver = webdriver.Firefox(options=options)
    websites = models.Website.objects.all()
    
    for query in queryset:
        if query.website:
            response = requests.get(query.website)
            website = response.url
            for ws in websites:
                if ws.website in website:
                    if ws.whatsapp:
                        whatsapp_number = get_phone(website)
                        if whatsapp_number and len(whatsapp_number) >= 8:
                            query.phone = whatsapp_number
                    elif ws.qualified == False:
                        query.website = website
    
    # query.save()
        