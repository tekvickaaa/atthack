import { GoogleGenerativeAI } from "@google/generative-ai";
import type { Message, TextBasedChannel } from "discord.js";
import { VoiceConnection, createAudioPlayer } from "@discordjs/voice";
import { Buffer } from "node:buffer";
import config from "./config.ts";
import logger from "./logger.ts";
import { transcriptStore } from "./transcript-store.ts";
import { TTSService } from "./tts-service.ts";

// Initialize Gemini API
const genAI = new GoogleGenerativeAI(config.GEMINI_API_KEY);

/**
 * Class to handle a single speech utterance
 * - Creates and manages Discord message
 * - Collects audio chunks
 * - Processes transcription on finalize
 * - Supports streaming real-time transcription
 */
export class Utterance {
  private chunks: Buffer[] = [];
  private discordMessage: Message | null = null;
  private startTime = Date.now();
  private isFinalized = false;

  constructor(
    private userId: string,
    private textChannel: TextBasedChannel,
    private username: string,
    private guildId: string,
    private channelId: string,
    private meetingName: string,
    private meetingDescription: string,
    private ttsService: TTSService,
    private connection: VoiceConnection
  ) {
    this.createPlaceholderMessage();
  }

  /**
   * Create the initial Discord message
   */
  private async createPlaceholderMessage() {
    if ("send" in this.textChannel) {
      try {
        this.discordMessage = await this.textChannel.send(
          `<@${this.userId}>: *Listening...*`
        );
        logger.info(`Created placeholder message for user ${this.userId}`);
      } catch (error) {
        logger.error("Error creating placeholder message:", error);
      }
    }
  }

  /**
   * Add audio data to this utterance
   */
  public addAudioData(data: Buffer) {
    if (!this.isFinalized) {
      this.chunks.push(data);
    }
  }



  /**
   * Finalize the utterance and perform transcription
   */
  public async finalize() {
    if (this.isFinalized) return;
    this.isFinalized = true;

    // Update message to show it's processing
    if (this.discordMessage && this.chunks.length > 0) {
      try {
        await this.discordMessage.edit(`<@${this.userId}>: *Transcribing...*`);
      } catch (error) {
        logger.error("Error updating message to processing status:", error);
      }
    }

    if (this.chunks.length === 0) {
      // No audio data collected
      this.updateMessageNoSpeech();
      return;
    }

    // Process audio data
    try {
      // Combine all chunks
      const pcmBuffer = Buffer.concat(this.chunks);

      // Convert to mono 16kHz for processing
      const monoBuffer = this.convertToMono16k(pcmBuffer);

      // Add WAV header
      const wavBuffer = this.addWavHeader(monoBuffer, 16000, 1);

      // Convert to base64
      const base64Audio = wavBuffer.toString("base64");

      // Get Gemini model and transcribe
      const model = genAI.getGenerativeModel({
        model: "gemini-2.0-flash",
      });

      // Transcribe audio
      const result = await model.generateContent([
        {
          inlineData: {
            mimeType: "audio/wav",
            data: base64Audio,
          },
        },
        {
          text: 'Please transcribe any speech in this audio. If there is no clear speech, respond with "No speech detected".',
        },
      ]);

      const transcription = result.response.text();

      // Update the Discord message with the transcription
      await this.updateMessageWithTranscription(transcription);
    } catch (error) {
      logger.error("Error transcribing audio:", error);
      this.updateMessageError();
    }
  }

  /**
   * Update message when no speech is detected - delete the message
   */
  private async updateMessageNoSpeech() {
    if (this.discordMessage) {
      try {
        // Delete the message instead of showing "No speech detected"
        await this.discordMessage.delete();
        logger.debug(
          `Deleted message for user ${this.userId} (no speech detected)`
        );
      } catch (error) {
        logger.error("Error deleting no-speech message:", error);
      }
    }
  }

  /**
   * Update message on error
   */
  private async updateMessageError() {
    if (this.discordMessage) {
      try {
        await this.discordMessage.edit(
          `<@${this.userId}>: *Error transcribing audio*`
        );
      } catch (error) {
        logger.error("Error updating error message:", error);
      }
    }
  }

