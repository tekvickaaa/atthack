from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict, field_serializer, model_validator
from typing import List, Optional, Dict, Any

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseSchema):
    id: int
    username: str
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    score: int = 0
    credits: int = 0

class TranscribeResponse(BaseSchema):
    id: int
    username: str
    meeting_id: int
    transcription_text: Optional[str] = None
    created_at: Optional[datetime] = None

class MeetingResponse(BaseSchema):
    id: int
    name: str
    description: str
    summary: Optional[str] = None
    begins_at: Optional[datetime] = None
    duration: Optional[timedelta] = None
    owner_username: str

class ParticipantResponse(BaseSchema):
    id: int
    meeting_id: int
    user_username: str