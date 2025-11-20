export default {
  // Discord bot token
  DISCORD_TOKEN: process.env.DISCORD_TOKEN || "",

  // Gemini API key
  GEMINI_API_KEY: process.env.GEMINI_API_KEY || "",

  // OpenRouter API key
  OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY || "",

  // OpenRouter Model
  OPENROUTER_MODEL: process.env.OPENROUTER_MODEL || "google/gemini-2.0-flash-001",

  // Discord command prefix
  PREFIX: "!",

  // Command for starting transcription
  START_COMMAND: "transcribe",

  // Command for stopping transcription
  STOP_COMMAND: "stop",
  
  // Logging level (1=error, 2=warn, 3=log, 4=info, 5=debug)
  LOG_LEVEL: parseInt(process.env.LOG_LEVEL || "4", 10),
  
  // Voice detection settings
  ACTIVATION_THRESHOLD: 0.5,   // Confidence threshold to start utterance
  DEACTIVATION_THRESHOLD: 0.3, // Lower threshold to maintain active utterance
  SILENCE_DURATION: 1000,      // Allow 1 second of silence before ending speech

  // ElevenLabs settings
  ELEVENLABS_API_KEY: process.env.ELEVENLABS_API_KEY || "",
  ELEVENLABS_VOICE_ID: process.env.ELEVENLABS_VOICE_ID || "JBFqnCBsd6RMkjVDRZzb", // Default voice (George)
};
