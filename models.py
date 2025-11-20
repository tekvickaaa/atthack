from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import datetime
from sqlalchemy.sql.sqltypes import Interval
from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    discord_user_id = Column(String, nullable=True)  # Added for Discord ID
    strengths = Column(String, nullable=True)
    weaknesses = Column(String, nullable=True)
    score = Column(Integer, default=0)
    credits = Column(Integer, default=0)

    transcribes = relationship("Transcribe", backref="user")
    owned_meetings = relationship("Meeting", backref="owner")
    meetings_participated = relationship("Participant", backref="user")


class Transcribe(Base):
    __tablename__ = 'transcribes'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Added auto-increment ID
    user_username = Column(String, ForeignKey('users.username'), nullable=False)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)

    transcription_text = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)  # Individual transcript timestamp
    guild_id = Column(String, nullable=True)  # Discord guild/server ID
    channel_id = Column(String, nullable=True)  # Discord channel ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # DB creation time


class Meeting(Base):
    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    temp_meeting_id = Column(String, nullable=True, unique=True)  # Store the original temp ID
    summary = Column(String, nullable=True)
    begins_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Interval, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Meeting creation time
    owner_username = Column(String, ForeignKey('users.username'), nullable=True)

    transcribes = relationship("Transcribe", backref="meeting")
    participants = relationship("Participant", backref="meeting")


class Participant(Base):
    __tablename__ = 'meeting_participants'
    __table_args__ = (UniqueConstraint('meeting_id', 'user_username', name='_meeting_user_uc'),)

    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    user_username = Column(String, ForeignKey('users.username'), nullable=False)