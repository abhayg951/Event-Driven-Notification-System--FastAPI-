from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class NotificationModel(BaseModel):
    event_type: str
    user_email: EmailStr
    message: str
    sent_at: Optional[datetime] = datetime.now()