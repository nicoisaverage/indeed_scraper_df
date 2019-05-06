import requests
import bs4
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
from datetime import datetime
from time import time

def extract_job_titles(soup):
    jobs = []
    for div in soup.find_all(name='div', attrs={"class":"row"}):
        for a in div.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
            jobs.append(a["title"])
    return jobs

def extract_companies(soup):
    companies =[]
    for div in soup.find_all(name='div', attrs={"class":"row"}):
        company = div.find_all(name="span", attrs={"class": "company"})
        if len(company) > 0:
            for b in company:
                companies.append(b.text.strip())
        else:
            sec_try = div.find_all(name="span", attrs={"class":"result-link-source"})
            for span in sec_try:
                companies.append(span.text.strip())
    return companies

def extract_locations(soup):
    locations = []
    spans = soup.find_all('div', attrs={'class':'location'})
    for span in spans:
        locations.append(span.text)
    return locations

def extract_salaries(soup):
    salaries = []
    for div in soup.find_all(name="div", attrs={'class':'row'}):
        spans = div.find_all('span', attrs={'class': 'salary no-wrap'})
        if not len(spans) == 0:
            for span in spans:
                salaries.append(span.text.strip())
        else:
            salaries.append('Nothing_found')
    return salaries

def extract_summaries(soup):
    summaries = []
    spans = soup.find_all('div', attrs={'class': 'summary'})
    for span in spans:
        summaries.append(span.text.strip())
    return summaries

def extract_urls(soup):
    urls = []
    for div in soup.find_all(name="div", attrs={'class':'row'}):
        d = div.find_all('div', attrs={'class': 'title'})[0]
        url = "http://indeed.com"+ d.contents[1].attrs['href']
        urls.append(url)
    return urls

def extract_dates(soup):
    dates = []
    urls = extract_urls(soup)
    for url in urls:
        broth = bs(requests.get(url).text, "html.parser")
        for div in broth.find_all('div', attrs={'class': 'jobsearch-JobMetadataFooter'}):
            for x in div.contents:
                if "ago" in x:
                    date = x.replace(" - ", "")
                    dates.append(date)
    return dates

def to_json(titles, companies, locations, salaries, summaries, urls, dates, search_location):
    dicts = []
    for i in range(len(titles)):
        data = {}
        data["title"] = titles[i]
        data["company"] = companies[i]
        try:
            data["location"] = locations[i]
        except:
            data["location"] = search_location
        data["salary"] = salaries[i]
        data["summary"] = summaries[i]
        data["url"] = urls[i]
        data["date"] = dates[i]
        dicts.append(data)
    return dicts

def list_page_soups(num_pages, query, location):
    soups = []
    for i in range(num_pages):
        url = "https://www.indeed.com/jobs?q={0}&l={1}&sort=date&start={2}".format(query.replace(" ", "+"), location.replace(" ", "+"), i*10)
        page = requests.get(url)
        soup = bs(page.text, "html.parser")
        soups.append(soup)
    return soups

def indeed_main(num_pages, query, search_location):
    soups = list_page_soups(num_pages, query, search_location)
    all_jobs = []
    for soup in soups:
        titles = extract_job_titles(soup)
        companies = extract_companies(soup)
        locations = extract_locations(soup)
        salaries = extract_salaries(soup)
        summaries = extract_summaries(soup)
        dates = extract_dates(soup)
#         print(dates)
#         print(len(dates))
        urls = extract_urls(soup)
        print(urls)
        json_data = to_json(titles, companies, locations, salaries, summaries, urls, dates, search_location)
        all_jobs.append(json_data)
    flat_list = [item for sublist in all_jobs for item in sublist]
    main_df = pd.DataFrame(flat_list)
    main_df['source'] = 'Indeed'
    return main_df

if __name__ == "__main__":

    num_pages = 10
    query = "tech"
    location = "Chicago, IL"

    df = indeed_main(num_pages, query, location)

    df.to_csv('indeed_jobs.csv')

# num_pages = '' #num of pages you want 
# query = '' #position you want to search 
# location = '' #location you want to search 

# df = indeed_main(num_pages, query, location)
# r = requests.get('http://indeed.com/pagead/clk?mo=r&ad=-6NYlbfkN0APcB5PE-vv4rq4lRUqBNRHh1T4fx-TP46vPzjjAkJXVvoBD-gi4c-kGVZQzThWHI6n0_w2OMzteHCVYtHEbelLOQdXYkf2euxcg9_CESWNP5oERiR9lpwbVZ_eKkv1MJZMoY0Zqy_U4U_VSM43YQkggwwCXZ5Ht0Rw4wQF9Dwtgs28OAS4l5B87o9A9TAOVIkrsR2hw4Ql6dpyAPTcntnRFrXWmP-60Kk52B4QNxneGv3t_rzDRVbFle5EbjoNgVDT-NmxbdJdFy60XhzbL6KwXYowGaGadKY6KZzzeVKXPyEJAtB0DbU6GSBfijSpVnCu67wUuDzzXzoP2kg-MQPaXRUAozpBtbu0ofxqZXX8S3uipEPkJXAnps1WFC9kth5YJ3kVcybQ77bdzMesMLEa1w38BoajS2IknFy0-ZS26A==&vjs=3&p=1&fvj=1')
# r.url
# df.head(10)
# df.drop_duplicates()
# search terms
# Boo-Yah
