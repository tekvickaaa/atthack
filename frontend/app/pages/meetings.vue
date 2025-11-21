<script setup lang="ts">
import { ref, onMounted } from 'vue'

const data = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const fetchQuizForMeeting = async (meetingId: number): Promise<string> => {
  try {
    const response = await fetch(`/api/meeting/${meetingId}/intro-quiz`)
    if (response.ok) {
      const jsonData = await response.json()
      console.log('Fetched intro quiz:', jsonData)
      return jsonData.quiz_type || 'intro'
    }
  } catch (err) {
    console.log('No intro quiz for meeting', meetingId)
  }

  try {
    const response = await fetch(`/api/meeting/${meetingId}/outro-quiz`)
    if (response.ok) {
      const jsonData = await response.json()
      console.log('Fetched outro quiz:', jsonData)
      return jsonData.quiz_type || 'outro'
    }
  } catch (err) {
    console.log('No outro quiz for meeting', meetingId)
  }

  try {
    const response = await fetch(`/api/meeting/${meetingId}/summary`)
    if (response.ok) {
      console.log('Fetched summary for meeting', meetingId)
      return 'sum'
    }
  } catch (err) {
    console.log('No summary for meeting', meetingId)
  }

  return 'intro'
}

const fetchMeetings = async () => {
  loading.value = true
  error.value = null
  try {
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
      const quiz_type = await fetchQuizForMeeting(meeting.id)
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