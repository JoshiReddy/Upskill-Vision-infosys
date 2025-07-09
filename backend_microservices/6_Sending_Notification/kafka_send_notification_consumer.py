from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import traceback
from flask import Flask, jsonify, request
from config import EMAIL_CONFIG
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration for Kafka Consumer
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'flask-consumer-group',
    'auto.offset.reset': 'earliest',
}

# Create Consumer instance and subscribe
consumer = Consumer(conf)
consumer.subscribe(['send_notification'])

def send_course_update_notification_email(recipient_emails, course_name, start_date, duration):
    try:
        sender_email = EMAIL_CONFIG["email"]
        sender_password = EMAIL_CONFIG["password"]

        # Load the HTML template
        with open("course_update_template.html", "r") as file:
            email_body = file.read()

        # Replace placeholders with actual values
        email_body = email_body.replace("{course_name}", course_name)
        email_body = email_body.replace("{start_date}", start_date)
        email_body = email_body.replace("{duration}", duration + " days")

        # Set up the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = ", ".join(recipient_emails)
        message["Subject"] = f"Course Update: {course_name}"
        message.attach(MIMEText(email_body, "html"))

        # SMTP setup
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        print(f"Course notification sent to {', '.join(recipient_emails)}")

    except (smtplib.SMTPException, FileNotFoundError) as e:
        print(f"SMTP or File error: {e}")
    except Exception as e:
        print("Error sending email:", e)
        traceback.print_exc()
    finally:
        server.quit()

def consume_update_messages():
    try:
        while True:
            msg = consumer.poll(timeout=2.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                else:
                    raise KafkaException(msg.error())
            else:
                try:
                    # Process message
                    message = json.loads(msg.value().decode('utf-8'))
                    print("Received message:", message)
                    send_course_update_notification_email(message['email_list'], message['name'], message['start_date'], message['duration'])
                except json.JSONDecodeError:
                    print("Invalid JSON format in message:", msg.value())
                except Exception as e:
                    print("Error processing message:", e)
                    traceback.print_exc()

    except KeyboardInterrupt:
        print("Consumer interrupted by user.")
    finally:
        consumer.close()

consume_update_messages()
