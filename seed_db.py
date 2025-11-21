"""
Database seeder script for testing.
Creates 2 meetings with users, transcripts, quizzes, and evaluations.
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import (
    User, Meeting, Transcribe, Quiz, Question, Answer, 
    UserQuizAttempt, UserMeetingEvaluation, QuizType
)
from openrouter_service import OpenRouterService
from quiz_service import QuizService


async def seed_database():
    """Seed the database with test data"""
    # Recreate tables to ensure schema is up to date
    print("🔄 Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables recreated\n")
    
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # Create users
        print("\n👥 Creating users...")
        users = [
            User(username="alice", discord_user_id="111111", score=0, credits=0),
            User(username="bob", discord_user_id="222222", score=0, credits=0),
            User(username="charlie", discord_user_id="333333", score=0, credits=0),
            User(username="diana", discord_user_id="444444", score=0, credits=0),
        ]
        
        for user in users:
            existing = db.query(User).filter(User.username == user.username).first()
            if not existing:
                db.add(user)
                print(f"  ✓ Created user: {user.username}")
            else:
                print(f"  ⊙ User already exists: {user.username}")
        
        db.commit()
        
        # Create Meeting 1: Product Planning
        print("\n📅 Creating Meeting 1: Product Planning...")
        meeting1 = Meeting(
            name="Q1 Product Planning",
            description="Planning session for Q1 product roadmap, discussing new features and prioritization",
            summary=None
        )
        db.add(meeting1)
        db.commit()
        db.refresh(meeting1)
        print(f"  ✓ Created meeting: {meeting1.name} (ID: {meeting1.id})")
        
        # Create transcripts for Meeting 1
        print("\n💬 Creating transcripts for Meeting 1...")
        base_time = datetime.now() - timedelta(hours=2)
        transcripts1 = [
            Transcribe(
                user_username="alice",
                meeting_id=meeting1.id,
                transcription_text="Good morning everyone! Let's start by reviewing our Q1 goals.",
                timestamp=base_time,
                foul=False,
                guild_id="guild_001",
                channel_id="channel_001"
            ),
            Transcribe(
                user_username="bob",
                meeting_id=meeting1.id,
                transcription_text="I think we should prioritize the mobile app improvements first.",
                timestamp=base_time + timedelta(minutes=1),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_001"
            ),
            Transcribe(
                user_username="charlie",
                meeting_id=meeting1.id,
                transcription_text="Great point Bob. We also need to address the performance issues in the dashboard.",
                timestamp=base_time + timedelta(minutes=2),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_001"
            ),
            Transcribe(
                user_username="alice",
                meeting_id=meeting1.id,
                transcription_text="Agreed. Let's allocate 40% of resources to mobile and 30% to dashboard optimization.",
                timestamp=base_time + timedelta(minutes=3),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_001"
            ),
            Transcribe(
                user_username="diana",
                meeting_id=meeting1.id,
                transcription_text="What about the API v2 migration? That's been pending for a while.",
                timestamp=base_time + timedelta(minutes=4),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_001"
            ),
            Transcribe(
                user_username="bob",
                meeting_id=meeting1.id,
                transcription_text="Good point Diana. We can dedicate the remaining 30% to API work.",
                timestamp=base_time + timedelta(minutes=5),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_001"
            ),
            Transcribe(
                user_username="charlie",
                meeting_id=meeting1.id,
                transcription_text="I'll create tickets for each initiative and assign them to the respective teams.",
                timestamp=base_time + timedelta(minutes=6),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_001"
            ),
            Transcribe(
                user_username="alice",
                meeting_id=meeting1.id,
                transcription_text="Perfect. Let's meet again next week to review progress.",
                timestamp=base_time + timedelta(minutes=7),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_001"
            ),
        ]
        
        for transcript in transcripts1:
            db.add(transcript)
        db.commit()
        print(f"  ✓ Created {len(transcripts1)} transcripts")
        
        # Generate intro quiz for Meeting 1
        print("\n📝 Generating intro quiz for Meeting 1...")
        quiz_service = QuizService(db)
        intro_quiz1 = await quiz_service.get_or_create_intro_quiz(meeting1.id)
        print(f"  ✓ Created intro quiz (ID: {intro_quiz1.id})")
        
        # Generate summary and outro quiz for Meeting 1
        print("\n📊 Generating summary for Meeting 1...")
        summary1 = await quiz_service.generate_meeting_summary(meeting1.id)
        print(f"  ✓ Generated meeting summary")
        
        print("\n📝 Generating outro quiz for Meeting 1...")
        outro_quiz1 = await quiz_service.get_or_create_outro_quiz(meeting1.id)
        print(f"  ✓ Created outro quiz (ID: {outro_quiz1.id})")
        
        # Submit quiz attempts for Meeting 1 users
        print("\n✍️ Creating quiz attempts for Meeting 1...")
        quiz_attempts1 = [
            {"username": "alice", "score": 5, "answers": [0, 1, 2, 3, 0]},  # 100%
            {"username": "bob", "score": 4, "answers": [0, 1, 2, 3, 1]},    # 80%
            {"username": "charlie", "score": 4, "answers": [0, 1, 2, 0, 0]}, # 80%
            {"username": "diana", "score": 3, "answers": [0, 1, 1, 3, 0]},   # 60%
        ]
        
        for attempt_data in quiz_attempts1:
            # Create quiz attempt record
            attempt = UserQuizAttempt(
                user_username=attempt_data["username"],
                quiz_id=outro_quiz1.id,
                score=attempt_data["score"],
                total_questions=5
            )
            db.add(attempt)
            print(f"  ✓ Created quiz attempt for {attempt_data['username']}: {attempt_data['score']}/5")
        
        db.commit()
        
        # Generate user evaluations for Meeting 1
        print("\n⭐ Generating user evaluations for Meeting 1...")
        for user_data in ["alice", "bob", "charlie"]:  # Leave diana for manual testing
            try:
                result = await quiz_service.evaluate_user_performance(meeting1.id, user_data)
                print(f"  ✓ Evaluated {user_data}: {result['evaluation_score']}/100")
            except Exception as e:
                print(f"  ✗ Failed to evaluate {user_data}: {e}")
        
        # Generate team evaluation for Meeting 1
        print("\n🏆 Generating team evaluation for Meeting 1...")
        try:
            team_result1 = await quiz_service.evaluate_team_performance(meeting1.id)
            print(f"  ✓ Team evaluation complete: {team_result1['team_evaluation_score']}/100 (from {team_result1['participant_count']} participants)")
        except Exception as e:
            print(f"  ✗ Failed to generate team evaluation: {e}")
        
        # ============================================================================
        # Create Meeting 2: Engineering Sync
        # ============================================================================
        
        print("\n\n📅 Creating Meeting 2: Engineering Sync...")
        meeting2 = Meeting(
            name="Engineering Weekly Sync",
            description="Weekly engineering team sync to discuss technical challenges, blockers, and upcoming sprints",
            summary=None
        )
        db.add(meeting2)
        db.commit()
        db.refresh(meeting2)
        print(f"  ✓ Created meeting: {meeting2.name} (ID: {meeting2.id})")
        
        # Create transcripts for Meeting 2
        print("\n💬 Creating transcripts for Meeting 2...")
        base_time2 = datetime.now() - timedelta(hours=1)
        transcripts2 = [
            Transcribe(
                user_username="bob",
                meeting_id=meeting2.id,
                transcription_text="Let's discuss the database migration issues we encountered this week.",
                timestamp=base_time2,
                foul=False,
                guild_id="guild_001",
                channel_id="channel_002"
            ),
            Transcribe(
                user_username="charlie",
                meeting_id=meeting2.id,
                transcription_text="The main issue was with foreign key constraints. We had to roll back twice.",
                timestamp=base_time2 + timedelta(minutes=1),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_002"
            ),
            Transcribe(
                user_username="diana",
                meeting_id=meeting2.id,
                transcription_text="I recommend we add more comprehensive tests before the next migration.",
                timestamp=base_time2 + timedelta(minutes=2),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_002"
            ),
            Transcribe(
                user_username="bob",
                meeting_id=meeting2.id,
                transcription_text="Good idea. Let's also improve our rollback procedures.",
                timestamp=base_time2 + timedelta(minutes=3),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_002"
            ),
            Transcribe(
                user_username="alice",
                meeting_id=meeting2.id,
                transcription_text="On a different note, the CI/CD pipeline is running much faster now after the optimizations.",
                timestamp=base_time2 + timedelta(minutes=4),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_002"
            ),
            Transcribe(
                user_username="charlie",
                meeting_id=meeting2.id,
                transcription_text="Yes! Build times are down from 15 minutes to 6 minutes. Great work Alice.",
                timestamp=base_time2 + timedelta(minutes=5),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_002"
            ),
            Transcribe(
                user_username="diana",
                meeting_id=meeting2.id,
                transcription_text="Should we tackle the authentication service refactor next sprint?",
                timestamp=base_time2 + timedelta(minutes=6),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_002"
            ),
            Transcribe(
                user_username="bob",
                meeting_id=meeting2.id,
                transcription_text="Let's prioritize it. We can split it into smaller chunks to make it manageable.",
                timestamp=base_time2 + timedelta(minutes=7),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_002"
            ),
            Transcribe(
                user_username="alice",
                meeting_id=meeting2.id,
                transcription_text="Agreed. I'll draft a technical proposal for the refactor by end of week.",
                timestamp=base_time2 + timedelta(minutes=8),
                foul=False,
                guild_id="guild_001",
                channel_id="channel_002"
            ),
        ]
        
        for transcript in transcripts2:
            db.add(transcript)
        db.commit()
        print(f"  ✓ Created {len(transcripts2)} transcripts")
        
        # Generate intro quiz for Meeting 2
        print("\n📝 Generating intro quiz for Meeting 2...")
        intro_quiz2 = await quiz_service.get_or_create_intro_quiz(meeting2.id)
        print(f"  ✓ Created intro quiz (ID: {intro_quiz2.id})")
        
        # Generate summary and outro quiz for Meeting 2
        print("\n📊 Generating summary for Meeting 2...")
        summary2 = await quiz_service.generate_meeting_summary(meeting2.id)
        print(f"  ✓ Generated meeting summary")
        
        print("\n📝 Generating outro quiz for Meeting 2...")
        outro_quiz2 = await quiz_service.get_or_create_outro_quiz(meeting2.id)
        print(f"  ✓ Created outro quiz (ID: {outro_quiz2.id})")
        
        # Submit quiz attempts for Meeting 2 users
        print("\n✍️ Creating quiz attempts for Meeting 2...")
        quiz_attempts2 = [
            {"username": "alice", "score": 4, "answers": [0, 1, 2, 3, 1]},   # 80%
            {"username": "bob", "score": 5, "answers": [0, 1, 2, 3, 0]},     # 100%
            {"username": "charlie", "score": 3, "answers": [0, 1, 1, 3, 1]}, # 60%
            {"username": "diana", "score": 4, "answers": [0, 1, 2, 0, 0]},   # 80%
        ]
        
        for attempt_data in quiz_attempts2:
            attempt = UserQuizAttempt(
                user_username=attempt_data["username"],
                quiz_id=outro_quiz2.id,
                score=attempt_data["score"],
                total_questions=5
            )
            db.add(attempt)
            print(f"  ✓ Created quiz attempt for {attempt_data['username']}: {attempt_data['score']}/5")
        
        db.commit()
        
        # Generate user evaluations for Meeting 2
        print("\n⭐ Generating user evaluations for Meeting 2...")
        for user_data in ["alice", "bob", "charlie", "diana"]:
            try:
                result = await quiz_service.evaluate_user_performance(meeting2.id, user_data)
                print(f"  ✓ Evaluated {user_data}: {result['evaluation_score']}/100")
            except Exception as e:
                print(f"  ✗ Failed to evaluate {user_data}: {e}")
        
        # Generate team evaluation for Meeting 2
        print("\n🏆 Generating team evaluation for Meeting 2...")
        try:
            team_result2 = await quiz_service.evaluate_team_performance(meeting2.id)
            print(f"  ✓ Team evaluation complete: {team_result2['team_evaluation_score']}/100 (from {team_result2['participant_count']} participants)")
        except Exception as e:
            print(f"  ✗ Failed to generate team evaluation: {e}")
        
        print("\n\n✅ Database seeding completed successfully!")
        print("\n📋 Summary:")
        print(f"  • Created 4 users: alice, bob, charlie, diana")
        print(f"  • Created 2 meetings with transcripts")
        print(f"  • Generated intro and outro quizzes for both meetings")
        print(f"  • Created quiz attempts for all users")
        print(f"  • Generated individual and team evaluations")
        print("\n🔗 Test the API:")
        print(f"  • Meeting 1 ID: {meeting1.id}")
        print(f"  • Meeting 2 ID: {meeting2.id}")
        print(f"  • GET /meeting/{meeting1.id}/evaluate (team evaluation)")
        print(f"  • GET /user/alice/quiz-attempts")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🌱 Database Seeder")
    print("=" * 60)
    asyncio.run(seed_database())
