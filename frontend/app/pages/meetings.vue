<script setup lang="ts">
interface fetchedMeetingProps {
  "id": number,
  "name": string,
  "description": string,
  "temp_meeting_id": null,
  "summary": string,
  "begins_at": string,
  "duration": string,
  "created_at": string,
  "owner_username": string
}

import { ref, onMounted } from 'vue'

const data = ref(null)
const loading = ref(false)
const error = ref(null)

const fetchMeetings = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await fetch('http://13.60.191.32:8000/meeting/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) throw new Error('Chyba fetchovania')
    data.value = await response.json()
  } catch (err: any) {
    error.value = err.message
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
      <h1 class="text-3xl font-bold ">
        Meetings Page
      </h1>
      <div v-if="loading">Načítavam...</div>
      <div v-else-if="error">Chyba: {{ error.message || 'Nepodarilo sa načítať dáta' }}</div>
      <div v-else-if="data && data.length > 0" class="rounded-2xl border border-gray-200 pt-5 h-full overflow-hidden flex flex-col gap-5">
        <MeetingCard
          v-for="meeting in data"
          :key="meeting.id"
          :meetingId="meeting.id"
          :meetingTitle="meeting.name"
          :meetingDescription="meeting.description"
        />
      </div>
      <div v-else class="text-gray-500">
        Žiadne stretnutia
      </div>
    </div>
  </UContainer>
</template>