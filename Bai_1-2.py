import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import sqlite3


url = "https://www.footballtransfers.com/en/leagues-cups/national/uk/premier-league/transfers/2024-2025"
id = 1
driver = webdriver.Chrome()
dc = dict()

for i in range (1,17):


    driver.get(f"{url}/{i}")

    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    table = soup.find("table", class_ = "table table-striped table-hover leaguetable mvp-table transfer-table mb-0")
    # s = "table table-striped table-hover leaguetable mvp-table transfer-table mb-0"
    rows = table.find_all("tr")

    for row in rows:
        name_tag = row.find('td', class_ = "td-player")
        price_tag = row.find('td', class_ = "text-right td-price td-price--no-tag")
        
        if name_tag and price_tag :
            name = name_tag.find('span')
            price = price_tag.find('span')
            dc[name.text.strip()] = price.text.strip()
            

conn = sqlite3.connect('player premier league.db')
cursor = conn.cursor()

cursor.execute('create table Transfer_price (ID Int, Name Text, Price Text)')

for row in cursor.execute('select player from player_stats').fetchall():
    name = row[0]
    if name in dc:
        data = (id,name,dc[name])
        cursor.execute('Insert into Transfer_price values (?,?,?)', data)
    else:
        data = (id,name,'N/a')
        cursor.execute('Insert into Transfer_price values (?,?,?)', data)
    id+=1

conn.commit()
conn.close()

    


    
