from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict

from flask import app
from models.notificationsModal import Notification, NotificationCollection
from pydantic import Field, ValidationError, BaseModel
from database import notfications_collection 

from auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationCreate(BaseModel):
    title: str
    description: str
    recipients: List[str]

# API endpoint to post a notification
@router.post("/", response_model=dict)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Extract details from token
        company_id = current_user.get("company_id")
        plant_id = current_user.get("plant_id")
        sender_id = current_user.get("user_id")

        if not all([company_id, plant_id, sender_id]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing required fields"
            )

        # Assert types to satisfy Pylance
        assert isinstance(company_id, str), "company_id must be a string"
        assert isinstance(plant_id, str), "plant_id must be a string"
        assert isinstance(sender_id, str), "sender_id must be a string"

        # Create new notification as a Notification object
        new_notification = Notification(
            sender=sender_id,
            recipients=notification_data.recipients,
            title=notification_data.title,
            description=notification_data.description
        )

        # Find existing document
        existing_doc = await notfications_collection.find_one({
            "company_id": company_id,
            "plant_id": plant_id
        })

        if existing_doc:
            # Append new notification (as dict) to existing notifications list
            existing_doc["notifications"].append(new_notification.dict(by_alias=True))

            # Update the document
            await notfications_collection.update_one(
                {"company_id": company_id, "plant_id": plant_id},
                {
                    "$set": {
                        "notifications": existing_doc["notifications"],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            # Create a new document
            new_doc = NotificationCollection(
                company_id=company_id,
                plant_id=plant_id,
                notifications=[new_notification],
                updated_at=datetime.utcnow()
            ).dict(by_alias=True)
            await notfications_collection.insert_one(new_doc)

        return {"message": "Notification created successfully", "notification_id": new_notification.notification_id}

    except ValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid notification data: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )

# API endpoint to get notifications
@router.get("/", response_model=Dict)
async def get_notifications(current_user: dict = Depends(get_current_user)):
    try:
        # Extract details from token
        company_id = current_user.get("company_id")
        plant_id = current_user.get("plant_id")
        user_id = current_user.get("user_id")

        if not all([company_id, plant_id, user_id]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing required fields"
            )

        # Find notifications for the company and plant
        notifications_doc = await notfications_collection.find_one({
            "company_id": company_id,
            "plant_id": plant_id
        })

        if not notifications_doc:
            return {"notifications": []}

        # Filter notifications where the user is a recipient
        user_notifications = [
            notification for notification in notifications_doc["notifications"]
            if user_id in notification["recipients"]
        ]

        return {"notifications": user_notifications}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )