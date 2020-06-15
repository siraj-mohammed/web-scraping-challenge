from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import time

#URLs to scrape
nasa_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
mars_weather_url = "https://twitter.com/marswxreport?lang=en"
mars_facts_url = "https://space-facts.com/mars/"
usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
mars_data = {}

def browser_init():
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    return browser


def scrape_nasa_news(browser):
    browser.visit(nasa_url)
    time.sleep(2)
    html = browser.html
    soup = bs(html, 'lxml')
    # Grab the second title
    news_title = soup.find_all('div', class_="content_title")[1].text
    # Grab the article text
    news_p = soup.find('div', class_='article_teaser_body').text
    return (news_title, news_p)


def scrape_jpl_image(browser):
    browser.visit(jpl_url)
    browser.click_link_by_id('full_image')
    time.sleep(2)
    html = browser.html
    soup = bs(html, 'lxml')
    featured_image = soup.find('img', class_='fancybox-image').get('src')
    featured_image_url = 'https://jpl.nasa.gov'+featured_image
    return featured_image_url


def scrape_mars_weather(browser):
    browser.visit(mars_weather_url)
    time.sleep(2)
    html = browser.html
    soup = bs(html, 'lxml')
    weather_tweets = soup.find_all('div', class_='css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0')
    current_weather = weather_tweets[1].find('span', class_='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0').text
    return current_weather


def scrape_mars_facts():
    mars_tables = pd.read_html(mars_facts_url)
    mars_facts = mars_tables[0].to_html(header=False, index=False)
    return mars_facts


def scrape_mars_hemispheres(browser):
    browser.visit(usgs_url)
    time.sleep(2)
    html = browser.html
    soup = bs(html, 'lxml')

    hemisphere_image_urls = []
    urls = []

    #Visit main page and grab URLs for each hemisphere 
    hemispheres = soup.find_all('div', class_='description')
    for hemisphere in hemispheres:
        urls.append("https://astrogeology.usgs.gov"+hemisphere.a['href'])

    #Visit pages for each hemisphere and grab title and full image URL
    for url in urls:
        browser.visit(url)
        time.sleep(2)
        html_ = browser.html
        soup_ = bs(html_, 'lxml')
        title = soup_.find('h2', class_='title').text
        img_url = soup_.find('div', class_='downloads').ul.li.a['href']
        hemisphere_image_urls.append({'title': title, 'img_url': img_url})
    return hemisphere_image_urls
    

def scrape():
    browser = browser_init()
    news_title, news_p = scrape_nasa_news(browser)
    mars_data['news_title'] = news_title
    mars_data['news_p'] = news_p
    mars_data['featured_image_url'] = scrape_jpl_image(browser)
    mars_data['current_weather'] = scrape_mars_weather(browser)
    mars_data['mars_facts'] = scrape_mars_facts()
    mars_data['hemisphere_image_urls'] = scrape_mars_hemispheres(browser)
    browser.quit()
    return mars_data

