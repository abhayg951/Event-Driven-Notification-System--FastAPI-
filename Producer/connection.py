import pika
from motor.motor_asyncio import AsyncIOMotorClient
import os

def get_rabbit_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    return connection

def get_db_connection():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client.get_database("ED_Notification_System")
    return db