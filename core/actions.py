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
from prospect.utils import (get_phone, has_string_in_list, is_telephone, is_cellphone, open_tab, close_tab, selenium_click, try_white, save_cookies, load_cookies)
from . import models
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from prospect import regex
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

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
            email = re.search(regex.EMAIL_PATTERN, body)
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

@admin.action(description="Open Selenium", permissions=["change"])
def open_selenium(modeladmin, request, queryset):
    options = Options()
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(652, 768 - 20)   
    driver.set_window_position(0, 0)
 
@admin.action(description="Get data from the Instagram page", permissions=["change"])
def get_instagram_data(modeladmin, request, queryset):
    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.instagram.com/")
    
    time.sleep(5)
    
    try:
        form = driver.find_element(By.ID, "loginForm")
        username = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        
        username.send_keys(settings.INSTAGRAM_USERNAME)
        password.send_keys(settings.INSTAGRAM_PASSWORD)
        form.submit()
    except:
        try:
            form = driver.find_element(By.ID, "login_form")
            username = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
            password = driver.find_element(By.CSS_SELECTOR, "input[name='pass']")
            
            username.send_keys(settings.INSTAGRAM_USERNAME)
            password.send_keys(settings.INSTAGRAM_PASSWORD)
            form.submit()
        except:
            pass
            
    open_tab(driver, "https://web.whatsapp.com/", 1)
    input("Press enter to continue ")
    close_tab(driver, 0)
            
    for index, query in enumerate(queryset):
        print("=============================")
        print(f"{index + 1} of {len(queryset)} - id: {query.id}")
        driver.get(query.get_instagram_link())
            
        time.sleep(10)
        
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            if body:
                body_html = body.get_attribute("innerHTML")
                if "Sorry, this page isn't available." in body_html:
                    query.qualified = False
                    query.save()
                    print("disqualified from page not available")
                    continue
        except:
            pass
    
        # name
        title = driver.find_element(By.TAG_NAME, "title")
        if title:
            title = title.get_attribute("innerText")
            
            if "@" in title:
                name = re.search(r"(.*?)\s?\(@", title)
                if name:
                    query.name = name.group(1)
                    
        disqualified_websites = models.Website.objects.filter(qualified=False)
        
        role_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
        if role_buttons and len(role_buttons) > 0:
            
            # open "more" button from bio
            for role_button in role_buttons:
                outer_text = role_button.get_attribute("outerText")
                if not outer_text: continue
                if "more" in outer_text:
                    role_button.click()
                    break
                
            # check for not qualified websites in the bio
            for role_button in role_buttons:
                try:
                    # more button does not exist -> StaleElementReferenceException
                    outer_text = role_button.get_attribute("outerText")
                except:
                    continue
                if not outer_text: continue
                else: outer_text = outer_text.lower()
                
                is_qualified = None
                
                for ws in disqualified_websites:
                    if outer_text and ws.website in outer_text:
                        if ws.qualified == False:
                            is_qualified = False
                            query.website = ws.website
                            query.qualified = False
                            print("disqualified from bio")
                            break
                
                if is_qualified == False:
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
                    if is_cellphone(phone_number):
                        if len(phone_number) == 11:
                            phone_number = f"55{phone_number}"
                        query.cellphone = phone_number
                    elif is_telephone(phone_number):
                        query.telephone = phone_number
                    break
        
        highlights = driver.find_elements(By.CSS_SELECTOR, "section ul > li [role='button']")
        if highlights and len(highlights) > 0:
            for highlight in highlights:
                outer_text = highlight.get_attribute("outerText")
                
                if not outer_text: continue
                else: outer_text = outer_text.lower()
                
                is_qualified = None
                
                for ws in disqualified_websites:
                    if outer_text and ws.website in outer_text:
                        if ws.qualified == False:
                            is_qualified = False
                            query.qualified = False
                            print("disqualified from highlight")
                            break
                
                if is_qualified == False:
                    break
                
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
                    time.sleep(0.5)
                    break
        
        # website
        websites = models.Website.objects.all()
        links_to_redirect = driver.find_elements(By.CSS_SELECTOR, "a[href*='l.instagram.com']")
        
        if links_to_redirect and len(links_to_redirect) > 0:
            for link in links_to_redirect:
                href = urllib.parse.urlparse(link.get_attribute("href"))
                query_params = urllib.parse.parse_qs(href.query)
                u_param = query_params.get('u', [None])[0]
                website = ""
                if "&fbclid" in u_param: website = u_param.split("&fbclid")[0]
                elif "?fbclid" in u_param: website = u_param.split("?fbclid")[0]
                
                is_whatsapp = False
                is_linktree = False
                is_qualified = None
                is_unknown = True
                
                for ws in websites.filter(bitly=True, linktree=False):
                    if ws.website in website:
                        print("website before:", website)
                        response = requests.get(website)
                        redirect_website = response.url
                        website = redirect_website
                        print("website after:", website)
                        break
                
                for ws in websites:
                    if website and ws.website in website:
                        if ws.whatsapp:
                            is_whatsapp = True
                        elif ws.qualified == False:
                            is_qualified = False
                        elif ws.linktree:
                            is_linktree = True
                        is_unknown = False
                        break
                   
                if is_unknown: 
                    query.website = website
                elif is_whatsapp:
                    phone_number = get_phone(website)
                    if phone_number:
                        if is_cellphone(phone_number):
                            if len(phone_number) == 11:
                                phone_number = f"55{phone_number}"
                            query.cellphone = phone_number
                            print("is_whatsapp website:", query.cellphone)
                        elif is_telephone(phone_number):
                            query.telephone = phone_number
                elif is_qualified == False:
                    query.website = website
                    query.qualified = False
                    print("disqualified from website bio")
                    break
                elif is_linktree:
                    query.website2 = website
                    open_tab(driver=driver, search=website, index_tab=1, sleep=3)
                    
                    try:
                        linktree_links = driver.find_elements(By.CSS_SELECTOR, "a")
                        for lt_link in linktree_links:
                            lt_href = lt_link.get_attribute("href")
                            
                            is_whatsapp2 = False
                            is_linktree2 = False
                            is_qualified2 = None
                            is_bitly2 = False
                            is_unknown2 = True
                            
                            for ws2 in websites:
                                if lt_href and ws2.website in lt_href:
                                    if ws2.whatsapp:
                                        is_whatsapp2 = True
                                    elif ws2.qualified == False:
                                        is_qualified2 = False
                                    is_unknown2 = False
                                    break
                            
                            if is_unknown2: 
                                query.website = lt_href
                            elif is_whatsapp2:
                                phone_number = get_phone(lt_href)
                                if phone_number:
                                    if is_cellphone(phone_number):
                                        if len(phone_number) == 11:
                                            phone_number = f"55{phone_number}"
                                        query.cellphone = phone_number
                                    elif is_telephone(phone_number):
                                        query.telephone = phone_number
                            elif is_qualified2 == False:
                                query.website = lt_href
                                query.qualified = False
                                print("disqualified from linktree")
                                break
                            elif is_linktree2:
                                query.website2 = lt_href
                            elif is_bitly2:
                                query.website2 = lt_href
                    except Exception as e:
                        print(e)
                        
                    close_tab(driver=driver, index_tab=0)
        
        try:
            posts = driver.find_elements(By.CSS_SELECTOR, "main > div > div > div a")
            if posts and len(posts) > 0:
                for post in posts:
                    text_post = post.get_attribute("text")
                    if "Pinned" not in text_post:
                        selenium_click(driver, post)
                        
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
                                print("disqualified from last post")
                        
                        # close post modal
                        role_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
                        if role_buttons and len(role_buttons) >= 1:
                            for role_button in role_buttons:
                                try:
                                    close_button = role_button.find_element(By.CSS_SELECTOR, "[aria-label='Close']")
                                    if close_button:
                                        close_button.click()
                                        time.sleep(1)
                                        break
                                except:
                                    pass
                        
                        break
                
                if query.qualified == None:
                    selenium_click(driver, posts[0])
                    
                    for index, post in enumerate(posts):
                        if index > 5: break
                        time.sleep(3)
                        
                        try:
                            first_comment = driver.find_element(By.CSS_SELECTOR, "[role='presentation'] ul li h1")
                            try:
                                outer_text = first_comment.get_attribute("outerText")
                            except:
                                outer_text = None
                            
                            if outer_text:
                                outer_text = outer_text.lower()
                                
                                is_qualified = None
                            
                                for ws in disqualified_websites:
                                    if outer_text and ws.website in outer_text:
                                        if ws.qualified == False:
                                            is_qualified = False
                                            query.qualified = False
                                            print("disqualified from first comment")
                                            break
                                
                                if is_qualified == False:
                                    break
                                
                                none_or_nine_cellphone = query.cellphone == None or (type(query.cellphone) == str and len(query.cellphone) == 9)
                                if none_or_nine_cellphone:
                                    phone_number = get_phone(outer_text)
                                    if phone_number and is_cellphone(phone_number):
                                            if len(phone_number) == 11:
                                                phone_number = f"55{phone_number}"
                                            query.cellphone = phone_number
                        except:
                            pass
                        
                        try:
                            buttons = driver.find_elements(By.CSS_SELECTOR, "button")
                            for button in buttons:
                                try:
                                    next_button = button.find_element(By.CSS_SELECTOR, "[aria-label='Next']")
                                    if next_button:
                                        button.click()
                                        break
                                except:
                                    pass
                        except:
                            pass
        except Exception as e:
            print(e)
        
        # check whatsapp web
        if not query.qualified == False and query.cellphone and len(query.cellphone) in (11, 13):
            open_tab(driver=driver, search=query.get_whatsapp_link(add_message=False), index_tab=1)
            
            def check_whatsapp():
                result = False
                
                try:
                    role_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
                    if role_buttons and len(role_buttons) >= 1:
                        # open "Profile details" sidebar
                        for role_button in role_buttons:
                            title_attr = role_button.get_attribute("title")
                            terms = ("Profile details", "Dados de perfil")
                            if any(item in title_attr for item in terms):
                                driver.execute_script("arguments[0].click();", role_button)
                                time.sleep(2)
                                break
                except Exception as e:
                    print(e)
                    
                try:
                    title_contacts = driver.find_elements(By.CSS_SELECTOR, "h1")
                    if title_contacts and len(title_contacts) >= 1:
                        # check with open "Contact info"
                        for role_button in title_contacts:
                            title_attr = role_button.get_attribute("innerText")
                            terms = ("Contact info", "Dados do contato")
                            if any(item in title_attr for item in terms):
                                result = True
                except Exception as e:
                    print(e)
                try:
                    whatsapp_links = driver.find_elements(By.CSS_SELECTOR, "a")
                    if whatsapp_links and len(whatsapp_links) >= 1:
                        for whatsapp_link in whatsapp_links:
                            link = whatsapp_link.get_attribute("href")
                            
                            is_linktree = False
                            is_qualified = None
                            is_bitly = False
                            is_unknown = True
                            
                            if "http" in link:
                                for ws in websites:
                                    if link and ws.website in link:
                                        if ws.qualified == False:
                                            is_qualified = False
                                        elif ws.linktree:
                                            is_linktree = True
                                        elif ws.bitly:
                                            is_bitly = True
                                        is_unknown = False
                                        break
                                
                                if is_unknown: 
                                    query.website = link
                                elif is_qualified == False:
                                    query.website = link
                                    query.qualified = False
                                    print("disqualified from WhatsApp")
                                    break
                                elif is_linktree:
                                    query.website2 = link
                                elif is_bitly:
                                    query.website2 = link
                                    
                            elif "mailto" in link:
                                query.email = link.replace("mailto:", "")
                except Exception as e:
                    print(e)
                    
                return result
            
            try_white(
                callback=check_whatsapp, 
                times=3,
                sleep_initial=15,
                sleep_after=10
            )
            
            close_tab(driver=driver, index_tab=0)
        
        query.save()
        print("=============================")

        len_chunck = 30
        chunk = (index + 1) % len_chunck == 0
        not_last = index + 1 != len(queryset)
        if chunk and not_last: time.sleep(60)
        
    driver.close()

