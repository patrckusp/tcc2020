import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from datetime import date
from calendar import monthrange
from urllib.parse import unquote

page = 1
cidade = ''
if(len(sys.argv) > 1):
    regiao = sys.argv[1]
if(len(sys.argv) > 2):
    estado = sys.argv[2]
if(len(sys.argv) > 3):
    cidade = sys.argv[3]
if(len(sys.argv) > 4):
    page = int(sys.argv[4])
    
links = {}
# links['centro-oeste'] = {'df': 'distrito-federal', 'go': 'goias', 'mt': 'mato-grosso', 'ms': 'mato-grosso-do-sul'}
# links['nordeste'] = {'al' : 'alagoas', 'ba': 'bahia', 'ce': 'ceara', 'ma' : 'maranhao', 'pb' : 'paraiba', 'pe' : 'pernambuco', 'pi' : 'piaui', 'rn' : 'rio-grande-do-norte', 'se' : 'sergipe'} # {'pe' : 'caruaru-regiao', 'petrolina-regiao'}
# links['norte'] = {'ac' : 'acre', 'ap' : 'amapa', 'am' : 'amazonas', 'pa' : 'para', 'ro' : 'rondonia', 'rr' : 'roraima', 'to' : 'tocantins'} # {'pa' : 'santarem-regiao'}
# links['sudeste'] = {'es' : 'espirito-santo', 'mg' : 'minas-gerais', 'rj' : 'rio-de-janeiro', 'sp' : 'sao-paulo'} # {'mg' : 'centro-oeste', 'mg' : 'grande-minas', 'mg' : 'sul-de-minas', 'mg' : 'triangulo-mineiro', 'mg' : 'vales-mg', 'mg' : 'zona-da-mata'} {'rj' : 'norte-fluminense', 'rj' : 'regiao-dos-lagos', 'rj' : 'regiao-serrana', 'rj' : 'sul-do-rio-costa-verde'} {'sp' : 'bauru-marilia', 'sp' : 'campinas-regiao', 'sp' : 'itapetininga-regiao', 'sp' : 'mogi-das-cruzes-suzano', 'sp' : 'piracicaba-regiao', 'sp' : 'presidente-prudente-regiao', 'sp' : 'ribeirao-preto-franca', 'sp' : 'sao-jose-do-rio-preto-aracatuba', 'sp' : 'santos-regiao', 'sp' : 'sao-carlos-regiao', 'sp' : 'sorocaba-jundiai', 'sp' : 'vale-do-paraiba-regiao'}
# links['sul'] = {'pr' : 'parana', 'rs' : 'rio-grande-do-sul', 'sc' : 'santa-catarina'} # {'pr' : 'campos-gerais-sul', 'pr' : 'norte-noroeste', 'pr' : 'oeste-sudoeste'}
if(cidade != ''):
    links[regiao] = {estado : cidade}
else:
    links['sudeste'] = {'sp' : 'sao-paulo'}

chrome_options = Options()  
chrome_prefs = {}
chrome_options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
chrome_options.add_argument("--headless")

chrome_articles_list = webdriver.Chrome(chrome_options=chrome_options)
chrome_article = webdriver.Chrome(chrome_options=chrome_options)

