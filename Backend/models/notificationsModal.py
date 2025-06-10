from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from enum import Enum

class NotificationStatus(str, Enum):
    SENT = "sent"
    READ = "read"
    UNREAD = "unread"

class NotificationType(str, Enum):
    ALERT = "alert"
    UPDATE = "update"
    REMINDER = "reminder"
    WARNING = "warning"

class Notification(BaseModel):
    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    sender: str = Field(..., description="Reference to the user (e.g., admin) who sent the notification")
    recipients: List[str] = Field(..., description="List of user IDs who receive the notification")
    title: str = Field(..., description="Title of the notification")
    description: str = Field(..., description="Detailed message or content of the notification")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the notification was created")
    #status: NotificationStatus = Field(default=NotificationStatus.UNREAD, description="Tracks if the notification has been read by recipients")
    #type: Optional[NotificationType] = Field(None, description="Categorizes the notification for filtering or display purposes")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            uuid.UUID: lambda v: str(v)
        }

class NotificationCollection(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    company_id: str = Field(..., description="Reference to the company that owns the notifications")
    plant_id: str = Field(..., description="Reference to the specific plant under the company")
    notifications: List[Notification] = Field(default_factory=list, description="List of notifications for the plant")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the document was created")
    updated_at: Optional[datetime] = Field(None, description="When the document was last updated")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            uuid.UUID: lambda v: str(v)
        }