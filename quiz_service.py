from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List, Dict
from models import Quiz, Question, Answer, UserQuizAttempt, Meeting, Transcribe, QuizType, User, UserMeetingEvaluation
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
        """Get existing meeting summary without regenerating"""
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            return None
        
        # Get transcript count
        transcript_count = self.db.query(Transcribe).filter(
            Transcribe.meeting_id == meeting_id
        ).count()
        
        return {
            "meeting_id": meeting_id,
            "meeting_name": meeting.name,
            "meeting_description": meeting.description,
            "summary_points": meeting.summary,
            "generated_at": meeting.created_at if meeting.summary else None,
            "has_summary": meeting.summary is not None,
            "transcript_count": transcript_count
        }

    async def generate_meeting_summary(self, meeting_id: int) -> Dict:
        """Generate summary from transcripts and save to meeting"""
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

        # Generate summary using AI
        summary_points = await self.ai_service.generate_summary_from_transcripts(
            meeting.name,
            meeting.description,
            transcript_dicts
        )

        # Save summary to meeting
        meeting.summary = summary_points
        self.db.commit()
        self.db.refresh(meeting)

        return {
            "meeting_id": meeting_id,
            "meeting_name": meeting.name,
            "meeting_description": meeting.description,
            "summary_points": summary_points,
            "generated_at": datetime.now(),
            "has_summary": True,
            "transcript_count": len(transcripts)
        }

    async def get_or_create_outro_quiz(self, meeting_id: int) -> Quiz:
        """Get existing outro quiz or create new one based on summary"""
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

        # Check if summary exists, if not generate it
        if not meeting.summary:
            # Generate summary first
            await self.generate_meeting_summary(meeting_id)
            self.db.refresh(meeting)

        # Generate quiz based on summary
        quiz_data = await self.ai_service.generate_outro_quiz_from_summary(
            meeting.name,
            meeting.description,
            meeting.summary
        )

        # Create quiz in database
        return self._create_quiz_from_data(
            meeting_id=meeting_id,
            quiz_type=QuizType.outro,
            quiz_data=quiz_data,
            summary_points=meeting.summary
        )

    async def evaluate_user_performance(self, meeting_id: int, username: str) -> Dict:
        """
        Generate performance evaluation for a user in a specific meeting.
        Only runs once per user-meeting combination.
        Calculates score (0-100), updates user credits and rolling average score.
        """
        # Check if evaluation already exists
        existing_eval = self.db.query(UserMeetingEvaluation).filter(
            UserMeetingEvaluation.meeting_id == meeting_id,
            UserMeetingEvaluation.user_username == username
        ).first()

        if existing_eval:
            raise ValueError(f"User {username} has already been evaluated for meeting {meeting_id}")

        # Verify meeting exists
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Verify user exists
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User {username} not found")

        # Get user's transcripts for this meeting
        user_transcripts = self.db.query(Transcribe).filter(
            Transcribe.meeting_id == meeting_id,
            Transcribe.user_username == username
        ).order_by(Transcribe.timestamp.asc()).all()

        if not user_transcripts:
            raise ValueError(f"User {username} has no transcripts for meeting {meeting_id}")

        # Calculate foul count
        foul_count = sum(1 for t in user_transcripts if t.foul)
        total_transcripts = len(user_transcripts)

        # Get outro quiz score for this meeting
        outro_quiz = self.db.query(Quiz).filter(
            Quiz.meeting_id == meeting_id,
            Quiz.quiz_type == QuizType.outro
        ).first()

        if not outro_quiz:
            raise ValueError(f"No outro quiz found for meeting {meeting_id}")

        # Get user's quiz attempt
        quiz_attempt = self.db.query(UserQuizAttempt).filter(
            UserQuizAttempt.user_username == username,
            UserQuizAttempt.quiz_id == outro_quiz.id
        ).first()

        if not quiz_attempt:
            raise ValueError(f"User {username} has not completed the outro quiz for meeting {meeting_id}")

        # Calculate quiz percentage
        quiz_percentage = (quiz_attempt.score / quiz_attempt.total_questions) * 100

        # Calculate quiz score component (0-30 points)
        quiz_score = int((quiz_percentage / 100) * 30)

        # Prepare transcript data for AI
        transcript_dicts = [
            {
                "transcription_text": t.transcription_text,
                "timestamp": t.timestamp.isoformat()
            }
            for t in user_transcripts
        ]

        # Generate AI evaluation
        ai_evaluation = await self.ai_service.generate_user_performance_evaluation(
            username=username,
            meeting_name=meeting.name,
            meeting_description=meeting.description,
            user_transcripts=transcript_dicts,
            foul_count=foul_count,
            total_transcripts=total_transcripts,
            quiz_percentage=quiz_percentage
        )

        participation_score = ai_evaluation["participation_score"]
        quality_score = ai_evaluation["quality_score"]
        strengths = ai_evaluation["strengths"]
        weaknesses = ai_evaluation["weaknesses"]
        tips = ai_evaluation["tips"]

        # Calculate total evaluation score (0-100)
        total_score = quiz_score + participation_score + quality_score

        # Count meetings attended (based on outro quiz attempts)
        meetings_attended = self.db.query(UserQuizAttempt).join(Quiz).filter(
            UserQuizAttempt.user_username == username,
            Quiz.quiz_type == QuizType.outro
        ).count() + 1  # +1 for current meeting

        # Calculate new rolling average score
        if meetings_attended == 1:
            new_average_score = total_score
        else:
            new_average_score = ((meetings_attended - 1) * user.score + total_score) / meetings_attended

        # Update user's score and credits
        user.score = int(new_average_score)
        user.credits += total_score

        # Save evaluation
        evaluation = UserMeetingEvaluation(
            user_username=username,
            meeting_id=meeting_id,
            evaluation_score=total_score,
            strengths=strengths,
            weaknesses=weaknesses,
            tips=tips,
            quiz_score=quiz_score,
            participation_score=participation_score,
            quality_score=quality_score
        )

        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        self.db.refresh(user)

        return {
            "meeting_id": meeting_id,
            "meeting_name": meeting.name,
            "username": username,
            "evaluation_score": total_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "tips": tips,
            "breakdown": {
                "quiz_score": quiz_score,
                "participation_score": participation_score,
                "quality_score": quality_score
            },
            "meetings_attended": meetings_attended,
            "updated_user_score": user.score,
            "credits_earned": total_score,
            "evaluated_at": evaluation.evaluated_at
        }

    async def evaluate_team_performance(self, meeting_id: int) -> Dict:
        """
        Generate team-level performance evaluation by aggregating all individual evaluations.
        Accepts any number of evaluations (>=1).
        Regenerates on each call to include latest data.
        """
        # Verify meeting exists
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Get all individual evaluations for this meeting
        evaluations = self.db.query(UserMeetingEvaluation).filter(
            UserMeetingEvaluation.meeting_id == meeting_id
        ).all()

        if not evaluations:
            raise ValueError(f"No individual evaluations found for meeting {meeting_id}")

        participant_count = len(evaluations)

        # Calculate average scores
        total_evaluation_score = sum(e.evaluation_score for e in evaluations)
        total_quiz_score = sum(e.quiz_score for e in evaluations)
        total_participation_score = sum(e.participation_score for e in evaluations)
        total_quality_score = sum(e.quality_score for e in evaluations)

        avg_evaluation_score = int(total_evaluation_score / participant_count)
        avg_quiz_score = int(total_quiz_score / participant_count)
        avg_participation_score = int(total_participation_score / participant_count)
        avg_quality_score = int(total_quality_score / participant_count)

        # Prepare evaluation data for AI (without usernames for anonymity)
        eval_data = [
            {
                "evaluation_score": e.evaluation_score,
                "strengths": e.strengths,
                "weaknesses": e.weaknesses,
                "tips": e.tips,
                "quiz_score": e.quiz_score,
                "participation_score": e.participation_score,
                "quality_score": e.quality_score
            }
            for e in evaluations
        ]

        # Generate team evaluation using AI
        ai_evaluation = await self.ai_service.generate_team_evaluation(
            meeting_name=meeting.name,
            meeting_description=meeting.description,
            participant_count=participant_count,
            individual_evaluations=eval_data
        )

        # Update meeting with team evaluation
        meeting.team_evaluation_score = avg_evaluation_score
        meeting.team_strengths = ai_evaluation["team_strengths"]
        meeting.team_weaknesses = ai_evaluation["team_weaknesses"]
        meeting.team_tips = ai_evaluation["team_tips"]
        meeting.team_evaluated_at = datetime.now()

        self.db.commit()
        self.db.refresh(meeting)

        return {
            "meeting_id": meeting_id,
            "meeting_name": meeting.name,
            "team_evaluation_score": avg_evaluation_score,
            "team_strengths": ai_evaluation["team_strengths"],
            "team_weaknesses": ai_evaluation["team_weaknesses"],
            "team_tips": ai_evaluation["team_tips"],
            "average_breakdown": {
                "quiz_score": avg_quiz_score,
                "participation_score": avg_participation_score,
                "quality_score": avg_quality_score
            },
            "participant_count": participant_count,
            "evaluated_at": meeting.team_evaluated_at
        }