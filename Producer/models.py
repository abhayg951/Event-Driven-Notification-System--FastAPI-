from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    email: EmailStr
    name: str

class EventModel(BaseModel):
    event_type: str
    user_email: EmailStr
    message: str
    created_at: Optional[datetime] = datetime.now()

class NotificationModel(BaseModel):
    user_email: EmailStr
    message: str
    sent_at: Optional[datetime] = datetime.now()