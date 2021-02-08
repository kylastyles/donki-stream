# donki-stream

A streaming sandbox for space weather events from NASA.

## Notable Links

About KSQLDB:
https://ksqldb.io/examples.html

About DONKI:
https://ccmc.gsfc.nasa.gov/support/DONKI-webservices.php

Actual Url to ping:
https://api.nasa.gov/DONKI/notifications?startDate=2014-05-01&endDate=2014-05-08&type=all&api_key=DEMO_KEY

About Running Kafka with Spring Boot JAVA:
https://github.com/igorkosandyak/spring-boot-kafka


## Kafka Commands
docker exec -it broke sh
usr/bin/kafka-topics --bootstrap-server localhost:9092 --list
usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic events_raw --from-beginning

## KSQLDB
docker exec -it ksqldb-serve sh
usr/bin/ksql
show topics;

TODO: Create Streams. Split events_raw topic into streams per messageType (Report, RBE, etc..)
