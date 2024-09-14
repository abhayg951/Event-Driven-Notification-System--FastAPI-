import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)

def log_notification(event_data, status):
    logging.info(f" Notification {status}: {event_data}")