@admin.action(description="Get data from the LinkedIn profile", permissions=["change"])
def get_linkedin_data(modeladmin, request, queryset):
    options = Options()
    firefox_profile = FirefoxProfile()
    # firefox_profile.set_preference('permissions.default.stylesheet', 2)
    # firefox_profile.set_preference('permissions.default.image', 2)
    # options.profile = firefox_profile
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(652, 768 - 20)
    driver.set_window_position(0, 0)
    
    driver.get("https://www.linkedin.com/login")
    
    time.sleep(5)
    
    form = driver.find_element(By.CLASS_NAME, "login__form")
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    
    if settings.LINKEDIN_USERNAME and settings.LINKEDIN_PASSWORD:
        if username and password and form:
            username.send_keys(settings.LINKEDIN_USERNAME)
            password.send_keys(settings.LINKEDIN_PASSWORD)
            form.submit()
            time.sleep(3)
        else:
            print(form, username, password)
            return
    else:
        print("Missing LinkedIn credentials")
        return
    
    for index_query, query in enumerate(queryset):
        driver.get(f"https://www.linkedin.com/in/{query.username}/details/experience/")
        time.sleep(3)
        print("=" * 30)
        print(f"query {index_query+1}")
        
        try:
            xpath = "//ul/li/div/section/h2/span"
            not_experiences = driver.find_element(By.XPATH, xpath)
            if not_experiences: 
                print(f"No experiences to {query.username}")
                query.archived = True
                query.save()
                continue
        except:
            pass
        
        xpath = "//main/section/div/div/div/ul/li"
        experiences = driver.find_elements(By.XPATH, xpath)
        if experiences:
            for index_experience, experience in enumerate(experiences):
                print("-" * 30)
                
                experience_title_element = None
                try:
                    selector = "div > div > div:nth-of-type(2) > div > div > div span:nth-of-type(1)"
                    experience_title_element = experience.find_element(By.CSS_SELECTOR, selector)
                except:
                    try:
                        selector = "div > div > div:nth-of-type(2) > div > a > div > div > div > div > span:nth-of-type(1)"
                        experience_title_element = experience.find_element(By.CSS_SELECTOR, selector)
                    except:
                        print("Experience title not found")
                
                if experience_title_element:
                    experience_title = experience_title_element.get_attribute("innerText")
                    print(f"experience({index_experience+1}):", experience_title)
                    
                    black_list = ("freelance", "suporte", "estágio", "estagiári", "aprendiz", "monitor", "atendente", "auxiliar", "soldado", "assistente", "operador", "vendedor", "studant", "design", "técnico", "php", "java")
                    
                    if not any(item in experience_title.lower() for item in black_list):
                        try:
                            selector = "div > div > div:nth-of-type(1) a[href*='company']"
                            company_link_element = experience.find_element(By.CSS_SELECTOR, selector)
                            company_link = company_link_element.get_attribute("href")
                            
                            
                            continue_script = input("Show company? [y/n]: ")
                            if continue_script.lower() == "y":
                                # open company page
                                driver.execute_script("window.open('');")
                                driver.switch_to.window(driver.window_handles[1]) 
                                driver.get(f"{company_link}about")
                                time.sleep(3)
                                
                                input("Press to continue")
                                
                                company = models.Company()
                                
                                company_title = driver.find_element(By.TAG_NAME, "h1")
                                # username = company_link.split("/")[3]
                                if company_title: company.name = company_title.get_attribute("outerText")
                                if company_link:
                                    if "/about/" in driver.current_url:
                                        company.linkedin = driver.current_url.replace("/about/", "/")
                                    else:
                                        company.linkedin = driver.current_url
                                
                                selector = "section > dl > dd > a"
                                company_website_element = driver.find_element(By.CSS_SELECTOR, selector)
                                company_website = company_website_element.get_attribute("href")
                                
                                if company_website: company.website = company_website
                                
                                # find email by website
                                try:
                                    driver.get(company_website)
                                    time.sleep(2)
                                except Exception as e:
                                    print(e)
                                    continue
                                
                                body = driver.find_element(By.TAG_NAME, "body")
                                email = re.search(regex.EMAIL_PATTERN, body.get_attribute("innerHTML"))
                                
                                if email:
                                    company.email = email.group()
                                else:
                                    terms_list = ["contato", "contact", "fale"]
                                    terms = []
                                    for term in terms_list:
                                        terms.append(f"contains(@href, '{term}')")
                                        
                                    try:
                                        xpath = f"//a[{' or '.join(terms)}]"
                                        contact_page_link = driver.find_element(By.XPATH, xpath)
                                        contact_page_link = contact_page_link.get_attribute("href")
                                        if contact_page_link:
                                            driver.get(contact_page_link)
                                            time.sleep(2)
                                            body = driver.find_element(By.TAG_NAME, "body")
                                            email = re.search(regex.EMAIL_PATTERN, body.get_attribute("innerHTML"))
                                        
                                            if email:
                                                query.email = email.group()
                                            else:
                                                print("email not found")
                                        else:
                                            print("email not found")
                                    except Exception as e:
                                        print(e)
                                        
                                company.employer = query
                                
                                print("company.name:", company.name)
                                print("company.linkedin:", company.linkedin)
                                print("company.website:", company.website)
                                print("company.email:", company.email)
                                
                                save_and_next = input("Save company? [y/n] ")
                                
                                if save_and_next.lower() == "y":
                                    try:
                                        company.save()
                                    except Exception as e:
                                        print(e)
                                    
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                        except Exception as e:
                            has_tabs = len(driver.window_handles) > 1
                            
                            if has_tabs and driver.window_handles[1]:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                                
                            print("Company link not found")
        
        query.archived = True
        query.save()
    driver.close()                

