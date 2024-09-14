from fastapi import APIRouter, HTTPException, status
from .models import UserModel, EventModel
from .collections import users_collection, events_collection
from .events import publish_event

router = APIRouter(
    prefix="/users"
)

@router.post('/')
async def create_user(user: UserModel):
    user_exists = await users_collection.find_one({"email": user.email})

    if user_exists:
        raise HTTPException(detail="user already exists", status_code=status.HTTP_400_BAD_REQUEST)
    
    new_user = await users_collection.insert_one(user.model_dump())
    event = EventModel(event_type = "email_notification", user_email=user.email, message="Thank you signing")

    await events_collection.insert_one(event.dict())
    publish_event("email_notification", event.model_dump())
    return {
        "message": "User created successfully",
        "user_id": str(new_user.inserted_id)
    }

@router.get("/{email}")
async def get_user(email: str):
    user = await users_collection.find_one({"email": email})
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

# async def log_event(event: EventModel):
#     await events_collection.insert_one(event.dict())