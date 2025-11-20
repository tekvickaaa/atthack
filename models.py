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
    strengths = Column(String, nullable=True)
    weaknesses = Column(String, nullable=True)
    score = Column(Integer, default=0)
    credits = Column(Integer, default=0)

    transcribes = relationship("Transcribe", backref="user")
    owned_meetings = relationship("Meeting", backref="owner")
    meetings_participated = relationship("Participant", backref="user")

class Transcribe(Base):
    __tablename__ = 'transcribes'

    user_username = Column(String, ForeignKey('users.username'), primary_key=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), primary_key=True)

    transcription_text = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", backref="transcribes")
    meeting = relationship("Meeting", backref="transcribes")

class Meeting(Base):
    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    begins_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Interval, nullable=True)
    owner_username = Column(String, ForeignKey('users.username'), nullable=True)
    user = relationship("User", backref="owned_meetings")
    participants = relationship("Participant", backref="owned_meetings")

class Participant(Base):
    __tablename__ = 'meeting_participants'
    __table_args__ = (UniqueConstraint('meeting_id', 'user_username', name='_meeting_user_uc'),)

    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    user_username = Column(Integer, ForeignKey('users.username'), nullable=False)
    meeting = relationship("Meeting", backref="participants")
    user = relationship("User", backref="meetings_participated")