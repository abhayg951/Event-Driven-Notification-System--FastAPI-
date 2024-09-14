import pika, os, sys
import json
from utils import send_notification
from connection import get_connection, get_db_connection
from models import NotificationModel
from bson import ObjectId

import asyncio



db_connection = get_db_connection()
notifications_collection = db_connection.get_collection("notifications")

channel = get_connection().channel()

def callback(ch, method, properties, body):
    print(f" [x] Received {body}")
    event_data = json.loads(body)

    # Assume event_data contains use email and message
    loop = asyncio.get_event_loop()
    not_id = loop.run_until_complete(log_notification(event_data))

    if event_data['event_type'] == "email_notification":
        # await send_email_notification(event_data["user_email"], event_data["message"])
        # loop.run_until_complete(send_notification(event_data, not_id))
        print("-----------------------------------------------")

def start_consumer():
    
    # Declare the exchange and bind it to the queue
    channel.exchange_declare(exchange="notification_exchange", exchange_type='direct')

    channel.queue_declare(queue="notification_queue")
    
    channel.queue_bind(queue="notification_queue", exchange="notification_exchange", routing_key="email_notification")

    # set the callback function to consume messages
    channel.basic_consume(queue="notification_queue", on_message_callback=callback, auto_ack=True)

    print('  [x] Waiting for messages....')
    channel.start_consuming()

async def log_notification(body: dict):

    if "_id" in body.keys():
        return ObjectId(body["_id"])
    
    event_data = NotificationModel(user_email=body["user_email"], message=body["message"], event_type=body["event_type"])
    inserted_notification = await notifications_collection.insert_one(event_data.model_dump())

    note_id = await notifications_collection.find_one({"_id": inserted_notification.inserted_id})
    return note_id["_id"]

if __name__ == '__main__':
    try:
        start_consumer()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)