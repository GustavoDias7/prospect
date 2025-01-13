from django.shortcuts import render
import chardet
from bs4 import BeautifulSoup
import urllib.parse
from . import models

# Create your views here.
def facebook(request):
    context = {}
    
    if request.method == "GET":
        fb_pages = models.Contact.objects.all()
        context["fb_pages"] = fb_pages
        
    if request.method == "POST":
        facebook_pages = request.FILES.get("facebook_pages")
        file = facebook_pages.read()
        soup = BeautifulSoup(file, "html.parser")
        links = soup.find_all("a", attrs={"role": "presentation"})
        
        fb_pages = []
        for link in links:
            href = urllib.parse.urlparse(link.get("href"))
            path_query = f'{href.path}?{href.query}' if href.query else href.path
            fb_page = models.Contact(path_query=path_query)
            fb_pages.append(fb_page)
            
        # try:
        models.Contact.objects.bulk_create(fb_pages)
        # except:
        #     print()
        
        fb_pages = models.Contact.objects.all()
        context["fb_pages"] = fb_pages
        
    return render(request, "pages/facebook.html", context)