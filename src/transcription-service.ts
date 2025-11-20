import { EndBehaviorType, VoiceConnection } from "@discordjs/voice";
import type { TextBasedChannel } from "discord.js";
import config from "./config.ts";
import logger from "./logger.ts";
import { UserAudioStream } from "./user-audio-stream.ts";
import { TTSService } from "./tts-service.ts";

export class TranscriptionService {
  private activeStreams: Map<string, UserAudioStream> = new Map();
  private transcriptionChannels: Map<string, TextBasedChannel> = new Map();

  constructor() {}

  createTranscriptionStream(
    connection: VoiceConnection,
    textChannel: TextBasedChannel,
    meetingName: string,
    meetingDescription: string,
    ttsService: TTSService
  ) {
    const receiver = connection.receiver;

    // Create a subscription ID to track this transcription session
    const subscriptionId = Date.now().toString();

    // Store the text channel for sending transcriptions
    this.transcriptionChannels.set(subscriptionId, textChannel);

    // Get guild ID and channel ID
    const guildId = "guildId" in textChannel ? textChannel.guildId || "DM" : "DM";
    const channelId = textChannel.id;

    // Track active users to avoid duplicate subscriptions
    const activeUsers = new Set<string>();

    // Set up audio receiving
    receiver.speaking.on("start", async (userId) => {
      logger.debug(`User ${userId} started speaking`);

      // Skip if we already have an active stream for this user
      const streamKey = `${subscriptionId}_${userId}`;
      if (activeUsers.has(userId)) {
        return;
      }

      // Mark user as active
      activeUsers.add(userId);

      // Get username from Discord client
      let username = "Unknown User";
      try {
        // Get the guild from the voice connection to fetch member info
        if ("guild" in textChannel && textChannel.guild) {
          const member = await textChannel.guild.members.fetch(userId);
          username = member.user.username;
        }
      } catch (error) {
        logger.error(`Error fetching username for user ${userId}:`, error);
      }

      // Create audio subscription
      const audioStream = receiver.subscribe(userId, {
        end: {
          behavior: EndBehaviorType.AfterSilence,
          duration: 2000,
        },
      });

      // Create a new audio stream processor
      const userStream = new UserAudioStream(
        userId,
        streamKey,
        textChannel,
        audioStream,
        () => {
          // Cleanup function
          this.activeStreams.delete(streamKey);
          activeUsers.delete(userId);
        },
        username,
        guildId,
        channelId,
        meetingName,
        meetingDescription,
        ttsService,
        connection
      );

      // Store the stream processor
      this.activeStreams.set(streamKey, userStream);
    });

    return subscriptionId;
  }

  stopTranscription(subscriptionId: string) {
    // Close all active streams for this subscription
    for (const [key, stream] of this.activeStreams.entries()) {
      if (key.startsWith(`${subscriptionId}_`)) {
        stream.destroy();
        this.activeStreams.delete(key);
      }
    }

    // Clean up the channel reference
    this.transcriptionChannels.delete(subscriptionId);
  }
}