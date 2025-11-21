/**
 * Transcript storage and management
 */

export interface TranscriptEntry {
  userId: string;
  username: string;
  transcription: string;
  timestamp: Date;
  guildId: string;
  channelId: string;
  foul?: boolean;
}

export class TranscriptStore {
  private transcripts: TranscriptEntry[] = [];

  /**
   * Add a new transcript entry
   */
  public addTranscript(entry: TranscriptEntry): void {
    this.transcripts.push(entry);
  }

  /**
   * Get all transcripts
   */
  public getAllTranscripts(): TranscriptEntry[] {
    return [...this.transcripts];
  }

  /**
   * Get transcripts for a specific guild
   */
  public getTranscriptsByGuild(guildId: string): TranscriptEntry[] {
    return this.transcripts.filter((t) => t.guildId === guildId);
  }

  /**
   * Get transcripts for a specific user
   */
  public getTranscriptsByUser(userId: string): TranscriptEntry[] {
    return this.transcripts.filter((t) => t.userId === userId);
  }

  /**
   * Get transcripts within a time range
   */
  public getTranscriptsByTimeRange(
    startTime: Date,
    endTime: Date
  ): TranscriptEntry[] {
    return this.transcripts.filter(
      (t) => t.timestamp >= startTime && t.timestamp <= endTime
    );
  }

  /**
   * Clear all transcripts
   */
  public clearTranscripts(): void {
    this.transcripts = [];
  }

  /**
   * Clear transcripts for a specific guild
   */
  public clearTranscriptsByGuild(guildId: string): void {
    this.transcripts = this.transcripts.filter((t) => t.guildId !== guildId);
  }

  /**
   * Get transcript count
   */
  public getTranscriptCount(): number {
    return this.transcripts.length;
  }

  /**
   * Export transcripts as JSON
   */
  public exportAsJSON(): string {
    return JSON.stringify(this.transcripts, null, 2);
  }

  /**
   * Get formatted transcript for display
   */
  public getFormattedTranscript(guildId?: string): string {
    const transcripts = guildId
      ? this.getTranscriptsByGuild(guildId)
      : this.getAllTranscripts();

    return transcripts
      .map(
        (t) =>
          `[${t.timestamp.toLocaleString()}] ${t.username}: ${t.transcription}`
      )
      .join("\n");
  }
}

// Global transcript store instance
export const transcriptStore = new TranscriptStore();
