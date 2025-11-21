<script setup lang="ts">
import { ref, onMounted } from 'vue'

const data = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const fetchQuizForMeeting = async (meetingId: number, attempts: any[]): Promise<string> => {
  // 1. Check Intro Quiz
  try {
    const response = await fetch(`/api/meeting/${meetingId}/intro-quiz`)
    if (response.ok) {
      const introQuiz = await response.json()
      // Check if user has attempted this quiz
      const hasAttempted = attempts.some((a: any) => a.quiz_id === introQuiz.id)
      if (!hasAttempted) {
        return 'intro'
      }
    }
  } catch (err) {
    console.log('No intro quiz for meeting', meetingId)
  }

  // 2. Check Outro Quiz
  try {
    const response = await fetch(`/api/meeting/${meetingId}/outro-quiz`)
    if (response.ok) {
      const outroQuiz = await response.json()
      // Check if user has attempted this quiz
      const hasAttempted = attempts.some((a: any) => a.quiz_id === outroQuiz.id)
      if (!hasAttempted) {
        return 'outro'
      }
    }
  } catch (err) {
    console.log('No outro quiz for meeting', meetingId)
  }

  // 3. Check Summary
  try {
    const response = await fetch(`/api/meeting/${meetingId}/summary`)
    if (response.ok) {
      console.log('Fetched summary for meeting', meetingId)
      return 'sum'
    }
  } catch (err) {
    console.log('No summary for meeting', meetingId)
  }

  // If intro is done, outro is not available (or done), and summary is not available
  // We might want to return something else, but for now let's default to 'waiting' or null
  // But to keep existing behavior safe, if we can't determine, maybe 'intro'?
  // Actually, if intro is done, we shouldn't show it.
  return 'waiting' 
}

const fetchMeetings = async () => {
  loading.value = true
  error.value = null
  try {
    // Fetch user attempts first (assuming user is 'alice')
    const attemptsResponse = await fetch('/api/user/alice/quiz-attempts')
    let attempts: any[] = []
    if (attemptsResponse.ok) {
      attempts = await attemptsResponse.json()
    } else {
      console.error('Failed to fetch quiz attempts')
    }

    const response = await fetch('/api/meeting')
    if (!response.ok) throw new Error('Chyba fetchovania')

    const meetings = await response.json()
    console.log('Fetched meetings data:', meetings)

    if (!Array.isArray(meetings)) {
      throw new Error('Invalid response format')
    }

    // Для каждой встречи загружаем quiz_type
    const meetingsWithQuiz: any[] = []
    for (const meeting of meetings) {
      const quiz_type = await fetchQuizForMeeting(meeting.id, attempts)
      meetingsWithQuiz.push({
        id: meeting.id,
        name: meeting.name,
        description: meeting.description,
        temp_meeting_id: meeting.temp_meeting_id,
        summary: meeting.summary,
        begins_at: meeting.begins_at,
        duration: meeting.duration,
        created_at: meeting.created_at,
        owner_username: meeting.owner_username,
        quiz_type
      })
    }

    data.value = meetingsWithQuiz
    console.log('Meetings with quiz types:', meetingsWithQuiz)
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error'
    error.value = errorMessage
    console.error('Error fetching meetings:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMeetings()
})
</script>

<template>
  <UContainer>
    <div class="px-48 pt-6 flex flex-col gap-5">
      <h1 class="text-3xl font-bold">
        Meetings Page
      </h1>
      <div v-if="loading">Načítavam...</div>
      <div v-else-if="error">Chyba: {{ error }}</div>
      <div v-else-if="data && data.length > 0" class="rounded-2xl border border-gray-200 pt-5 h-full overflow-hidden flex flex-col gap-5">
        <MeetingCard
          v-for="meeting in data"
          :key="meeting.id"
          :id="meeting.id"
          :name="meeting.name"
          :description="meeting.description"
          :quiz_type="meeting.quiz_type"
        />
      </div>
      <div v-else class="text-gray-500">
        Žiadne stretnutia
      </div>
    </div>
  </UContainer>
</template>