@admin.action(description="Get e-mail from the company link", permissions=["change"])
def get_email_from_link(modeladmin, request, queryset):
    options = Options()
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(652, 768 - 20)
    driver.set_window_position(0, 0)
    
    for query in queryset:
        if query.website:
            try:
                driver.get(query.website)
            except Exception as e:
                print(e)
                continue
            time.sleep(2)

            body = driver.find_element(By.TAG_NAME, "body")
            email = re.search(regex.EMAIL_PATTERN, body.get_attribute("innerHTML"))
            
            if email:
                query.email = email.group()
            else:
                terms_list = ["contato", "contact", "fale"]
                terms = []
                for term in terms_list:
                    terms.append(f"contains(@href, '{term}')")
                try:
                    xpath = f"//a[{' or '.join(terms)}]"
                    contact_page_link = driver.find_element(By.XPATH, xpath)
                    contact_page_link = contact_page_link.get_attribute("href")
                    if contact_page_link:
                        driver.get(contact_page_link)
                        time.sleep(2)
                        body = driver.find_element(By.TAG_NAME, "body")
                        email = re.search(regex.EMAIL_PATTERN, body.get_attribute("innerHTML"))
                    
                        if email:
                            query.email = email.group()
                        else:
                            print("email not found")
                    else:
                        print("email not found")
                except Exception as e:
                    print(e)
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

