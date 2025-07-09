from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, jsonify, request
from config import EMAIL_CONFIG
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration for Kafka Consumer
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka server address
    'group.id': 'flask-consumer-group',
    'auto.offset.reset': 'earliest',  # Start from the earliest message
}

# Create Consumer instance
consumer = Consumer(conf)

# Subscribe to Kafka topic
consumer.subscribe(['send_course_notification'])

def send_course_notification_email(recipient_emails, course_name, start_date, duration):
    try:
        sender_email = EMAIL_CONFIG["email"]
        sender_password = EMAIL_CONFIG["password"]

        # Load the HTML templates
        with open("course_notification_template.html", "r") as file:
            email_body = file.read()

        # Replace placeholders with actual values
        email_body = email_body.replace("{course_name}", course_name)
        email_body = email_body.replace("{start_date}", start_date)
        email_body = email_body.replace("{duration}", duration +" days")

        # Set up the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = ", ".join(recipient_emails)  # Join the list of emails into a comma-separated string
        message["Subject"] = f"New Course Available: {course_name}"
        message.attach(MIMEText(email_body, "html"))

        # Set up the SMTP server (Gmail SMTP server)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Establish a secure TLS connection
        server.login(sender_email, sender_password)

        # Send the email
        server.send_message(message)
        server.quit()

        print(f"Course notification sent to {', '.join(recipient_emails)}")
        return True
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")
    return False



def consume_course_messages():
    try:
        while True:
            # Poll for messages
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                else:
                    print(f"Kafka error: {msg.error()}")
            else:
                # Process the message
                try:
                    message = json.loads(msg.value().decode('utf-8'))
                    print(message)
                    success = send_course_notification_email(
                        message['email_list'], 
                        message['name'], 
                        message['start_date'], 
                        message['duration']
                    )
                    if success:
                        print(f"Successfully processed message: {message}")
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error processing message: {e}")
    except KeyboardInterrupt:
        print("Shutting down consumer...")
    finally:
        consumer.close()
        print("Kafka consumer connection closed.")



consume_course_messages()
