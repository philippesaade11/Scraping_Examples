'''
Google Review Extraction

'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

import pandas as pd
import numpy as np
import re
import os
from lxml import html
import time
from datetime import datetime, date, timedelta
import unicodedata
import sys
import json
import random
import re
import requests
import pickle

def time_conversion(check):
#     print check
    unit = check.split()[1]
    if unit == "year" or unit == "years":
        if check.split()[0] == 'a' or check.split()[0] == 'one':
            number_of_years = 1
        else:
            number_of_years = int(check.split()[0])
        minutes_deducted = 365 * 24 * 60 * number_of_years
    if unit == "month" or unit == "months":
        if check.split()[0] == 'a' or check.split()[0] == 'one':
            number_of_months = 1
        else:
            number_of_months = int(check.split()[0])
        minutes_deducted = 30 * 24 * 60 * number_of_months
    if unit == "week" or unit == "weeks":
        if check.split()[0] == 'a' or check.split()[0] == 'one':
            number_of_weeks = 1
        else:
            number_of_weeks = int(check.split()[0])
        minutes_deducted = 7 * 24 * 60 * number_of_weeks
    if unit == "day" or unit == "days":
        if check.split()[0] == 'a' or check.split()[0] == 'one':
            number_of_days = 1
        else:
            number_of_days = int(check.split()[0])
        minutes_deducted = 24 * 60 * number_of_days
    if unit == "hour" or unit == "hours":
        if check.split()[0] == 'an' or check.split()[0] == 'one':
            number_of_hours = 1
        else:
            number_of_hours = int(check.split()[0])
        minutes_deducted =  60 * number_of_hours
    if unit == "minute" or unit == "minutes":
        if check.split()[0] == 'a' or check.split()[0] == 'one':
            number_of_minutes = 1
        else:
            number_of_minutes = int(check.split()[0])
        minutes_deducted = number_of_minutes


    new_time = datetime.now() - timedelta(minutes=minutes_deducted)
    date_new_time=new_time
    new_time = new_time.strftime('%d/%m/%Y')
    #print('actual_time',check)
    #print('converted_time',new_time)
    return new_time,date_new_time

def google_reviews_scraper_less10(browser, total_reviews, overall_rating):
    '''
    Scrape all the reviews of 1 URL
    '''
    temp_df = pd.DataFrame(columns=['Author','Total_Reviews_by_Author','Rating','Date','Content','Content_org','Response_from_owner','Response_from_owner_org', 'Total_Reviews'])
    k = 0
    overall_rating = overall_rating.replace(',','.')

    num_reviews = len(browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata]"))
    for j in range(1, num_reviews+1):
        try:
            
            review_author = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[1]/div[1]/a")[0].get_attribute("innerText")
            review_author = '' if review_author is None else review_author
            review_author = ''.join("*" if i % 2 == 0 else char for i, char in enumerate(review_author, 1))

            try:
                review_author_reviews = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[1]/div[2]/a/span")[0].get_attribute("innerText")
                review_author_reviews = review_author_reviews.encode('ascii', 'ignore').decode('utf-8')
                if (len(str(review_author_reviews).split(" "))  > 0) and ('review' in str(review_author_reviews)):
                    review_author_reviews = int(re.findall(r'\d+',str(review_author_reviews))[0])
                else:
                    review_author_reviews = 0
            except Exception as e:
                review_author_reviews = 0

            review_rating = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[1]/g-review-stars/span")[0].get_attribute('aria-label')
            review_rating = review_rating.encode('ascii', 'ignore').decode('ascii')
            if (len(str(review_rating).split(" ")) > 0):    
                review_rating = str(review_rating).split(" ")[1]
            else:
                review_rating = 0

            review_date = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[1]/span[1]")[0].get_attribute("innerText")

            try:
                try:                                                           
                    review_content = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[2]/span/span[2]")[0].get_attribute("innerText")
                    assert(review_content is not None)
                except Exception as e:
                    review_content = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[2]/span")[0].get_attribute("innerText")
                    if review_content is None:
                        review_content = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[2]")[0].get_attribute("innerText")

                assert(review_content is not None)
                review_content = review_content.replace('\n', ' ')
            except Exception as e:
                review_content = ""

            try:
                try:                                                           
                    review_response_from_user = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[3]/div[2]/span[2]")[0].get_attribute("innerText")
                    assert(review_response_from_user is not None)
                except Exception as e:
                    try:
                        review_response_from_user = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[3]/div[2]")[0].get_attribute("innerText")
                        if review_response_from_user is None:
                            review_response_from_user = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[3]")[0].get_attribute("innerText")
                        assert(review_response_from_user is not None)
                    except Exception as e:
                        try:                                                           
                            review_response_from_user = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[2]/div[2]/span[2]")[0].get_attribute("innerText")
                            assert(review_response_from_user is not None)
                        except Exception as e:
                            review_response_from_user = browser.find_elements_by_xpath("//div[@id='reviewSort']/div/div[2]/div[@jsdata][" + str(j) + "]/div[2]/div[2]")[0].get_attribute("innerText")

                assert(review_response_from_user is not None)
                review_response_from_user = review_response_from_user.replace('\n', ' ')
            except Exception as e:
                review_response_from_user = ""

            review_response_from_user = review_response_from_user.replace('\n', ' ')
            if review_response_from_user.find("Response from the owner") != -1:
                review_response_from_user = re.split(r'Response from the \b\w+ \b\w+ \b\w+ ', review_response_from_user)[1]
                
            review_date_new_format, date_review_date_new_format = time_conversion(review_date)
            date_fil=datetime.now()-date_review_date_new_format
            
            review_content_org=''        
            if("(Translated by Google)" in review_content and "(Original)" in review_content):
                review_content = re.sub(r"\(\bTranslated by Google\b\)","", review_content)
                t_review_content = review_content.split("(Original)")
                review_content = t_review_content[0].strip()
                review_content_org = t_review_content[1].strip()
            else:
                review_content_org = review_content
                
            review_response_from_user_org=''        
            if("(Translated by Google)" in review_response_from_user and "(Original)" in review_response_from_user):
                review_response_from_user = re.sub(r"\(\bTranslated by Google\b\)","", review_response_from_user)
                t_review_response_from_user = review_response_from_user.split("(Original)")
                review_response_from_user = t_review_response_from_user[0].strip()
                review_response_from_user_org = t_review_response_from_user[1].strip()
            else:
                review_response_from_user_org=review_response_from_user

            temp_df.loc[k,'Author'] = review_author
            temp_df.loc[k,'Total_Reviews_by_Author'] = review_author_reviews
            temp_df.loc[k,'Rating'] = review_rating.replace(',','.')
            temp_df.loc[k,'Date'] = review_date_new_format
            temp_df.loc[k,'Content'] = review_content
            temp_df.loc[k,'Content_org']=review_content_org
            temp_df.loc[k,'Response_from_owner'] = review_response_from_user
            temp_df.loc[k,'Response_from_owner_org'] = review_response_from_user_org
            temp_df.loc[k,'date_dif']=date_fil.days
            temp_df.loc[k,'Total Reviews'] = total_reviews
            
            k += 1
        except Exception as e:
            print(e, flush=True)
            print('inside Exception', flush=True)
            if (k >= (int(total_reviews)-1)):
                temp_df['Average_Rating'] = overall_rating
                return temp_df
            continue

    if len(temp_df) > 0:
        temp_df['Average_Rating'] = overall_rating
    return temp_df

def google_reviews_scraper(data_url, cookies, total_reviews, overall_rating):
    '''
    Scrape all the reviews of 1 URL
    '''
    print(data_url)
    temp_df = pd.DataFrame(columns=['Author','Total_Reviews_by_Author','Rating','Date','Content','Content_org','Response_from_owner','Response_from_owner_org', 'Total_Reviews'])
    k = 0
    overall_rating = overall_rating.replace(',','.')

    for i in range(0, total_reviews, 10):
        time.sleep(10/total_reviews)
        for trial in range(3):
            try:
                ua = UserAgent()
                userAgent = ua.random

                data_url = re.sub("start_index:([0-9]*)?", "start_index:"+str(i), data_url)
                data_url = re.sub("next_page_token:([0-9]*)?", "next_page_token:"+str(i), data_url)
                data_url = "?hl=en&".join(data_url.split("?"))

                session = requests.Session()
                for cookie in cookies:
                    session.cookies.set(cookie['name'], cookie['value'])

                response = session.get(data_url, headers={'User-Agent': userAgent})

                text = unicodedata.normalize("NFKD", response.text)
                text = text.replace("\r", " ")
                start = list(re.compile("(<([A-Za-z][A-Za-z0-9]*)\\b[^>]*>)").finditer(text))[0].start()
                end = list(re.compile("(</([A-Za-z][A-Za-z0-9]*)\\b[^>]*>)").finditer(text))[-1].end()

                tree = html.fromstring(text[start:end])

                #Extract Reviews
                for j in range(1, len(tree.xpath("//div[@jsdata]"))+1):
                    review_author = tree.xpath('//div[@jsdata][' + str(j) + ']/div[1]/div[1]/a')[0].text_content()
                    review_author = '' if review_author is None else review_author
                    review_author =''.join("*" if i % 2 == 0 else char for i, char in enumerate(review_author, 1))

                    try:
                        review_author_reviews = tree.xpath("//div[@jsdata][" + str(j) + "]/div[1]/div[2]/a/span")[0].text_content()
                        review_author_reviews = review_author_reviews.encode('ascii', 'ignore').decode('utf-8')
                        if (len(str(review_author_reviews).split(" "))  > 0) and ('review' in str(review_author_reviews)):
                            review_author_reviews = int(re.findall(r'\d+',str(review_author_reviews))[0])
                        else:
                            review_author_reviews = 0
                    except Exception as e:
                        review_author_reviews = 0

                    review_rating = tree.xpath("//div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[1]/g-review-stars/span")[0].attrib['aria-label']
                    review_rating = review_rating.encode('ascii', 'ignore').decode('ascii')
                    if (len(str(review_rating).split(" ")) > 0):    
                        review_rating = str(review_rating).split(" ")[1]
                    else:
                        review_rating = 0

                    review_date = tree.xpath("//div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[1]/span[1]")[0].text_content()

                    try:
                        try:                                                           
                            review_content = tree.xpath("//div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[2]/span/span[2]")[0].text_content()
                            assert(review_content is not None)
                        except Exception as e:
                            review_content = tree.xpath("//div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[2]/span")[0].text_content()
                            if review_content is None:
                                review_content = tree.xpath("//div[@jsdata][" + str(j) + "]/div[1]/div[3]/div[2]")[0].text_content()

                        assert(review_content is not None)
                        review_content = review_content.replace('\n', ' ')
                    except Exception as e:
                        review_content = ""

                    try:
                        try:                                                           
                            review_response_from_user = tree.xpath("//div[@jsdata][" + str(j) + "]/div[3]/div[2]/span[2]")[0].text_content()
                            assert(review_response_from_user is not None)
                        except Exception as e:
                            try:
                                review_response_from_user = tree.xpath("//div[@jsdata][" + str(j) + "]/div[3]/div[2]")[0].text_content()
                                if review_response_from_user is None:
                                    review_response_from_user = tree.xpath("//div[@jsdata][" + str(j) + "]/div[3]")[0].text_content()
                                assert(review_response_from_user is not None)
                            except Exception as e:
                                try:                                                           
                                    review_response_from_user = tree.xpath("//div[@jsdata][" + str(j) + "]/div[2]/div[2]/span[2]")[0].text_content()
                                    assert(review_response_from_user is not None)
                                except Exception as e:
                                    review_response_from_user = tree.xpath("//div[@jsdata][" + str(j) + "]/div[2]/div[2]")[0].text_content()

                        assert(review_response_from_user is not None)
                        review_response_from_user = review_response_from_user.replace('\n', ' ')
                    except Exception as e:
                        review_response_from_user = ""

                    review_response_from_user = review_response_from_user.replace('\n', ' ')
                    if review_response_from_user.find("Response from the owner") != -1:
                        review_response_from_user = re.split(r'Response from the \b\w+ \b\w+ \b\w+ ', review_response_from_user)[1]
                        
                    review_date_new_format, date_review_date_new_format = time_conversion(review_date)
                    date_fil=datetime.now()-date_review_date_new_format
                    
                    review_content_org=''        
                    if("(Translated by Google)" in review_content and "(Original)" in review_content):
                        review_content = re.sub(r"\(\bTranslated by Google\b\)","", review_content)
                        t_review_content = review_content.split("(Original)")
                        review_content = t_review_content[0].strip()
                        review_content_org = t_review_content[1].strip()
                    else:
                        review_content_org = review_content
                        
                    review_response_from_user_org=''        
                    if("(Translated by Google)" in review_response_from_user and "(Original)" in review_response_from_user):
                        review_response_from_user = re.sub(r"\(\bTranslated by Google\b\)","", review_response_from_user)
                        t_review_response_from_user = review_response_from_user.split("(Original)")
                        review_response_from_user = t_review_response_from_user[0].strip()
                        review_response_from_user_org = t_review_response_from_user[1].strip()
                    else:
                        review_response_from_user_org=review_response_from_user

                    temp_df.loc[k,'Author'] = review_author
                    temp_df.loc[k,'Total_Reviews_by_Author'] = review_author_reviews
                    temp_df.loc[k,'Rating'] = review_rating.replace(',','.')
                    temp_df.loc[k,'Date'] = review_date_new_format
                    temp_df.loc[k,'Content'] = review_content
                    temp_df.loc[k,'Content_org']=review_content_org
                    temp_df.loc[k,'Response_from_owner'] = review_response_from_user
                    temp_df.loc[k,'Response_from_owner_org'] = review_response_from_user_org
                    temp_df.loc[k,'date_dif']=date_fil.days
                    temp_df.loc[k,'Total Reviews'] = total_reviews
                    
                    if(k >= (int(total_reviews)-1)):
                        temp_df['Average_Rating'] = overall_rating
                        return temp_df
                    k += 1
                break
            except Exception as e:
                if trial >= 2:
                    print(e, flush=True)
                    print('inside Exception', flush=True)

                    if (k >= (int(total_reviews)-1)):
                        temp_df['Average_Rating'] = overall_rating
                        return temp_df
                    continue

    if len(temp_df) > 0:
        temp_df['Average_Rating'] = overall_rating
    return temp_df

def get_driver():
    try:
        if random.randint(0, 3) == 0:
            print("Login to Google", flush=True)
            google_login()
    except Exception as e:
        print("Error Loginging in", flush=True)
        print(e, flush=True)
        
    try:
        ua = UserAgent()
        userAgent = ua.random
    except:
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"

    options = Options()
    options.add_argument('--lang=en-ca')
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("enable-automation")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-cache")
    options.add_argument("--aggressive-cache-discard")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-offline-load-stale-cache")
    options.add_argument("--incognito")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-impl-side-painting")
    options.add_argument("--disable-gpu-sandbox")
    options.add_argument("--disable-accelerated-2d-canvas")
    options.add_argument("start-maximized")
    options.add_argument(f'user-agent={userAgent}')
    options.add_experimental_option("detach", True)

    if(sys.platform.startswith('win')):
        browser = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)
    else:
        browser = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options=options)
    
    browser.delete_all_cookies()
    if os.path.exists("cookies.pickle"):
        browser.get("https://google.com")
        cookies = pickle.load(open("cookies.pickle", "rb"))
        for cookie in cookies:
            browser.add_cookie(cookie)
        print("Added Google Cookies", flush=True)
    return browser
     
def google_login():
    try:
        ua = UserAgent()
        userAgent = ua.random
    except:
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"

    options = Options()
    options.add_argument('--lang=en-ca')
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("enable-automation")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-cache")
    options.add_argument("--aggressive-cache-discard")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-offline-load-stale-cache")
    options.add_argument("--incognito")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-impl-side-painting")
    options.add_argument("--disable-gpu-sandbox")
    options.add_argument("--disable-accelerated-2d-canvas")
    options.add_argument("start-maximized")
    options.add_argument(f'user-agent={userAgent}')
    options.add_experimental_option("detach", True)

    if(sys.platform.startswith('win')):
        browser = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)
    else:
        browser = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options=options)
    
    browser.delete_all_cookies()
    browser.get("https://accounts.google.com/signin")

    btn = browser.find_element_by_xpath("//input[@type='email']")
    btn.send_keys("email")
    btn.send_keys(Keys.ENTER)
    time.sleep(3)

    btn = browser.find_element_by_xpath("//input[@type='password']")
    btn.send_keys("password")
    btn.send_keys(Keys.ENTER)
    time.sleep(3)

    pickle.dump(browser.get_cookies(), open("cookies.pickle", "wb"))
    try:
        browser.quit()
        browser.close()
    except:
        pass

def scrape_reviews(url):
    try:
        print(url, flush=True)
        browser = get_driver()
        browser.get(url)
        time.sleep(random.randint(2,5))
        browser.maximize_window()

        for trial in range(5):
            try:
                time.sleep(random.randint(4,10))
                browser.find_element_by_xpath("//g-dropdown-button").click()
                browser.find_element_by_xpath("//div[@class='EwsJzb sAKBe']/g-menu/g-menu-item[2]").click()
                print("URL is clean", flush=True)
                time.sleep(random.randint(2,5))
                latest_date_text = browser.find_element_by_xpath('''//*[@id="reviewSort"]/div/div[2]/div[1]/div[1]/div[3]/div[1]/span[1]''').get_attribute("innerText")
                break
            except Exception as e:
                if(browser.page_source.find("recaptcha") > 100):
                    print("Blocked", flush=True)
                    time.sleep(random.randint(3000,6000)) #sleep for almost 1 hour
                if(trial == 1):
                    #fix url:
                    params = {x.split("=")[0]:x.split("=")[1] for x in url.split("?")[1].replace("#", "&").split("&")}
                    newurl = f"https://www.google.com/search?source=hp&ei={params.get('ei', '')}&q={params.get('q', '')}&oq={params.get('oq', '')}&gs_l={params.get('gs_l', '')}#lrd={params.get('lrd', '')}"
                    print(f"Fix URL to {newurl}", flush=True)
                    browser.get(newurl)
                    time.sleep(random.randint(2,5))
                    browser.maximize_window()
                if(trial == 3):
                    print(e, flush=True)
                    browser.find_element_by_xpath("//a[@data-async-trigger='reviewDialog']").click()

        cookies = browser.get_cookies()

        for trial in range(4):
            try:
                total_reviews = browser.find_element_by_xpath('//*[@id="gsr"]/span/g-lightbox/div[2]/div[3]/span/div/div/div/div[1]/div[3]/div[1]/div/span').get_attribute("innerText").split('\n')
                total_reviews = total_reviews[0].split(' ')[0]
                total_reviews = int(re.sub("[^0-9]","",total_reviews))#in case bigger than 100
                
                overall_rating = browser.find_element_by_xpath('//*[@id="gsr"]/span/g-lightbox/div[2]/div[3]/span/div/div/div/div[1]/div[3]/div[1]/span').get_attribute("innerText")
                for scroll in range(2):
                    element_inside_popup = browser.find_element_by_xpath('''//*[@id="reviewSort"]/div[last()]/div[2]/div[1]/a''')
                    element_inside_popup.send_keys(Keys.END)
                    time.sleep(random.randint(2,5))
                break
            except Exception as e:
                if(trial == 2):
                    print(e, flush=True)
                    browser.find_element_by_xpath("//a[@data-async-trigger='reviewDialog']").click()
        
        print("total reviews is ", total_reviews, flush=True)
        if total_reviews <= 10:
            final_output = google_reviews_scraper_less10(browser, total_reviews, overall_rating)
            try:
                browser.quit()
                browser.close()
            except:
                pass
            return (final_output, total_reviews)

        js =  "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; return performance.getEntries() || {};"
        networks = browser.execute_script(js)
        try:
            browser.quit()
            browser.close()
        except:
            pass
        data_url = [x["name"] for x in networks if "/async/reviewSort" in x["name"]][0]
        
        review_date_new_format, date_review_date_new_format = time_conversion(latest_date_text)
        date_fil = datetime.now() - date_review_date_new_format
        
        final_output = google_reviews_scraper(data_url, cookies, total_reviews, overall_rating)
        return (final_output, total_reviews)

    except Exception as e:
        print(e, flush=True)
        try:
            browser.quit()
            browser.close()
        except:
            pass
        
        return (pd.DataFrame(), None)
