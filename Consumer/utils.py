import pika, smtplib, json
from email.mime.text import MIMEText
from connection import get_db_connection, get_connection
from event_logging import log_notification

channel = get_connection().channel()


db_connection = get_db_connection()
notifications_collection = db_connection.get_collection("notifications")

async def send_notification(notification_data, not_id):
    MAX_RETRY_COUNT = 3
    try:
        # Simulate sending notification (e.g., email, SMS)
        # Assume this can raise an exception on failure
        await send_email_notification(notification_data["user_email"], notification_data["message"])

        # Update notification status to 'sent'
        
        await notifications_collection.update_one(
            {"_id": not_id},
            {"$set": {"status": "sent"}}
        )
        log_notification(notification_data, "sent")
    except Exception as e:
        # Update notification status to "failed"
        current_retries = notification_data.get("retries", 0)
        if current_retries < MAX_RETRY_COUNT:
            await notifications_collection.update_one(
                {"_id": not_id},
                {"$set": {"status": "failed", "retries": current_retries + 1}}
            )
            log_notification(notification_data, "failed")
            updated_notification = await notifications_collection.find_one({"_id": not_id})

            # re-publish the message for retry
            publish_event_to_rabbitmq(updated_notification)
        else:
            # Log the failure and mark as permanently failed
            await notifications_collection.update_one(
                {"_id": not_id},
                {"$set": {"status": "permanently_failed"}}
            )
            log_notification(notification_data, "permanently failed")

        print(f"Failed to send notification: {e}")

async def send_email_notification(email: str, message: str):
    '''this function will send the notification through email'''
    sender_email = "<sender_email>"
    sender_password = "<password>"

    msg = MIMEText(message)
    msg["Subject"] = "Notification"
    msg["From"] = sender_email
    msg["To"] = email

    # SMTP server setup for Gmail
    with smtplib.SMTP_SSL("smtp.gmail.com") as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())

def publish_event_to_rabbitmq(notification_data: dict):
    """this function is called only when mail server face a failure"""
    try:
        # Declare the exchange to ensure it's present
        channel.exchange_declare(exchange="notification_exchange", exchange_type='direct')

        # Publish the message to the exchange with the appropriate routing key

        body = json.dumps(notification_data, sort_keys=True, default=str)
        channel.basic_publish(
            exchange='notification_exchange',
            routing_key='email_notification',
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        get_connection().close()
    except Exception as e:
        print(f"Error published message to RabbitMQ: {e}")