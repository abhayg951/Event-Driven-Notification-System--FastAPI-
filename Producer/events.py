import json
import pika
from .connection import get_rabbit_connection
import time

RATE_LIMIT = 10 # notifications per seconds
last_sent_time = time.time()

def rate_limit():
    global last_sent_time
    time_since_last_time = time.time() - last_sent_time
    if time_since_last_time < 1 / RATE_LIMIT:
        # time.sleep((1 / RATE_LIMIT) - time_since_last_time)
        time.sleep(10)
    last_sent_time = time.time()

channel = get_rabbit_connection().channel()
def publish_event(event_type: str, message: dict):
    '''This will send the email notification to the consumer'''

    rate_limit()

    # Declare the exchange
    channel.exchange_declare(exchange='notification_exchange', exchange_type='direct')

    # Declare queue
    channel.queue_declare(queue="notification_queue")

    channel.queue_bind(queue="notification_queue", exchange="notification_exchange", routing_key="email_notification")

    # Bind the queue to the exchange (but don't declare the queue in the sender, just send to the exchange)

    event_message = json.dumps(message, sort_keys=True, default=str)

    # publishing message to the exchange the routing key
    channel.basic_publish(exchange="notification_exchange", routing_key=event_type, body=event_message)
    
    get_rabbit_connection().close()