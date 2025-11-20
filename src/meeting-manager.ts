import type { TranscriptEntry } from "./transcript-store.ts";

interface Meeting {
  meetingId: string;
  name: string;
  description: string;
  guildId: string;
  createdAt: Date;
}

class MeetingManager {
  private meetings: Meeting[] = [];

  /**
   * Add a new meeting to the array
   */
  addMeeting(name: string, description: string, guildId: string): Meeting {
    const meeting: Meeting = {
      meetingId: "", // Will be filled when connected to server
      name,
      description,
      guildId,
      createdAt: new Date(),
    };

    this.meetings.push(meeting);
    return meeting;
  }

  /**
   * Get all meetings for a specific guild
   */
  getMeetingsByGuild(guildId: string): Meeting[] {
    return this.meetings.filter(m => m.guildId === guildId);
  }

  /**
   * Get a specific meeting by index
   */
  getMeeting(index: number): Meeting | undefined {
    return this.meetings[index];
  }

  /**
   * Update meeting ID when connected to server
   */
  async updateMeetingIdFromServer(meeting: Meeting): Promise<void> {
    try {
      console.log(`[Server] Sending meeting to server:`, {
        name: meeting.name,
        description: meeting.description,
      });

      const response = await fetch("http://13.60.191.32:8000/meeting", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: meeting.name,
          description: meeting.description,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const data = await response.json() as { id: number, name: string };
      
      if (data && data.id !== undefined) {
        meeting.meetingId = data.id.toString();
        console.log(`[Server] Received meeting ID: ${meeting.meetingId}`);
      } else {
        console.error("[Server] Invalid response format:", data);
        meeting.meetingId = `TEMP_${Date.now()}`;
      }
    } catch (error) {
      console.error("[Server] Error creating meeting:", error);
      // Fallback to temp ID if server request fails
      meeting.meetingId = `TEMP_${Date.now()}`;
    }
  }

  /**
   * Send transcripts to server
   */
  async sendTranscriptsToServer(meetingId: string, transcripts: TranscriptEntry[]): Promise<void> {
    // Skip if meeting ID is temporary (not from server)
    if (meetingId.startsWith("TEMP_")) {
      console.log(`[Server] Skipping transcript upload for temporary meeting ID: ${meetingId}`);
      return;
    }

    try {
      console.log(`[Server] Sending ${transcripts.length} transcripts for meeting ${meetingId}`);

      const response = await fetch(`http://13.60.191.32:8000/meeting/${meetingId}/transcripts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(transcripts.map(t => ({
          userId: t.userId,
          username: t.username,
          transcription: t.transcription,
          timestamp: t.timestamp.toISOString(),
          guildId: t.guildId,
          channelId: t.channelId
        }))),
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      console.log(`[Server] Transcripts sent successfully`);
    } catch (error) {
      console.error("[Server] Error sending transcripts:", error);
    }
  }

  /**
   * Get all meetings
   */
  getAllMeetings(): Meeting[] {
    return this.meetings;
  }

  /**
   * Clear all meetings for a guild
   */
  clearMeetingsByGuild(guildId: string): void {
    this.meetings = this.meetings.filter(m => m.guildId !== guildId);
  }

  /**
   * Clear all meetings
   */
  clearAllMeetings(): void {
    this.meetings = [];
  }
}

// Export singleton instance
export const meetingManager = new MeetingManager();
export type { Meeting };
