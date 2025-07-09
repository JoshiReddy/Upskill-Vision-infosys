from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import sys, os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_connection import get_db_connection

# Configuration for Kafka Consumer
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka server address
    'group.id': 'flask-consumer-group',
    'auto.offset.reset': 'earliest',  # Start from the earliest message
}

consumer = Consumer(conf)
consumer.subscribe(['audit_trail'])

def consume_messages():
    connection = get_db_connection()
    connection.database = "UpSkill_7"

    try:
        cursor = connection.cursor()
        
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                else:
                    raise KafkaException(msg.error())
            else:
                try:
                    # Process the message
                    message = json.loads(msg.value().decode('utf-8'))
                    print("Received message:", message)
                    
                    cursor.execute(
                        """INSERT INTO audit_trail (courseid, email, name, timestamp, action)
                        VALUES (%s, %s, %s, NOW(), %s);""",
                        (message['course_id'], message['email'], message['name'], message['action'])
                    )
                    connection.commit()

                except json.JSONDecodeError:
                    print("Failed to decode JSON message:", msg.value())
                except Exception as e:
                    print("Error while processing message:", e)
                    traceback.print_exc()

    except KeyboardInterrupt:
        print("Consumer interrupted by user.")
    finally:
        # Close resources
        cursor.close()
        connection.close()
        consumer.close()

consume_messages()
