from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# Request schemas
class MeetingCreate(BaseModel):
    name: str
    description: str

class TranscriptItem(BaseModel):
    userId: str
    username: str
    transcription: str
    timestamp: str  # ISO format datetime string
    guildId: str
    channelId: str

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
    foul: bool
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

class ParticipantResponse(BaseSchema):
    id: int
    meeting_id: int
    user_username: str


from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class QuizTypeEnum(str, Enum):
    intro = "intro"
    outro = "outro"


# Answer schemas
class AnswerBase(BaseModel):
    answer_text: str
    order: int = Field(..., ge=0, le=3)


class AnswerResponse(AnswerBase):
    id: int
    question_id: int

    model_config = {"from_attributes": True}


# Question schemas
class QuestionBase(BaseModel):
    question_text: str
    order: int = Field(..., ge=0, le=4)


class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int
    answers: List[AnswerResponse]

    model_config = {"from_attributes": True}


class QuestionWithCorrectAnswer(QuestionResponse):
    """Extended version that includes correct answer - only used after submission"""
    correct_answer_index: int


# Quiz schemas
class QuizResponse(BaseModel):
    id: int
    meeting_id: int
    quiz_type: QuizTypeEnum
    summary_points: Optional[str] = None
    generated_at: datetime
    questions: List[QuestionResponse]

    model_config = {"from_attributes": True}


class QuizWithAnswers(BaseModel):
    """Quiz response after submission - includes correct answers"""
    id: int
    meeting_id: int
    quiz_type: QuizTypeEnum
    summary_points: Optional[str] = None
    generated_at: datetime
    questions: List[QuestionWithCorrectAnswer]

    model_config = {"from_attributes": True}


# Quiz submission schemas
class QuestionAnswerSubmission(BaseModel):
    question_id: int
    selected_answer_index: int = Field(..., ge=0, le=3)


class QuizSubmission(BaseModel):
    user_username: str
    answers: List[QuestionAnswerSubmission]

    @field_validator('answers')
    @classmethod
    def validate_answers_length(cls, v):
        if len(v) != 5:
            raise ValueError('Must submit exactly 5 answers')
        return v


class QuizSubmissionResponse(BaseModel):
    score: int
    total_questions: int
    percentage: float
    passed: bool  # True if >= 60%
    correct_answers: List[int]  # List of correct answer indices
    user_answers: List[int]  # List of user's submitted answer indices
    quiz_with_answers: QuizWithAnswers
    attempt_id: int


# User quiz attempt schemas
class UserQuizAttemptResponse(BaseModel):
    id: int
    user_username: str
    quiz_id: int
    score: int
    total_questions: int
    completed_at: datetime
    percentage: float
    passed: bool

    model_config = {"from_attributes": True}


class MeetingSummaryResponse(BaseModel):
    meeting_id: int
    meeting_name: str
    meeting_description: str
    summary_points: Optional[str] = None
    generated_at: Optional[datetime] = None
    has_summary: bool
    transcript_count: Optional[int] = None


# User meeting evaluation schemas
class ScoreBreakdown(BaseModel):
    quiz_score: int  # 0-30
    participation_score: int  # 0-20
    quality_score: int  # 0-50


class UserMeetingEvaluationResponse(BaseModel):
    meeting_id: int
    meeting_name: str
    username: str
    evaluation_score: int  # 0-100 total
    strengths: str
    weaknesses: str
    tips: str
    breakdown: ScoreBreakdown
    meetings_attended: int
    updated_user_score: int
    credits_earned: int
    evaluated_at: datetime