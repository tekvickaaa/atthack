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
   * Placeholder for future server integration
   */
  async updateMeetingIdFromServer(meeting: Meeting): Promise<void> {
    // TODO: Implement server connection
    // This will send meeting data to server and receive meeting ID
    console.log(`[Placeholder] Would send meeting to server:`, {
      name: meeting.name,
      description: meeting.description,
    });
    
    // Simulate server response
    meeting.meetingId = `TEMP_${Date.now()}`;
    
    console.log(`[Placeholder] Received meeting ID: ${meeting.meetingId}`);
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
