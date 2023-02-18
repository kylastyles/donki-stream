#!/usr/bin/env python3

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import os

'''
Write space weather notifications to Kafka
'''
class KafkaWriter:
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    try:
        producer = KafkaProducer(
                    bootstrap_servers=[KAFKA_BROKER],
                    value_serializer=lambda x: json.dumps(x).encode('utf-8')
                    )
    except NoBrokersAvailable:
        print("ERROR: Kafka service not available; unable to write. Either start kafka service or choose file output.")
        exit()

    def __init__(self, messages):
        count = 0
        
        for msg in messages:
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