  /**
   * Check if the transcription is relevant to the meeting
   */
  private async checkRelevancy(currentTranscript: string): Promise<{ relevant: boolean; chatWarning?: string; warning?: string }> {
    if (!config.OPENROUTER_API_KEY) {
      return { relevant: true };
    }

    try {
      // Get past context (last 10 messages)
      const pastTranscripts = transcriptStore
        .getTranscriptsByGuild(this.guildId)
        .slice(-10)
        .map((t) => `${t.username}: ${t.transcription}`)
        .join("\n");

      const prompt = `
You are a meeting assistant.
Meeting Name: ${this.meetingName}
Meeting Description: ${this.meetingDescription}

Past Context:
${pastTranscripts}

Current Speech (by ${this.username}):
${currentTranscript}

Is the current speech relevant to the meeting topic and context?
If it is NOT relevant, provide a short warning message to be spoken to the user.
IMPORTANT: The warning message MUST be in the same language as the Meeting Description.
IMPORTANT: The warning message MUST address the user by name (${this.username}).
IMPORTANT: The chat warning MUST be in the same language as the Meeting Description.
Reply with JSON only: {"relevant": boolean, "chatWarning": "short warning text for chat in the appropriate language (e.g. '⚠️ Irrelevant: reason')", "warning": "warning message in the appropriate language addressing the user for TTS"}
`;

      const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${config.OPENROUTER_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: config.OPENROUTER_MODEL,
          messages: [
            {
              role: "system",
              content: "You are a helpful assistant that checks if a speech is relevant to a meeting. You must respond with valid JSON.",
            },
            { role: "user", content: prompt },
          ],
        }),
      });

      if (!response.ok) {
        logger.error(`OpenRouter API error: ${response.statusText}`);
        return { relevant: true };
      }

      const data = await response.json() as any;
      const content = data.choices[0]?.message?.content;
      
      if (!content) return { relevant: true };

      // Extract JSON from markdown code block if present
      const jsonMatch = content.match(/```json\n([\s\S]*?)\n```/) || content.match(/\{[\s\S]*\}/);
      const jsonStr = jsonMatch ? jsonMatch[0].replace(/```json|```/g, "") : content;

      const result = JSON.parse(jsonStr);
      return {
        relevant: result.relevant,
        chatWarning: result.chatWarning,
        warning: result.warning
      };
    } catch (error) {
      logger.error("Error checking relevancy:", error);
      return { relevant: true };
    }
  }

  /**
   * Update message with transcription
   */
  private async updateMessageWithTranscription(transcription: string) {
    if (this.discordMessage) {
      try {
        if (
          transcription &&
          transcription.trim() !== "No speech detected" &&
          transcription.trim() !== "No speech detected."
        ) {
          const trimmedTranscription = transcription.trim();
          
          // Check relevancy
          const relevancy = await this.checkRelevancy(trimmedTranscription);
          
          let messageContent = `<@${this.userId}>: ${trimmedTranscription}`;
          
          if (!relevancy.relevant) {
            const chatWarning = relevancy.chatWarning || "⚠️ **Irrelevant:** Off-topic";
            messageContent += `\n${chatWarning}`;
            
            // Play TTS warning
            try {
              const warningText = relevancy.warning || `${this.username}, that comment was irrelevant.`;
              const audioResource = await this.ttsService.generateAudioResource(warningText);
              const player = createAudioPlayer();
              player.play(audioResource);
              this.connection.subscribe(player);
            } catch (ttsError) {
              logger.error("Error playing TTS warning:", ttsError);
            }
          }

          await this.discordMessage.edit(messageContent);
          
          // Save transcript to store
          transcriptStore.addTranscript({
            userId: this.userId,
            username: this.username,
            transcription: trimmedTranscription,
            timestamp: new Date(),
            guildId: this.guildId,
            channelId: this.channelId,
          });
          
          logger.debug(`Saved transcript for user ${this.userId}`);
        } else {
          // Delete the message instead of showing "No speech detected"
          await this.discordMessage.delete();
          logger.debug(
            `Deleted message for user ${this.userId} (empty transcription)`
          );
        }
      } catch (error) {
        logger.error("Error updating transcription message:", error);
      }
    }
  }

  /**
   * Converts 48kHz stereo PCM to 16kHz mono PCM
   */
  private convertToMono16k(buffer: Buffer): Buffer {
    // Parameters
    const inputSampleRate = 48000;
    const outputSampleRate = 16000;
    const ratio = inputSampleRate / outputSampleRate;
    const inputChannels = 2; // Stereo
    const bytesPerSample = 2; // 16-bit

    // Calculate output buffer size
    const inputSamples = buffer.length / (bytesPerSample * inputChannels);
    const outputSamples = Math.floor(inputSamples / ratio);
    const outputBuffer = Buffer.alloc(outputSamples * bytesPerSample);

    // Process each output sample
    for (let i = 0; i < outputSamples; i++) {
      // Find the corresponding input sample
      const inputIndex = Math.floor(i * ratio) * inputChannels * bytesPerSample;

      // Average the left and right channels for mono conversion
      if (inputIndex + 3 < buffer.length) {
        const leftSample = buffer.readInt16LE(inputIndex);
        const rightSample = buffer.readInt16LE(inputIndex + 2);
        const monoSample = Math.round((leftSample + rightSample) / 2);

        // Write to output buffer
        outputBuffer.writeInt16LE(monoSample, i * bytesPerSample);
      }
    }

    return outputBuffer;
  }

  /**
   * Adds a WAV header to PCM audio data
   */
  private addWavHeader(
    pcmData: Buffer,
    sampleRate: number,
    numChannels: number
  ): Buffer {
    const byteRate = sampleRate * numChannels * 2; // 2 bytes per sample
    const blockAlign = numChannels * 2;
    const dataSize = pcmData.length;
    const buffer = Buffer.alloc(44 + pcmData.length);

    // RIFF identifier
    buffer.write("RIFF", 0);
    // File size
    buffer.writeUInt32LE(36 + dataSize, 4);
    // RIFF type
    buffer.write("WAVE", 8);
    // Format chunk identifier
    buffer.write("fmt ", 12);
    // Format chunk length
    buffer.writeUInt32LE(16, 16);
    // Sample format (PCM)
    buffer.writeUInt16LE(1, 20);
    // Channel count
    buffer.writeUInt16LE(numChannels, 22);
    // Sample rate
    buffer.writeUInt32LE(sampleRate, 24);
    // Byte rate (SampleRate * NumChannels * BitsPerSample/8)
    buffer.writeUInt32LE(byteRate, 28);
    // Block align (NumChannels * BitsPerSample/8)
    buffer.writeUInt16LE(blockAlign, 32);
    // Bits per sample
    buffer.writeUInt16LE(16, 34);
    // Data chunk identifier
    buffer.write("data", 36);
    // Data chunk length
    buffer.writeUInt32LE(dataSize, 40);

    // Copy audio data
    pcmData.copy(buffer, 44);

    return buffer;
  }
}
