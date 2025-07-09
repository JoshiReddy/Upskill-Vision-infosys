from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG

# Kafka Configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'flask-consumer-group',
    'auto.offset.reset': 'earliest',
}

consumer = Consumer(conf)
consumer.subscribe(['sending_otp'])


def send_otp_email(recipient_email, otp):
    try:
        sender_email = EMAIL_CONFIG["email"]
        sender_password = EMAIL_CONFIG["password"]

        # Set up the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = "Your OTP Code"
        body = f"Your OTP code is: {otp}. It is valid for 5 minutes."
        message.attach(MIMEText(body, "plain"))

        # SMTP setup
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)

        print(f"OTP sent to {recipient_email}")
        return "Sent Successfully"
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        return "SMTP Error Occurred"
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return "Some Error Occurred"


def consume_messages():
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                else:
                    print(f"Kafka error: {msg.error()}")
            else:
                try:
                    message = json.loads(msg.value().decode('utf-8'))
                    print(f"Received message: {message}")
                    send_otp_email(message['email'], message['otp'])
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Message processing error: {e}")
    except KeyboardInterrupt:
        print("Shutting down consumer...")
    finally:
        consumer.close()
        print("Consumer connection closed.")


consume_messages()
