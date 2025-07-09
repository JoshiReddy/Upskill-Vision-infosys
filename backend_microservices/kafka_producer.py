from confluent_kafka import Producer
import json

# Configuration for Kafka Producer
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka server address
    'client.id': 'flask-producer',
}

# Callback function to handle delivery reports
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Create Producer instance
producer = Producer(conf)

# Function to produce messages to Kafka
def produce_message(topic, message):
    # Convert message to JSON string
    message = json.dumps(message)
    # Send message to Kafka topic
    producer.produce(topic, message.encode('utf-8'), callback=delivery_report)
    producer.flush()