@admin.action(description="Set the qualily of Instagram contact", permissions=["change"])
def set_contact_quality(modeladmin, request, queryset):
    options = Options()
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.instagram.com/")
    time.sleep(3)
    
    form = None
    username = None
    password = None
    
    try:
        form = driver.find_element(By.CSS_SELECTOR, "#loginForm")
        username = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    except Exception as e:
        print("Default login form not found.")
    
    if form == None:
        try:
            form = driver.find_element(By.CSS_SELECTOR, "#login_form")
            username = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
            password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        except Exception as e:
            print("Meta login form not found.")
        
    if form == None: return
    
    if settings.INSTAGRAM_USERNAME and settings.INSTAGRAM_PASSWORD:
        if username and password and form:
            username.send_keys(settings.INSTAGRAM_USERNAME)
            password.send_keys(settings.INSTAGRAM_PASSWORD)
            form.submit()
            time.sleep(10)
        else:
            print(form, username, password)
            return
    else:
        print("Missing Instagram credentials")
        return
    
    for index, query in enumerate(queryset):
        print("=================================")
        driver.switch_to.window(driver.window_handles[0])
        driver.get(query.get_instagram_link())
        time.sleep(3)
        
        print(f"{index + 1} of {len(queryset)}")
        print("name:", query.name)
        print("username:", query.username)
        print("last post:", query.last_post.strftime("%b. %d, %Y"))
        print("cellphone:", query.fcellphone())
        print("telephone:", query.ftelephone())
        print("website:", query.website)
        
        if query.cellphone == None or (query.cellphone != None and len(query.cellphone) == 9):
            set_phone_number = input("Do you want to set a new cellphone number? [y/n] ")
            if set_phone_number.lower() == "y":
                new_number = get_phone(input("Enter the number: "))
                if is_cellphone(new_number):
                    if len(whatsapp_number) == 11:
                        whatsapp_number = f"55{whatsapp_number}"
                    query.cellphone = new_number
        
        continue_or_disqualify = input("Qualify (y), disqualify/archive (n) or skip (q)? ")
        if continue_or_disqualify.lower() == "q":
            pass
        elif continue_or_disqualify.lower() == "y":
            query.qualified = True
        
            decider_name = input("Name of decider? ")
            if len(decider_name) >= 3:
                decider = models.Decider()
                decider.name = decider_name
                decider.save()
                query.decider = decider
        elif continue_or_disqualify.lower() != "y":
            disqualify_or_archive = input("Disqualify(d) or archive (a)? ")
            if disqualify_or_archive.lower() == "d":
                query.qualified = False
                disqualify_website = input("Disqualified website? [y/n] ")
                if disqualify_website.lower() == "y":
                    query.website = input("Enter disqualified website: ")
            else:
                query.archived = True
            
        query.save()
        print("=================================")
    driver.close()

