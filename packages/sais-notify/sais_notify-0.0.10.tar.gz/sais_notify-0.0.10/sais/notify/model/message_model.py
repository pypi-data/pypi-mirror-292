from typing import Optional

from pydantic import BaseModel, Field

from sais.notify.types import NotifyType


class NotificationRequest(BaseModel):
    notify_type: NotifyType
    to: str
    message: str


class MessageModel(BaseModel):
    message: str
    to: str
    type: Optional[str]
    subject: Optional[str] = None
    sign_name: str = Field(default=None, alias='signName', description='Sign name field')
    template_code: str = Field(default=None, alias='templateCode', description='Template code field')
    robot_name: str = Field(default=None, alias='robotName', description='Robot name field')
