from kafka import KafkaConsumer
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import requests

consumer = KafkaConsumer(bootstrap_servers=['localhost:29092'])
consumer.subscribe(['rtdata'])

df = pd.DataFrame(columns=['timestamp','variable','value','delta','Day sin','Day cos','Week sin','Week cos','Year sin','Year cos'])

day = 24*60*60
week = 7*day
year = (365.2425)*day

for message in consumer:
    if df['timestamp'].size > 60*24*2*2:
        df = df.iloc[2:,:]
    new = pd.DataFrame.from_dict(json.loads(message.value.decode("utf-8")))
    new['timestamp'] = pd.to_datetime(new['timestamp'])
    new['delta'] = new.apply(lambda row: int((row['timestamp'] - datetime.now()).total_seconds()/3600), axis=1)
    seconds = new['timestamp'].map(pd.Timestamp.timestamp)
    new['Day sin'] = np.sin(seconds * (2 * np.pi / day))
    new['Day cos'] = np.cos(seconds * (2 * np.pi / day)) 
    new['Week sin'] = np.sin(seconds * (2 * np.pi / week))
    new['Week cos'] = np.cos(seconds * (2 * np.pi / week))
    new['Year sin'] = np.sin(seconds * (2 * np.pi / year))
    new['Year cos'] = np.cos(seconds * (2 * np.pi / year))
    df = pd.concat([df,new])
    df = df[df['delta']<24]
    load = np.array(df[df['variable']=='load'].groupby(['delta'])['value'].mean())
    temperature = np.array(df[df['variable']=='temperature'].groupby(['delta'])['value'].mean())
    fourier = np.array(df.groupby(['delta']).mean(numeric_only=True).iloc[:,1:])
    
    if (load.shape[0] == 24) and (temperature.shape[0] == 24):
        data_tbs = np.stack([np.c_[load, np.zeros(len(load)), temperature, fourier]])
        params={'data': data_tbs.tolist()}
        response = requests.post("http://127.0.0.1:5000/forecast", json=json.dumps(params))
        print(pd.DataFrame(json.loads(response.content), index=[datetime.now()]))