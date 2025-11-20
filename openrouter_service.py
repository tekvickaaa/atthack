import os
import json
import httpx
from typing import List, Dict, Optional
from datetime import datetime


class OpenRouterService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "openai/gpt-oss-20b:free"
        self.timeout = 60.0

    async def _make_request(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Make async request to OpenRouter API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": os.getenv("APP_URL", "http://localhost:8000"),
                    "X-Title": "Meeting Quiz Generator"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate_intro_quiz(self, meeting_name: str, meeting_description: str) -> Dict:
        """
        Generate an introductory quiz based on meeting topic.
        Returns dict with questions array.
        """
        prompt = f"""Generate 5 multiple-choice questions for an introductory quiz about the following meeting:

Meeting Name: {meeting_name}
Description: {meeting_description}

Create questions that test basic knowledge and expectations about this topic. Each question should have 4 possible answers with exactly one correct answer.

Return ONLY valid JSON in this exact format with no markdown, no backticks, no preamble:
{{
  "questions": [
    {{
      "question_text": "Question text here?",
      "answers": [
        "Answer option 1",
        "Answer option 2",
        "Answer option 3",
        "Answer option 4"
      ],
      "correct_answer_index": 0
    }}
  ]
}}

Ensure:
- Exactly 5 questions
- Each question has exactly 4 answers
- correct_answer_index is 0, 1, 2, or 3
- Questions are relevant to the meeting topic
- Mix of difficulty levels"""

        messages = [{"role": "user", "content": prompt}]
        response_text = await self._make_request(messages, temperature=0.7)

        # Clean response and parse JSON
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            quiz_data = json.loads(response_text)
            self._validate_quiz_structure(quiz_data)
            return quiz_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {e}")

    async def generate_outro_quiz_and_summary(
            self,
            meeting_name: str,
            transcripts: List[Dict]
    ) -> Dict:
        """
        Generate an outro quiz and summary based on meeting transcripts.
        Returns dict with questions array and summary_points string.
        """
        # Format transcripts for prompt
        transcript_text = self._format_transcripts(transcripts)

        prompt = f"""Analyze the following meeting transcripts and generate:
1. A summary of key points (5-7 bullet points)
2. 5 multiple-choice questions testing understanding of what was discussed

Meeting Name: {meeting_name}

Transcripts:
{transcript_text}

Return ONLY valid JSON in this exact format with no markdown, no backticks, no preamble:
{{
  "summary_points": "• Key point 1\\n• Key point 2\\n• Key point 3\\n• Key point 4\\n• Key point 5",
  "questions": [
    {{
      "question_text": "Question text here?",
      "answers": [
        "Answer option 1",
        "Answer option 2",
        "Answer option 3",
        "Answer option 4"
      ],
      "correct_answer_index": 0
    }}
  ]
}}

Ensure:
- Summary has 5-7 bullet points separated by \\n
- Exactly 5 questions
- Each question has exactly 4 answers
- correct_answer_index is 0, 1, 2, or 3
- Questions test comprehension of actual meeting content
- Mix of detail and big-picture questions"""

        messages = [{"role": "user", "content": prompt}]
        response_text = await self._make_request(messages, temperature=0.7)

        # Clean response and parse JSON
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            quiz_data = json.loads(response_text)
            self._validate_quiz_structure(quiz_data, require_summary=True)
            return quiz_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {e}")

    def _format_transcripts(self, transcripts: List[Dict]) -> str:
        """Format transcripts for AI prompt"""
        formatted = []
        for t in transcripts:
            timestamp = t.get('timestamp', 'Unknown time')
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            username = t.get('user_username', t.get('username', 'Unknown'))
            text = t.get('transcription_text', t.get('transcription', ''))

            formatted.append(f"[{timestamp}] {username}: {text}")

        return "\n".join(formatted)

    def _validate_quiz_structure(self, quiz_data: Dict, require_summary: bool = False):
        """Validate the quiz data structure"""
        if "questions" not in quiz_data:
            raise ValueError("Response missing 'questions' field")

        if require_summary and "summary_points" not in quiz_data:
            raise ValueError("Response missing 'summary_points' field")

        questions = quiz_data["questions"]
        if len(questions) != 5:
            raise ValueError(f"Expected 5 questions, got {len(questions)}")

        for i, q in enumerate(questions):
            if "question_text" not in q:
                raise ValueError(f"Question {i} missing 'question_text'")
            if "answers" not in q:
                raise ValueError(f"Question {i} missing 'answers'")
            if "correct_answer_index" not in q:
                raise ValueError(f"Question {i} missing 'correct_answer_index'")

            if len(q["answers"]) != 4:
                raise ValueError(f"Question {i} must have exactly 4 answers")

            if not (0 <= q["correct_answer_index"] <= 3):
                raise ValueError(f"Question {i} correct_answer_index must be 0-3")