@admin.action(description="Send WhatsApp message", permissions=["change"])
def send_whatsapp_message(modeladmin, request, queryset):
    options = Options()
    driver = webdriver.Firefox(options=options)
    driver.get("https://web.whatsapp.com/")
    input("Press enter to continue ")
    
    for index, query in enumerate(queryset):
        print(f"{index + 1} of {len(queryset)} - id: {query.id}")
        if query.cellphone == None: continue
        
        driver.get(query.get_whatsapp_link(add_message=True))
        time.sleep(15)
        
        # find send button and send message
        try:
            send_buttons = driver.find_elements(By.CSS_SELECTOR, "footer button")
            for send_button in send_buttons:
                label = send_button.get_attribute("aria-label")
                if label in ("Send", "Enviar"):
                    selenium_click(driver, send_button)
                    break
        except Exception as e:
            print(e)
            
        # time.sleep(20)
        
        # # check if the automatic message has disqualified website
        # disqualified_websites = models.Website.objects.filter(qualified=False)
        # try:
        #     message_links = driver.find_elements(By.CSS_SELECTOR, "#main a")
        #     for message_link in message_links:
        #         href = message_link.get_attribute("href")
        #         for ws in disqualified_websites:
        #             if ws.website in href:
        #                 # archive contact in whatsapp
        #                 # ActionChains(driver) \
        #                 #     .key_down(Keys.CONTROL) \
        #                 #     .key_down(Keys.ALT) \
        #                 #     .key_down(Keys.SHIFT) \
        #                 #     .send_keys('e') \
        #                 #     .key_up(Keys.SHIFT) \
        #                 #     .key_up(Keys.ALT) \
        #                 #     .key_up(Keys.CONTROL) \
        #                 #     .perform()
        #                 query.qualified = False
        # except Exception as e:
        #     print(e)
        
        query.contacted = True
        query.save()
        
        time.sleep(10)
    driver.close()


