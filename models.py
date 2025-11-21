from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, UniqueConstraint, Interval, \
    Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
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
    foul = Column(Boolean, default=False, nullable=True)
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

class QuizType(enum.Enum):
    intro = "intro"
    outro = "outro"


class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    quiz_type = Column(SQLEnum(QuizType), nullable=False)
    summary_points = Column(Text, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting", backref="quizzes")
    questions = relationship("Question", backref="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    correct_answer_index = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)

    answers = relationship("Answer", backref="question", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    answer_text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)


class UserQuizAttempt(Base):
    __tablename__ = 'user_quiz_attempts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_username = Column(String, ForeignKey('users.username'), nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="quiz_attempts")
    quiz = relationship("Quiz", backref="attempts")


class UserMeetingEvaluation(Base):
    __tablename__ = 'user_meeting_evaluations'
    __table_args__ = (UniqueConstraint('user_username', 'meeting_id', name='_user_meeting_eval_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_username = Column(String, ForeignKey('users.username'), nullable=False)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    evaluation_score = Column(Integer, nullable=False)  # 0-100
    strengths = Column(Text, nullable=False)
    weaknesses = Column(Text, nullable=False)
    tips = Column(Text, nullable=False)
    quiz_score = Column(Integer, nullable=False)  # 0-30 points
    participation_score = Column(Integer, nullable=False)  # 0-20 points
    quality_score = Column(Integer, nullable=False)  # 0-50 points
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="meeting_evaluations")
    meeting = relationship("Meeting", backref="evaluations")
