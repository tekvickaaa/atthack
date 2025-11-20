from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List, Dict
from models import Quiz, Question, Answer, UserQuizAttempt, Meeting, Transcribe, QuizType
from openrouter_service import OpenRouterService
from datetime import datetime


class QuizService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = OpenRouterService()

    async def get_or_create_intro_quiz(self, meeting_id: int) -> Quiz:
        """Get existing intro quiz or create new one"""
        # Check if intro quiz already exists
        existing_quiz = self.db.query(Quiz).filter(
            Quiz.meeting_id == meeting_id,
            Quiz.quiz_type == QuizType.intro
        ).first()

        if existing_quiz:
            return existing_quiz

        # Get meeting info
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Generate quiz using AI
        quiz_data = await self.ai_service.generate_intro_quiz(
            meeting.name,
            meeting.description
        )

        # Create quiz in database
        return self._create_quiz_from_data(
            meeting_id=meeting_id,
            quiz_type=QuizType.intro,
            quiz_data=quiz_data,
            summary_points=None
        )

    async def get_or_create_outro_quiz(self, meeting_id: int) -> Quiz:
        """Get existing outro quiz or create new one based on transcripts"""
        # Check if outro quiz already exists
        existing_quiz = self.db.query(Quiz).filter(
            Quiz.meeting_id == meeting_id,
            Quiz.quiz_type == QuizType.outro
        ).first()

        if existing_quiz:
            return existing_quiz

        # Get meeting info
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Get transcripts
        transcripts = self.db.query(Transcribe).filter(
            Transcribe.meeting_id == meeting_id
        ).order_by(Transcribe.timestamp.asc()).all()

        if not transcripts:
            raise ValueError(f"No transcripts found for meeting {meeting_id}")

        # Convert to dict for AI service
        transcript_dicts = [
            {
                "user_username": t.user_username,
                "transcription_text": t.transcription_text,
                "timestamp": t.timestamp
            }
            for t in transcripts
        ]

        # Generate quiz and summary using AI
        quiz_data = await self.ai_service.generate_outro_quiz_and_summary(
            meeting.name,
            transcript_dicts
        )

        # Update meeting summary
        meeting.summary = quiz_data.get("summary_points")

        # Create quiz in database
        return self._create_quiz_from_data(
            meeting_id=meeting_id,
            quiz_type=QuizType.outro,
            quiz_data=quiz_data,
            summary_points=quiz_data.get("summary_points")
        )

    def _create_quiz_from_data(
            self,
            meeting_id: int,
            quiz_type: QuizType,
            quiz_data: Dict,
            summary_points: Optional[str]
    ) -> Quiz:
        """Create quiz and questions from AI-generated data"""
        # Create quiz
        new_quiz = Quiz(
            meeting_id=meeting_id,
            quiz_type=quiz_type,
            summary_points=summary_points
        )
        self.db.add(new_quiz)
        self.db.flush()

        # Create questions and answers
        for q_idx, question_data in enumerate(quiz_data["questions"]):
            new_question = Question(
                quiz_id=new_quiz.id,
                question_text=question_data["question_text"],
                correct_answer_index=question_data["correct_answer_index"],
                order=q_idx
            )
            self.db.add(new_question)
            self.db.flush()

            # Create answers
            for a_idx, answer_text in enumerate(question_data["answers"]):
                new_answer = Answer(
                    question_id=new_question.id,
                    answer_text=answer_text,
                    order=a_idx
                )
                self.db.add(new_answer)

        self.db.commit()
        self.db.refresh(new_quiz)
        return new_quiz

    def get_quiz_by_id(self, quiz_id: int) -> Optional[Quiz]:
        """Get quiz by ID with all relations"""
        return self.db.query(Quiz).filter(Quiz.id == quiz_id).first()

    def submit_quiz_attempt(
            self,
            quiz_id: int,
            user_username: str,
            answers: List[Dict[str, int]]
    ) -> Dict:
        """
        Submit quiz attempt and calculate score.
        Returns detailed results including correct answers.
        """
        quiz = self.get_quiz_by_id(quiz_id)
        if not quiz:
            raise ValueError(f"Quiz {quiz_id} not found")

        if len(answers) != len(quiz.questions):
            raise ValueError(f"Expected {len(quiz.questions)} answers, got {len(answers)}")

        # Build question_id to question mapping
        question_map = {q.id: q for q in quiz.questions}

        # Validate all question IDs exist
        for answer in answers:
            if answer["question_id"] not in question_map:
                raise ValueError(f"Invalid question_id: {answer['question_id']}")

        # Calculate score
        correct_count = 0
        correct_answers = []
        user_answers = []

        for answer in answers:
            question = question_map[answer["question_id"]]
            user_answer_idx = answer["selected_answer_index"]

            correct_answers.append(question.correct_answer_index)
            user_answers.append(user_answer_idx)

            if user_answer_idx == question.correct_answer_index:
                correct_count += 1

        total_questions = len(quiz.questions)
        percentage = (correct_count / total_questions) * 100
        passed = percentage >= 60.0

        # Save attempt
        attempt = UserQuizAttempt(
            user_username=user_username,
            quiz_id=quiz_id,
            score=correct_count,
            total_questions=total_questions
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        return {
            "score": correct_count,
            "total_questions": total_questions,
            "percentage": round(percentage, 2),
            "passed": passed,
            "correct_answers": correct_answers,
            "user_answers": user_answers,
            "attempt_id": attempt.id
        }

    def get_user_attempts(self, user_username: str, quiz_id: Optional[int] = None) -> List[UserQuizAttempt]:
        """Get user's quiz attempts, optionally filtered by quiz_id"""
        query = self.db.query(UserQuizAttempt).filter(
            UserQuizAttempt.user_username == user_username
        )

        if quiz_id:
            query = query.filter(UserQuizAttempt.quiz_id == quiz_id)

        return query.order_by(desc(UserQuizAttempt.completed_at)).all()

    def get_meeting_summary(self, meeting_id: int) -> Optional[Dict]:
        """Get meeting summary from outro quiz"""
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            return None

        outro_quiz = self.db.query(Quiz).filter(
            Quiz.meeting_id == meeting_id,
            Quiz.quiz_type == QuizType.outro
        ).first()

        return {
            "meeting_id": meeting_id,
            "meeting_name": meeting.name,
            "summary_points": outro_quiz.summary_points if outro_quiz else None,
            "generated_at": outro_quiz.generated_at if outro_quiz else None,
            "has_outro_quiz": outro_quiz is not None
        }