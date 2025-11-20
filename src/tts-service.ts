import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createAudioResource, StreamType } from "@discordjs/voice";
import config from "./config.ts";
import { Readable } from "stream";

export class TTSService {
  private client: ElevenLabsClient;

  constructor() {
    if (!config.ELEVENLABS_API_KEY) {
      console.warn("ELEVENLABS_API_KEY is not set. TTS will not work.");
    }
    this.client = new ElevenLabsClient({
      apiKey: config.ELEVENLABS_API_KEY,
    });
  }

  async generateAudioResource(text: string) {
    try {
      const audioStream = await this.client.textToSpeech.convert(
        config.ELEVENLABS_VOICE_ID,
        {
          text,
          modelId: "eleven_turbo_v2_5", 
          outputFormat: "mp3_44100_128",
        }

      );

      return createAudioResource(audioStream as unknown as Readable, {
        inputType: StreamType.Arbitrary,
      });
    } catch (error) {
      console.error("Error generating TTS:", error);
      throw error;
    }
  }
}
