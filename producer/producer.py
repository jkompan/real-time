import json
import sys
from datetime import datetime, timedelta
from time import sleep
from kafka import KafkaProducer
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# browser
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
browser = webdriver.Chrome(options=options)

def scrape_load():
    browser.get('https://www.pse.pl/dane-systemowe')
    load = browser.find_element(By.ID, 'zapotrzebowanie-mw')
    return {'timestamp':[datetime.now().strftime('%Y-%m-%d %H:%M:%S')], 'variable':['load'], 'value':[float(load.text.replace(" ",""))]}

def scrape_temperature():
    browser.get('https://sggw.meteo.waw.pl/')
    temperature = browser.find_element(By.XPATH, '/html/body/div/div[6]/div[2]/div/strong')
    return {'timestamp':[datetime.now().strftime('%Y-%m-%d %H:%M:%S')], 'variable':['temperature'],'value':[float(temperature.text.replace(',','.'))]}

    
if __name__ == "__main__":
    SERVER = "localhost:29092"

    producer = KafkaProducer(
        bootstrap_servers=[SERVER],
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        api_version=(2, 7, 0),
    )
    
    try:
        start_data = pd.read_csv('start.csv')
        for row in range(23):
            current_load = {'timestamp':[start_data.iloc[2*row,0]],'variable':[start_data.iloc[2*row,1]],'value':[start_data.iloc[2*row,2]/1000]}
            current_temp = {'timestamp':[start_data.iloc[2*row+1,0]],'variable':[start_data.iloc[2*row+1,1]],'value':[start_data.iloc[2*row+1,2]]}
            print(current_load)
            print(current_temp)
            producer.send("rtdata", value=current_load)
            producer.send("rtdata", value=current_temp)
            sleep(1)

        while True:
            current_load = scrape_load()
            print(current_load)
            producer.send("rtdata", value=current_load)
            sleep(15)
            
            current_temp = scrape_temperature()
            print(current_temp)
            producer.send("rtdata", value=current_temp)
            sleep(15)

    except KeyboardInterrupt:
        producer.close()