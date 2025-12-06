from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SessionCreate(BaseModel):
    customer_id: str
    language: Optional[str] = "en"
    channel: Optional[str] = "phone"
    persona: Optional[str] = "default"

class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime

class MessageInput(BaseModel):
    type: str
    text: str | None = None
    audio_file: str | None = None   # instead of audio_base64
    mime: str | None = None

class MessageResponse(BaseModel):
    message_id: str
    incoming_text: str
    reply_text: str
    reply_audio_base64: str

class ConversationResponse(BaseModel):
    conversation: List[dict]

class MCPPayload(BaseModel):
    session_id: str
    customer_id: str
    llm_response: str
    scenario: str
    crm_record: dict
    meta: dict
