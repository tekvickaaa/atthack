# Discord Transcriber & Meeting Assistant

A comprehensive tool that records Discord voice channels, transcribes audio using Gemini AI, and provides a web dashboard for meeting summaries, quizzes, and analytics.

## 🛠 Tech Stack

## ADD the bot to your server:
- [Click here for bot invite to your Discord server](https://discord.com/oauth2/authorize?client_id=1441076928273715354&permissions=8&integration_type=0&scope=bot)
- Here you can add hosted discord bot which will work out of the box without hosting

### Discord Commands
- `!transcribe "Meeting Name" "Meeting Description"` - Starts recording and transcribing a meeting. (You need to be in voice channel)
  - Example: `!transcribe "Team Standup" "Daily standup meeting for the dev team"`
- `!stop` - Stops the recording, saves the transcript, and generates a summary.

### Frontend
- **Framework:** Nuxt 4 (Vue 3)
- **UI Library:** Nuxt UI, TailwindCSS
- **Graphics:** PixiJS
- **State Management:** Vue Composables

### Backend (API)
- **Language:** Python
- **Framework:** FastAPI
- **Database:** SQLAlchemy (SQLite/PostgreSQL)
- **Validation:** Pydantic
- **AI Integration:** Google Gemini API, OpenRouter

### Discord Bot
- **Runtime:** Node.js / TypeScript
- **Library:** Discord.js, @discordjs/voice
- **Audio Processing:** @ricky0123/vad-node (Voice Activity Detection), Prism Media
- **AI:** Google Generative AI (Gemini)



### AI Models
- **Transcription:** Gemini 2.0 Flash (Google Generative AI)
- **Relevancy Check:** GPT-OSS 20B (via OpenRouter)
- **Quiz Generation:** GPT-OSS 20B (via OpenRouter)

## 🚀 Getting Started

### Prerequisites
- Node.js (v20+ recommended)
- Python (v3.10+)
- pnpm or npm
- FFmpeg (required for audio processing)

### 1. Installation

**Root Directory (Bot):**
```bash
npm install
```

**Frontend Directory:**
```bash
cd frontend
npm install
cd ..
```

### 2. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token

# AI Configuration
GEMINI_API_KEY=your_google_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# API Configuration
API_URL=http://localhost:8000
```

## 🏃‍♂️ Running the Project

You need to run two separate processes to get the application working.

### 1. Start the Discord Bot
This connects to Discord, handles voice recording, and communicates with the backend.
```bash
# From the root directory
npm run dev
```

### 2. Start the Frontend Dashboard
This provides the user interface for viewing summaries and quizzes.
```bash
# From the frontend directory
cd frontend
npm run dev
```
*Frontend will run on http://localhost:3000*

## 📝 Features
- **Real-time Transcription:** Transcribes voice chat using Gemini AI.
- **Meeting Summaries:** Automatically generates summaries of meetings.
- **Quizzes:** Generates quizzes based on meeting content to test understanding.
- **Dashboard:** View meeting history, transcripts, and analytics.
