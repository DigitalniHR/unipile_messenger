"""
Pydantic models for UniPile API responses.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class Account(BaseModel):
    """UniPile connected account (LinkedIn, Email, etc.)."""

    id: str = Field(alias="id")
    provider: str = Field(default="LINKEDIN")
    name: Optional[str] = None
    identifier: Optional[str] = None  # email or username
    status: str = "OK"  # OK, CREDENTIALS_REQUIRED, etc.
    created_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class ChatParticipant(BaseModel):
    """Participant in a chat conversation."""

    attendee_id: Optional[str] = None
    attendee_provider_id: Optional[str] = None
    name: Optional[str] = None
    profile_url: Optional[str] = None
    profile_picture_url: Optional[str] = None


class Chat(BaseModel):
    """Chat/conversation from UniPile."""

    id: str
    account_id: str
    provider: str = "LINKEDIN"
    name: Optional[str] = None
    attendees: List[ChatParticipant] = []
    last_message_text: Optional[str] = None
    last_message_timestamp: Optional[datetime] = None
    unread_count: int = 0
    is_group: bool = False

    class Config:
        populate_by_name = True


class Message(BaseModel):
    """Individual message in a chat."""

    id: str
    chat_id: Optional[str] = None
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    text: Optional[str] = None
    timestamp: Optional[datetime] = None
    is_sender: bool = False  # True if sent by the connected account
    attachments: List[Any] = []

    class Config:
        populate_by_name = True


class Connection(BaseModel):
    """LinkedIn connection/relation."""

    id: str
    provider_id: Optional[str] = None
    name: Optional[str] = None
    headline: Optional[str] = None
    profile_url: Optional[str] = None
    profile_picture_url: Optional[str] = None


class APIResponse(BaseModel):
    """Generic API response wrapper."""

    items: List[Any] = []
    cursor: Optional[str] = None  # For pagination
    has_more: bool = False
