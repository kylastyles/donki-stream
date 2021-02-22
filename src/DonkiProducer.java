package producers;

import org.apache.kafka.clients.producer.*;
//import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.net.http;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

public class DonkiProducer {

    Logger logger = LoggerFactory.getLogger(DonkiProducer.class.getName());

    String apiKey = System.getenv("API_KEY");

    public DonkiProducer(){}

    public static void main(String[] args) { new DonkiProducer().run(); }

    public void run() {
        logger.info("Setup");

        BlockingQueue<String> msgQueue = new LinkedBlockingQueue<String>();   // capacity: 1000);
        // create donki client
        Client client = createDonkiClient(msgQueue);
        // attempts to establish a connection
        client.connect();

        // create a kafka producer
        KafkaProducer<String, String> producer = createKafkaProducer();

        // add a shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("Stopping application...");
            logger.info("Shutting down client from donki...");
            client.stop();
            logger.info("Closing producer...");
            producer.close();
            logger.info("Shutdown complete.");
        }));

        // loop to send msgs to kafka on different threads
        while (!client.isDone()) {
            String msg = null;
            try {
                msg = msgQueue.poll();   // timeout: 5, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                e.printStackTrace();
                client.stop();
            }
            if (msg != null) {
                logger.info(msg);
                producer.send(new ProducerRecord<>() {   // topic: "events_raw", key:null, msg), new Callback() {
                    @Override
                    public void onCompletion(RecordMetadata recordMetadata, Exception e) {
                        if (e != null) {
                            logger.error(e);
                        }
                    }
                });
            }
        }
        logger.info("End of application");
    }

    public Client createDonkiClient(BlockingQueue<String> msgQueue){
        //Hosts donki-hosts = new HttpHosts("https://api.nasa.gov/DONKI/notifications");

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.nasa.gov/DONKI/notifications"))
                .timeout(Duration.ofMinutes(1))
                .header("Content-Type", "application/json")
                .GET()  // "startDate": "2021-01-01", "endDate": "2021-01-30", "api_key": apiKey, "type": "all")
                .build();

    }



    public KafkaProducer<String, String> createKafkaProducer(){
        String bootstrapServers = "127.0.0.1:9092";

        // create Producer properties
        Properties properties = new Properties();
        properties.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        properties.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        properties.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        // create safe Producer
        properties.setProperty(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");
        properties.setProperty(ProducerConfig.ACKS_CONFIG, "all");
        properties.setProperty(ProducerConfig.RETRIES_CONFIG, Integer.toString(Integer.MAX_VALUE));
        properties.setProperty(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, "5"); // kafka 2.0 >= 1.1 so we can keep this as 5. Use 1 otherwise.

        // high throughput producer (at the expense of a bit of latency and CPU usage)
        properties.setProperty(ProducerConfig.COMPRESSION_TYPE_CONFIG, "snappy");
        properties.setProperty(ProducerConfig.LINGER_MS_CONFIG, "20");
        properties.setProperty(ProducerConfig.BATCH_SIZE_CONFIG, Integer.toString(32*1024)); // 32 KB batch size

        // create the producer
        KafkaProducer<String, String> producer = new KafkaProducer<String, String>(properties);
        return producer;
    }
}