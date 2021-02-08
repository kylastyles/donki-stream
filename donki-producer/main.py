#!/usr/bin/env python3

from kafka import KafkaProducer
import json
import os
import requests
from contextlib import suppress

from message_parser import DONKI_message_parser

'''
Pull space weather notifications from NASA API and write to Kafka
'''

# --- SETUP ---

API_KEY = os.getenv('API_KEY', 'DEMO_KEY')
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')

producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )

dates_list = [("2020-01-01", "2020-01-31"),
              ("2020-02-01", "2020-02-29"),
              ("2020-03-01", "2020-03-31"),
              ("2020-04-01", "2020-04-28"),
              ("2020-05-01", "2020-05-31"),
              ("2020-06-01", "2020-06-30"),
              ("2020-07-01", "2020-07-31"),
              ("2020-08-01", "2020-08-31"),
              ("2020-09-01", "2020-09-30"),
              ("2020-10-01", "2020-10-31"),
              ("2020-11-01", "2020-11-30"),
              ("2020-12-01", "2020-12-31"),
              ("2021-01-01", "2021-01-31")
    ]

# --- API PULL ---

print(f"Attempting to pull {dates_list} events from API")

data = []

for dates in dates_list:
    headers = {"Content-Type": "application/json"}
    payload = {
        "startDate": dates[0][0],
        "endDate": dates[0][1],
        "api_key": API_KEY,
        "type": "all"
    }
    try:
        r = requests.get(url="https://api.nasa.gov/DONKI/notifications", params=payload, headers=headers)
        data.extend(json.loads(r.content))  # type(r.content) => bytes
    except Exception as e:
        print(f"ERROR: Request Get - {e}")


# --- KAFKA PUSH ---

print(f"Attempting to load {len(data)} messages...")

count = 0

for msg in data:
    with suppress(ValueError):
        # try to clean up message before send to kafka
        msg = DONKI_message_parser(msg)
    try:
        producer.send(topic='donki_events', value=msg)
        count += 1
    except Exception as e:
        try:
            producer.send(topic='errors', value=e)
        except Exception as e2:
            print(f"ERROR: Failed to Produce - {e2}")

producer.flush()

if count > 0:
    print(f"SUCCESS: Loaded {count} messages to Kafka")
else:
    print("FAILED: No messages loaded to Kafka")

