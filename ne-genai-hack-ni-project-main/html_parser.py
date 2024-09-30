"""Scrape metadata attributes from a requested URL."""
import requests
from bs4 import BeautifulSoup
import pprint
import urllib


def scrape_page(url):
    if urllib.parse.urlparse(url).scheme != "":
        html = {}
        """Scrape target URL for metadata."""
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
        r = requests.get(url, headers=headers)
        html = BeautifulSoup(r.content, 'html.parser')
        
    else :
        html = BeautifulSoup(open(url), "html.parser")

    return html

def get_images(html):
    images =  html.find_all("img")
    images_no_alt_text = []
    for image in images :
        if image["alt"] == "":
            images_no_alt_text.append(image)
    return images_no_alt_text

def update_alt_text(html,image_src, text):
    image=html.find("img", {"src" : image_src})
    image["alt"] = text
    return html

def output_html(html, file_name):
    with open(file_name, "w", encoding = 'utf-8') as file:
        file.write(str(html.prettify()))

if __name__ == '__main__':

    html = scrape_page("/Users/sirajama/repos/external/beautifulsoup-tutorial/index.html")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(html)
    images =  html.find_all("img")
    for image in images :
        print ("Source Location is :{}".format(image["src"]))
        html = update_alt_text(html, image["src"],"Sample text for test")
    pp.pprint(html)
    output_html(html,"output.html")