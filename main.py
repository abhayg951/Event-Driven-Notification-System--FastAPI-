from fastapi import FastAPI, status, Body
from typing import Annotated, Optional
import motor.motor_asyncio
import os
from pydantic.functional_validators import BeforeValidator
from pydantic import BaseModel, ConfigDict, Field, EmailStr

from pymongo import ReturnDocument

app = FastAPI()

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["DB_URL"])
db = client.get_database("ED_Notification_System")
user_collection = db.get_collection("Users")

@app.get("/")
def home():
    return {
        "message": "Welcome to Event-Driven Notification System"
    }

# Represents an ObjectID field in the database
# It will be represented as a 'str' on the model so that it can be serialized to JSON

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserModel(BaseModel):
    """
    Container for a single user record
    """

    # The primary key for the UserModel, stored as a 'str' on the instance.
    # This will be aliased to '_id' when sent to MongoDB
    #  but provided as 'id' in the API request and responses

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    email: EmailStr = Field(...)
    password : str = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
    )

@app.post(
    "/user/",
    response_description="Add new user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=True
)
async def create_user(user: UserModel = Body(...)):
    """
    Insert a new User

    a unique `id` will be created and provide in the response
    """

    new_user = await user_collection.insert_one(
        user.model_dump(by_alias=True, exclude=["id"])
    )

    created_user = await user_collection.find_one(
        {"_id": new_user.inserted_id}
    )

    return created_user