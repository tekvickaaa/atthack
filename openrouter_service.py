import httpx
import json
import os
from typing import List, Dict


class OpenRouterService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openai/gpt-oss-20b:free"
        self.timeout = 60.0

    async def _call_api(self, messages: List[Dict]) -> str:
        """Make API call to OpenRouter"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate_intro_quiz(self, meeting_name: str, meeting_description: str) -> Dict:
        """Generate intro quiz based on meeting name and description"""
        prompt = f"""You are creating a pre-meeting quiz to prepare participants.

Meeting Name: {meeting_name}
Meeting Description: {meeting_description}

Create exactly 5 multiple-choice questions that will help participants prepare for this meeting.
Each question should have exactly 4 answer options.

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{
  "questions": [
    {{
      "question_text": "What is...",
      "correct_answer_index": 0,
      "answers": ["Answer 1", "Answer 2", "Answer 3", "Answer 4"]
    }}
  ]
}}

Make questions relevant, educational, and varied in difficulty."""

        messages = [{"role": "user", "content": prompt}]
        response = await self._call_api(messages)

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response: {e}\nResponse: {response}")

    async def generate_summary_from_transcripts(
            self,
            meeting_name: str,
            meeting_description: str,
            transcripts: List[Dict]
    ) -> str:
        """Generate meeting summary from transcripts"""
        # Format transcripts for the prompt
        transcript_text = "\n".join([
            f"[{t['timestamp']}] {t['user_username']}: {t['transcription_text']}"
            for t in transcripts
        ])

        prompt = f"""You are creating a comprehensive summary of a meeting.

Meeting Name: {meeting_name}
Meeting Description: {meeting_description}

Meeting Transcripts:
{transcript_text}

Based on the transcripts above, create a concise summary with 5-7 bullet points covering the main topics discussed, key decisions made, and important takeaways.

Return ONLY the bullet points in this format (no JSON, just plain text):
• First main point
• Second main point
• Third main point
• Fourth main point
• Fifth main point
• Sixth main point (if applicable)
• Seventh main point (if applicable)

Focus on the most important information from the actual discussion."""

        messages = [{"role": "user", "content": prompt}]
        response = await self._call_api(messages)

        return response.strip()

    async def generate_outro_quiz_from_summary(
            self,
            meeting_name: str,
            meeting_description: str,
            summary_points: str
    ) -> Dict:
        """Generate outro quiz based on meeting summary"""
        prompt = f"""You are creating a post-meeting quiz to test participant understanding.

Meeting Name: {meeting_name}
Meeting Description: {meeting_description}

Meeting Summary:
{summary_points}

Based on the summary above, create exactly 5 multiple-choice questions that test understanding of what was discussed in the meeting.
Each question should have exactly 4 answer options.

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{
  "questions": [
    {{
      "question_text": "What was discussed about...",
      "correct_answer_index": 0,
      "answers": ["Answer 1", "Answer 2", "Answer 3", "Answer 4"]
    }}
  ]
}}

Make questions specific to the actual content discussed in the meeting."""

        messages = [{"role": "user", "content": prompt}]
        response = await self._call_api(messages)

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response: {e}\nResponse: {response}")

    async def generate_user_performance_evaluation(
            self,
            username: str,
            meeting_name: str,
            meeting_description: str,
            user_transcripts: List[Dict],
            foul_count: int,
            total_transcripts: int,
            quiz_percentage: float
    ) -> Dict:
        """Generate user performance evaluation based on meeting participation"""
        # Format user's transcripts
        transcript_text = "\n".join([
            f"[{t['timestamp']}] {t['transcription_text']}"
            for t in user_transcripts
        ])

        prompt = f"""You are evaluating a participant's performance in a meeting.

Meeting Name: {meeting_name}
Meeting Description: {meeting_description}

Participant: {username}
Number of contributions: {total_transcripts}
Off-topic contributions (fouls): {foul_count}
Quiz score: {quiz_percentage:.1f}%

Participant's contributions:
{transcript_text}

Based on the participant's contributions, evaluate their performance:

1. Analyze the quality and relevance of their contributions
2. Consider their engagement level (number of contributions)
3. Factor in off-topic speech (fouls are negative)
4. Assess their understanding (quiz performance)

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{
  "strengths": "Brief description of participant's strengths (2-3 sentences)",
  "weaknesses": "Brief description of areas for improvement (2-3 sentences)",
  "tips": "Actionable advice for future meetings (2-3 specific tips)",
  "participation_score": 15,
  "quality_score": 40
}}

Scoring guidelines:
- participation_score (0-20): Based on engagement quantity and distribution
  * 0-5: Minimal participation
  * 6-12: Moderate participation
  * 13-17: Good participation
  * 18-20: Excellent participation
  
- quality_score (0-50): Based on contribution relevance and value
  * 0-15: Poor quality, many fouls, off-topic
  * 16-30: Basic quality, some relevant points
  * 31-40: Good quality, mostly relevant and valuable
  * 41-50: Excellent quality, highly relevant and insightful
  
Penalize fouls heavily in quality_score. Each foul should reduce quality significantly."""

        messages = [{"role": "user", "content": prompt}]
        response = await self._call_api(messages)

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            result = json.loads(cleaned)
            
            # Validate scores are within range
            if not (0 <= result["participation_score"] <= 20):
                result["participation_score"] = max(0, min(20, result["participation_score"]))
            if not (0 <= result["quality_score"] <= 50):
                result["quality_score"] = max(0, min(50, result["quality_score"]))
            
            return result
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response: {e}\nResponse: {response}")
        except KeyError as e:
            raise ValueError(f"Missing required field in AI response: {e}\nResponse: {response}")