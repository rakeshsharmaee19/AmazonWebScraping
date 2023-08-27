import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By

def mediaMart():
    op = webdriver.ChromeOptions()
    op.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"+"AppleWebKit/537.36 (KHTML, like Gecko)"
    +"Chrome/87.0.4280.141 Safari/537.36")
    # op.add_experimental_option("detach", True)

    url = "https://www.mediamarkt.es/es/product/_secadora-aeg-t7dbg841-bomba-de-calor-8-kg-a-blanco-1455590.html"

    browser = webdriver.Chrome('drivers/chromedriver.exe', chrome_options=op)
    browser.get(url)
    browser.maximize_window()

    browser.find_element(by=By.XPATH, value='//*[@id="pwa-consent-layer-accept-all-button"]').click()

    soup = BeautifulSoup(browser.page_source, "html.parser")
    review ={}
    review['title'] = soup.find('h1', {'class': 'sc-1jga2g7-0 euMfmk sc-1jga2g7-1 huobCt sc-rkspnd-1 lafhVL'}).text
    review['price'] = soup.find('div', {'class': 'sc-1vld6r2-1 PQAAE sc-1r6586o-5 bIJnnS'}).text
    temp_dict = {}
    nextPagePointer = soup.find('button', {"class":"sc-140xkaw-1 etwLZa"}).text
    while nextPagePointer == "Página siguiente ›":
        userName = soup.findAll('div', {"class":"sc-1b4w28x-4 bMLqrS sc-v1lln3-0 jmjMWn"})
        for user in userName:
            temp_dict['heading']= user.find('p',{"class":"sc-1jga2g7-0 euMfmk sc-1jga2g7-1 cBnkuG"}).text
            temp_dict['review']= user.find('p',{"class":"sc-1jga2g7-0 euMfmk sc-1jga2g7-1 kasTav"}).text
            review[user.find('span',{"class":'sc-1jga2g7-0 euMfmk sc-1jga2g7-1 bxERgx sc-bkca2b-10 hHywUM'}).text] = temp_dict
        try:
            nextPagePointer = soup.find('button', {"class":"sc-140xkaw-1 etwLZa"}).text
        except:
            nextPagePointer = ""
        if nextPagePointer:
            clickVal = browser.find_element(By.XPATH, value='//*[@class="sc-140xkaw-1 etwLZa"]')
            try:
                clickVal.click()
            except:
                nextPagePointer = ''
            soup = BeautifulSoup(browser.page_source, "html.parser")

    df = pd.DataFrame(review)
    df.to_csv(r'mediaMartReviews.csv')
    

def amazon():
    HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/90.0.4430.212 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

    def getdata(url):  # function for getting page data
        r = requests.get(url, headers=HEADERS)
        return r.text

    def html_code(url):  # Function for getting html data
        # pass the url
        # into getdata function
        htmldata = getdata(url)
        soup = BeautifulSoup(htmldata, 'html.parser')

        # display html code
        return soup

    def cus_data(soup):
        result = {}
        result['title'] = soup.find('span', {'id': 'productTitle'}).text
        result['price'] = soup.find('span', {'class': 'a-offscreen'}).text.replace(',','.')
        view_all_link = soup.find("a", {"data-hook": "see-all-reviews-link-foot"})
        actual_url = "https://www.amazon.it/" + view_all_link['href']
        while actual_url is not None:
            temp_dict = {}
            required_content = html_code(actual_url)
            try:
                temp = required_content.find('li', {'class': 'a-last'})
            except:
                temp = None

            for i in required_content.find_all('div', {'data-hook': 'review'}):
                try:
                    temp_dict['heading'] = i.find('a', {'data-hook': 'review-title'}).find('span').text
                except:
                    temp_dict['heading'] = i.find('span', {'data-hook': 'review-title'}).find('span').text
                temp_dict['review'] = i.find('span', {'data-hook': 'review-body'}).find('span').text
                result[i.find('span', {'class': 'a-profile-name'}).text] = temp_dict

            if temp is not None:
                try:
                    actual_url = "https://www.amazon.it/" + temp.find('a')['href']
                except:
                    actual_url = None
            else:
                break
        return result

    url = "https://www.amazon.it/Electrolux-EP81UB25UG-Aspirapolvere-Portatile-accessori/dp/B09C62DKN2/?th=1"

    soup = html_code(url)
    op = cus_data(soup)
    df = pd.DataFrame(op)
    df.to_csv(r'amazonReviews.csv')

mediaMart()
amazon()