for regiao in links:
    if(not os.path.isdir(regiao)):
        os.mkdir(regiao)
    for estado in links[regiao]:
        path = regiao + '/' + estado
        if(not os.path.isdir(path)):
            os.mkdir(path)

        date_end = date.today()
        count = 0
        try:
            with open(path + '/checkpoint.txt', 'r') as text_file:
                checkpoint = text_file.readline()
                print(checkpoint.rstrip('\n'))
                if(checkpoint != ''):
                    date_end = datetime.strptime(checkpoint.rstrip('\n'), "%Y-%m-%d").date()
                    page = int(text_file.readline().rstrip('\n'))
                    count = int(text_file.readline().rstrip('\n'))
        except FileNotFoundError:
            open(path + '/checkpoint.txt', 'x')

        print(date_end)
        print(page)
        print(count)
        print("\n")
        stop = False
        while(date_end.year!='2013' and date_end.month!='1'):
            date_begin = date(date_end.year, date_end.month, 1)
            if(stop):
                page = 1
                stop = False

            while(not stop):
                begin = date_begin.strftime("%Y-%m-%d")
                end = date_end.strftime("%Y-%m-%d")
                print("Begin: " + begin)
                print("End: " + end)
                print("Page: " + str(page))
                print('https://g1.globo.com/busca/?q=' + links[regiao][estado] + '+' + estado + '&page=' + str(page) + '&order=recent&from=' + begin + 'T00%3A00%3A00-0300&to=' + end + 'T23%3A59%3A59-0300' + "\n")
                chrome_articles_list.get('https://g1.globo.com/busca/?q=' + links[regiao][estado] + '+' + estado + '&page=' + str(page) + '&order=recent&from=' + begin + 'T00%3A00%3A00-0300&to=' + end + 'T23%3A59%3A59-0300')

                try:
                    chrome_articles_list.find_element_by_css_selector('.pagination.widget') #last page in search
                except NoSuchElementException:
                    stop = True

                articles_list = chrome_articles_list.find_elements_by_css_selector('.widget--info__text-container')

                for article_item in articles_list:
                    with open(path + '/checkpoint.txt', 'w') as text_file:
                            text_file.write(end + "\n")
                            text_file.write(str(page) + "\n")
                            text_file.write(str(count) + "\n")
                            
                    article = {} #json with article infos

                    try:
                        header = article_item.find_element_by_css_selector('.widget--info__header')
                    except NoSuchElementException:
                        continue

                    if(header.text == 'G1'):
                        anchor = article_item.find_element_by_css_selector('a')
                        href = anchor.get_attribute('href')
                        anchor_decoded = unquote(href)
                        url_begin = anchor_decoded.find('&u=http') + 3
                        if(url_begin > 3):
                            url_end = anchor_decoded.find('&syn=')
                            if(url_end > 0):
                                href = anchor_decoded[url_begin:url_end]

                        print(href)
                        if(href.find('/noticia/')<0):
                            continue

                        if(href.find('/'+ links[regiao][estado] +'/')<0 and href.find('/'+ estado +'/')<0):
                            continue

                        try:
                            chrome_article.get(href)
                        except (TimeoutException):
                            print("Timeout\n")
                            continue

                        article['url'] = chrome_article.current_url
                        # if(article['url'].find('/noticia/')<0):
                        #     continue

                        # if(article['url'].find('/'+ links[regiao][estado] +'/')<0 and article['url'].find('/'+ estado +'/')<0):
                        #     continue

                        try:
                            title_head = chrome_article.find_element_by_class_name('content-head__title')
                        except NoSuchElementException:
                            continue

                        article['title'] = chrome_article.find_element_by_class_name('content-head__title').text
                        article['subtitle'] = chrome_article.find_element_by_class_name('content-head__subtitle').text

                        article['publication_date'] = chrome_article.find_element_by_css_selector('time[itemprop="datePublished"]').get_attribute('datetime')
                        article['updated_at'] = chrome_article.find_element_by_css_selector('time[itemprop="dateModified"]').get_attribute('datetime')

                        content_parts = chrome_article.find_elements_by_css_selector('p.content-text__container')
                        content = ''
                        for content_part in content_parts:
                            if not content_part.text:
                                content_next = content_part.find_element_by_xpath('following-sibling::*')
                                if(content_next.get_attribute('class')=='content-unordered-list'):
                                    u_list = content_next.find_elements_by_tag_name('li')
                                    for list_item in u_list:
                                        content += list_item.text + "\n"
                            else:
                                content += content_part.text + "\n"
                        article['content'] = content
                        print(article['url'] + "\n")
                        print(path + '/' + str(count) + '.json')
                        article_file_name = "{}/{}.json".format(path,count)

                        with open(article_file_name, 'w') as outfile:
                            json.dump(article, outfile, indent=4)

                        count+=1
                page+=1
            if(date_end.month == 1):
                date_end = date(date_end.year-1, 12, monthrange(date_end.year - 1, 12)[1])
            else:
                date_end = date(date_end.year, date_end.month - 1, monthrange(date_end.year, date_end.month - 1)[1])
chrome_article.close()
chrome_articles_list.close()