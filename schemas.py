from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# Request schemas
class MeetingCreate(BaseModel):
    name: str
    description: str
    meetingId: str  # The temp ID from client
    createdAt: Optional[str] = None  # We'll ignore this but accept it

class TranscriptItem(BaseModel):
    userId: str
    username: str
    transcription: str
    timestamp: str  # ISO format datetime string
    guildId: str
    channelId: str

class TranscriptsCreate(BaseModel):
    meeting_id: int  # The real DB meeting ID
    transcripts: List[TranscriptItem]

# Response schemas
class UserResponse(BaseSchema):
    id: int
    username: str
    discord_user_id: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    score: int = 0
    credits: int = 0

class TranscribeResponse(BaseSchema):
    id: int
    user_username: str
    meeting_id: int
    transcription_text: str
    timestamp: datetime
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    created_at: datetime

class MeetingResponse(BaseSchema):
    id: int
    name: str
    description: str
    temp_meeting_id: Optional[str] = None
    summary: Optional[str] = None
    begins_at: Optional[datetime] = None
    duration: Optional[timedelta] = None
    created_at: datetime
    owner_username: Optional[str] = None

class MeetingCreateResponse(BaseSchema):
    id: int
    name: str
    temp_meeting_id: Optional[str] = None

class ParticipantResponse(BaseSchema):
    id: int
    meeting_id: int
    user_username: str