# donki-stream

A streaming sandbox for space weather events from NASA. A recent change to this project is that it now accepts command line arguments for dates, 
and will write to either json file or kafka-- default is json file. This change will help to accommodate 
future Machine Learning efforts with the data. 

### How to Run

Use the docker-compose file to stand up services if needed: `docker-compose up`.

Run DONKI-stream with `python3 DONKI-stream/main.py` to write 30 days before today's date to file.

Or use `python3 DONKI-stream/main.py -d 2022-01-31 -o kafka` to write Jan 2-31, 2022 to kafka.

Why 30 days? Because that is the maximum limit allowed by the DONKI API in one pull. 

### Notable Links

About DONKI:
https://ccmc.gsfc.nasa.gov/support/DONKI-webservices.php

Actual Url to ping:
https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/notifications?startDate=2014-05-01&endDate=2014-05-08&type=all


### Kafka Commands

docker exec -it broke sh
usr/bin/kafka-topics --bootstrap-server localhost:9092 --list
usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic events_raw --from-beginning

### KSQLDB Commands

About KSQLDB: https://ksqldb.io/examples.html

docker exec -it ksqldb-serve sh
usr/bin/ksql
show topics;

