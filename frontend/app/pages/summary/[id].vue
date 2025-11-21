<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ref, onMounted, computed } from 'vue'

interface SummaryData {
  summary_points: string[] | string
}

const route = useRoute()

const meetingId = route.params.id
const data = ref<SummaryData | null>(null)
const loading = ref<boolean>(true)
const error = ref<string | null>(null)

const summaryPoints = computed(() => {
  if (!data.value?.summary_points) return []

  // Ak je to string, skúsime ho rozdeliť podľa nových riadkov
  if (typeof data.value.summary_points === 'string') {
    // Skúsime rozdeliť podľa nových riadkov
    const points = data.value.summary_points.split(/\n+/).filter(p => p.trim())
    if (points.length > 1) return points

    // Alebo vrátime celý text ako jeden bod
    return [data.value.summary_points]
  }

  // Ak je to pole, použijeme ho priamo
  return data.value.summary_points
})

const fetchSummary = async (id: string | number) => {
  try {
    console.log('Fetching summary for meeting ID:', id)
    const response = await fetch(`/api/meeting/${id}/summary`)
    console.log('Response status:', response.status)

    if (response.ok) {
      const jsonData = await response.json()
      console.log('Fetched summary data:', jsonData)
      return jsonData
    } else {
      const errorMsg = `Failed to fetch summary: ${response.status} ${response.statusText}`
      console.error(errorMsg)
      throw new Error(errorMsg)
    }
  } catch (err) {
    console.error('Error fetching summary:', err)
    throw err
  }
}

onMounted(async () => {
  console.log('Meeting ID from route:', meetingId)

  if (!meetingId) {
    error.value = 'Meeting ID not found'
    loading.value = false
    return
  }

  try {
    const id = (Array.isArray(meetingId) ? meetingId[0] : meetingId) as string
    if (!id) {
      throw new Error('Invalid meeting ID')
    }
    data.value = await fetchSummary(id)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error fetching summary'
  } finally {
    loading.value = false
  }
})

</script>

<template>
  <UContainer>
    <div class="px-48 pt-6 flex flex-col gap-5">
      <h1 class="text-3xl font-bold">
        Summary of meeting {{ meetingId }}
      </h1>
      <div class="rounded-2xl border border-gray-200 p-5 min-h-fit overflow-hidden flex flex-col gap-5">
        <div v-if="loading">
          Načítavam summary...
        </div>
        <div v-else-if="error" class="text-red-500">
          Chyba: {{ error }}
        </div>
        <div v-else-if="summaryPoints && summaryPoints.length > 0">
          <ul class="list-disc pl-5 space-y-2">
            <li v-for="(point, index) in summaryPoints" :key="index" class="text-base">
              {{ point }}
            </li>
          </ul>
        </div>
        <p v-else>
          No summary available.
        </p>
      </div>
    </div>
  </UContainer>
</template>
