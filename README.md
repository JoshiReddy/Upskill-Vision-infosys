# Upskill-Vision-infosys
Project Setup Guide
Follow the steps below to set up and run the project.

Prerequisites
Before starting, ensure that Java is installed and its path is set in the environment variables.

1. Create .env File
Create a .env file with your own credentials link below in microservices folder.

DB_HOST="localhost"
DB_USER="Db-UserName"
DB_PASSWORD="Db-Password"
DB_NAME="Db-Name"
EMAIL="sample@gmail.com"
EMAIL_PASSWORD="aaaa aaaa aaaa aaaa"
JWT_SECRET_TOKEN="34567890-"
2. Download and Extract Dependencies
Download the following dependencies for Windows and extract them:

Kafka: Download Kafka 3.9.0
Nginx: Download Nginx 1.26.2
3. Configure Nginx
Navigate to the Nginx directory, typically located at C:\nginx\conf\nginx.conf.
Replace the existing nginx.conf file with the one provided in the repository.
4. Set Kafka Path in Environment Variables
Add Kafka's path (e.g., C:\kafka\bin) to your system's environment variables.

5. Start Kafka and Zookeeper
Open two separate terminals and execute the following commands:

Start Zookeeper:

.\bin\windows\zookeeper-server-start.bat config\zookeeper.properties
Start Kafka Server:

.\bin\windows\kafka-server-start.bat config\server.properties
6. Create Kafka Topics
In a terminal, navigate to Kafka's directory and execute the following commands to create the necessary Kafka topics:

bin\windows\kafka-topics.bat --bootstrap-server localhost:9092 --create --topic sending_otp --partitions 1 --replication-factor 1

bin\windows\kafka-topics.bat --bootstrap-server localhost:9092 --create --topic send_notification --partitions 1 --replication-factor 1

bin\windows\kafka-topics.bat --bootstrap-server localhost:9092 --create --topic send_course_notification --partitions 1 --replication-factor 1

bin\windows\kafka-topics.bat --bootstrap-server localhost:9092 --create --topic audit_trail --partitions 1 --replication-factor 1
7. Start Nginx
In a new terminal, navigate to the Nginx directory and run the following command:

nginx.exe
8. Run Backend Services
In separate terminals, navigate to the Backend_Microservices folder and run the following Python services:

authentication_service.py
student_course_service.py
admin_course_service.py
all_users_list_service.py
user_course_progress_service.py
sending_notifications_service.py
audit_trial_service.py
Additionally, run the Kafka consumers in different terminals:

kafka_audit_trail_consumer.py
kafka_send_notification_consumer.py
kafka_send_new_course_notification_consumer.py
kafka_otp_consumer.py
9. Start Frontend (React)
Navigate to the frontend directory and start the React development server.

npm start
Note: Install Dependencies
Make sure to install all necessary dependencies for both the frontend and backend.

# For frontend (React):
npm install

# For backend (Python services):
pip install -r requirements.txt
With these steps, you should be able to set up the project successfully. If you face any issues, please check the logs for any errors and ensure all services are running properly.