@admin.action(description="Updaload post", permissions=["change"])
def upload_post(modeladmin, request, queryset):
    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.instagram.com/")
    sleep = 30
    time.sleep(sleep)
    load_cookies(driver, "instagram_cookies")
    
    try:
        form = driver.find_element(By.ID, "loginForm")
        username = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        
        username.send_keys(settings.INSTAGRAM_USERNAME)
        password.send_keys(settings.INSTAGRAM_PASSWORD)
        form.submit()
        
        time.sleep(sleep)
        save_cookies(driver, "instagram_cookies")
    except:
        try:
            form = driver.find_element(By.ID, "login_form")
            username = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
            password = driver.find_element(By.CSS_SELECTOR, "input[name='pass']")
            
            username.send_keys(settings.INSTAGRAM_USERNAME)
            password.send_keys(settings.INSTAGRAM_PASSWORD)
            form.submit()
            
            time.sleep(sleep)
            save_cookies(driver, "instagram_cookies")
        except:
            pass
    
    time.sleep(sleep/2)
    driver.get(f"https://www.instagram.com/{settings.INSTAGRAM_USERNAME}")
    time.sleep(sleep)
    
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        if body:
            body_html = body.get_attribute("innerHTML")
            if "Choose a way to confirm it’s you" in body_html:
                input("Press enter to continue")
    except Exception as e:
        pass
        # print("Confirm it's you:", e)
    
    for index, query in enumerate(queryset):
        try:
            # open new post option
            role_links = driver.find_elements(By.CSS_SELECTOR, "[role='link']")
            if role_links and len(role_links) >= 1:
                for role_link in role_links:
                    try:
                        new_post = role_link.find_element(By.CSS_SELECTOR, "[aria-label='New post']")
                        if new_post:
                            role_link.click()
                            time.sleep(sleep / 2)
                            break
                    except Exception as e:
                        pass
                        # print("post option", e)
            
            # click post open
            role_links = driver.find_elements(By.CSS_SELECTOR, "[role='link']")
            if role_links and len(role_links) >= 1:
                for role_link in role_links:
                    try:
                        post = role_link.find_element(By.CSS_SELECTOR, "[aria-label='Post']")
                        if post:
                            role_link.click()
                            time.sleep(sleep / 2)
                            break
                    except Exception as e:
                        pass
                        # print("post", e)
            
            # set image path to the input file
            try:
                file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                file_input.send_keys(query.image.path)
                time.sleep(2)
            except Exception as e:
                pass
                # print("file_input", e)
            
            # click in the next button
            role_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
            if role_buttons and len(role_buttons) >= 1:
                for role_button in role_buttons:
                    try:
                        innerText = role_button.get_attribute("innerText")
                        if innerText == "Next":
                            role_button.click()
                            time.sleep(sleep / 2)
                            break
                    except Exception as e:
                        pass
                        # print("next button", e)
                        
            # click in the next button again
            role_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
            if role_buttons and len(role_buttons) >= 1:
                for role_button in role_buttons:
                    try:
                        innerText = role_button.get_attribute("innerText")
                        if innerText == "Next":
                            role_button.click()
                            time.sleep(sleep / 2)
                            break
                    except Exception as e:
                        pass
                        # print("next button", e)
                        
            # click in the next button
            try:
                caption = driver.find_element(By.CSS_SELECTOR, "[aria-label='Write a caption...']")
                if caption:
                    try:
                        caption.click()
                        for letter in query.phrase:
                            caption.send_keys(letter)
                            time.sleep(0.2)
                        for letter in [0,1,2,3,4,5]:
                            caption.send_keys("\n")
                            time.sleep(0.2)
                        for letter in query.hashtag.content:
                            caption.send_keys(letter)
                            time.sleep(0.2)
                    except Exception as e:
                        pass
                        # print("next button", e)
            except Exception as e:
                pass
                # print(e)
            input("Press enter to continue")
                
            # click in the share button
            # role_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
            # if role_buttons and len(role_buttons) >= 1:
            #     for role_button in role_buttons:
            #         try:
            #             innerText = role_button.get_attribute("innerText")
            #             if innerText == "Share":
            #                 role_button.click()
            #                 time.sleep(2)
            #                 break
            #         except Exception as e:
            #             pass
            #             # print("next button", e)
            
        except Exception as e:
            pass
            # print(e)
        query.posted = True
        query.save()
        
        if index + 1 != len(queryset): time.sleep(sleep)
        
        
    # bot.logout()
    

