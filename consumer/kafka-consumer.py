from kafka import KafkaConsumer
import pandas as pd

consumer = KafkaConsumer(bootstrap_servers=['localhost:29092'])
consumer.subscribe(['rtdata'])

df = pd.DataFrame(columns=['time','variable','value'])
df
for message in consumer:
    
    print(f'Topic: {message.topic}, Value: {message.value.decode("utf-8")}')