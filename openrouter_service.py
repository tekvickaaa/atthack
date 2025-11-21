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