@admin.action(description="Testing cookies", permissions=["change"])
def test_cookies(modeladmin, request, queryset):
    options = Options()
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(652, 768 - 20)
    driver.set_window_position(0, 0)
    
    driver.get("https://www.instagram.com/")
    
    time.sleep(10)
    
    load_cookies(driver, "instagram_cookies")
    
    try:
        form = driver.find_element(By.ID, "loginForm")
        username = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        
        username.send_keys(settings.INSTAGRAM_USERNAME)
        password.send_keys(settings.INSTAGRAM_PASSWORD)
        form.submit()
        
        time.sleep(10)
        save_cookies(driver, "instagram_cookies")
    except:
        try:
            form = driver.find_element(By.ID, "login_form")
            username = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
            password = driver.find_element(By.CSS_SELECTOR, "input[name='pass']")
            
            username.send_keys(settings.INSTAGRAM_USERNAME)
            password.send_keys(settings.INSTAGRAM_PASSWORD)
            form.submit()
            
            time.sleep(10)
            save_cookies(driver, "linkedin_cookies")
        except:
            pass
        
    for index, query in enumerate(queryset):
        pass


@admin.action(description="Follow decider", permissions=["change"])
def follow_decider(modeladmin, request, queryset):
    
    for index, query in enumerate(queryset):
        query.followed = True
        query.save()
        
@admin.action(description="Resave", permissions=["change"])
def resave(modeladmin, request, queryset):
    
    for index, query in enumerate(queryset):
        query.save()
        
@admin.action(description="Not posted", permissions=["change"])
def not_posted(modeladmin, request, queryset):
    for query in queryset:
        query.posted = False
        query.save()