<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ref, onMounted, computed } from 'vue'

interface SummaryData {
  summary_points: string[] | string
}

interface ScoreBreakdown {
  quiz_score: number
  participation_score: number
  quality_score: number
}

interface UserMeetingEvaluationResponse {
  meeting_id: number
  meeting_name: string
  username: string
  evaluation_score: number
  strengths: string
  weaknesses: string
  tips: string
  breakdown: ScoreBreakdown
  meetings_attended: number
  updated_user_score: number
  credits_earned: number
  evaluated_at: string
}

interface TeamMeetingEvaluationResponse {
  meeting_id: number
  meeting_name: string
  team_evaluation_score: number
  team_strengths: string
  team_weaknesses: string
  team_tips: string
  average_breakdown: ScoreBreakdown
  participant_count: number
  evaluated_at: string
}

const route = useRoute()

const meetingId = route.params.id
const data = ref<SummaryData | null>(null)
const personalEvaluation = ref<UserMeetingEvaluationResponse | null>(null)
const teamEvaluation = ref<TeamMeetingEvaluationResponse | null>(null)
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

const fetchPersonalEvaluation = async (id: string | number) => {
  try {
    const response = await fetch(`/api/meeting/${id}/evaluate/alice`, {
      headers: {
        'X-User-Username': 'alice'
      }
    })
    if (response.ok) {
      personalEvaluation.value = await response.json()
    } else {
      console.error('Failed to fetch personal evaluation')
    }
  } catch (err) {
    console.error('Error fetching personal evaluation:', err)
  }
}

const fetchTeamEvaluation = async (id: string | number) => {
  try {
    const response = await fetch(`/api/meeting/${id}/evaluate`, {
      headers: {
        'X-User-Username': 'alice'
      }
    })
    if (response.ok) {
      teamEvaluation.value = await response.json()
    } else {
      console.error('Failed to fetch team evaluation')
    }
  } catch (err) {
    console.error('Error fetching team evaluation:', err)
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
    
    await Promise.all([
      fetchSummary(id).then(res => data.value = res),
      fetchPersonalEvaluation(id),
      fetchTeamEvaluation(id)
    ])
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error fetching summary'
  } finally {
    loading.value = false
  }
})

</script>

<template>
  <UContainer>
    <div class="px-48 pt-6 flex flex-col gap-5 pb-10">
      <h1 class="text-3xl font-bold">
        Summary of meeting {{ meetingId }}
      </h1>
      
      <div class="rounded-2xl border border-gray-200 p-5 min-h-fit overflow-hidden flex flex-col gap-5">
        <h2 class="text-xl font-bold">Meeting Summary</h2>
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

      <!-- Personal Evaluation Section -->
      <div v-if="personalEvaluation" class="rounded-2xl border border-gray-200 p-5 min-h-fit overflow-hidden flex flex-col gap-5">
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-bold">Personal Evaluation</h2>
          <UBadge color="primary" size="lg">Score: {{ personalEvaluation.evaluation_score }}/100</UBadge>
        </div>
        
        <div class="grid grid-cols-3 gap-4">
          <div class="p-3 bg-gray-900 text-white rounded-lg text-center">
            <div class="text-sm text-gray-400">Quiz Score</div>
            <div class="text-xl font-bold">{{ personalEvaluation.breakdown.quiz_score }}</div>
          </div>
          <div class="p-3 bg-gray-900 text-white rounded-lg text-center">
            <div class="text-sm text-gray-400">Participation</div>
            <div class="text-xl font-bold">{{ personalEvaluation.breakdown.participation_score }}</div>
          </div>
          <div class="p-3 bg-gray-900 text-white rounded-lg text-center">
            <div class="text-sm text-gray-400">Quality</div>
            <div class="text-xl font-bold">{{ personalEvaluation.breakdown.quality_score }}</div>
          </div>
        </div>

        <div class="space-y-3">
          <div>
            <h3 class="font-semibold text-green-600">Strengths</h3>
            <p>{{ personalEvaluation.strengths }}</p>
          </div>
          <div>
            <h3 class="font-semibold text-red-600">Weaknesses</h3>
            <p>{{ personalEvaluation.weaknesses }}</p>
          </div>
          <div>
            <h3 class="font-semibold text-blue-600">Tips</h3>
            <p>{{ personalEvaluation.tips }}</p>
          </div>
        </div>
        
        <div class="flex gap-4 text-sm text-gray-500 mt-2">
          <span>Credits Earned: +{{ personalEvaluation.credits_earned }}</span>
          <span>Total Score: {{ personalEvaluation.updated_user_score }}</span>
        </div>
      </div>

      <!-- Team Evaluation Section -->
      <div v-if="teamEvaluation" class="rounded-2xl border border-gray-200 p-5 min-h-fit overflow-hidden flex flex-col gap-5">
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-bold">Team Evaluation</h2>
          <UBadge color="orange" size="lg">Team Score: {{ teamEvaluation.team_evaluation_score }}/100</UBadge>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div class="p-3 bg-gray-900 text-white rounded-lg text-center">
            <div class="text-sm text-gray-400">Quiz Score</div>
            <div class="text-xl font-bold">{{ teamEvaluation.average_breakdown.quiz_score }}</div>
          </div>
          <div class="p-3 bg-gray-900 text-white rounded-lg text-center">
            <div class="text-sm text-gray-400">Participation</div>
            <div class="text-xl font-bold">{{ teamEvaluation.average_breakdown.participation_score }}</div>
          </div>
          <div class="p-3 bg-gray-900 text-white rounded-lg text-center">
            <div class="text-sm text-gray-400">Quality</div>
            <div class="text-xl font-bold">{{ teamEvaluation.average_breakdown.quality_score }}</div>
          </div>
        </div>

        <div class="space-y-3">
          <div>
            <h3 class="font-semibold text-green-600">Team Strengths</h3>
            <p>{{ teamEvaluation.team_strengths }}</p>
          </div>
          <div>
            <h3 class="font-semibold text-red-600">Team Weaknesses</h3>
            <p>{{ teamEvaluation.team_weaknesses }}</p>
          </div>
          <div>
            <h3 class="font-semibold text-blue-600">Team Tips</h3>
            <p>{{ teamEvaluation.team_tips }}</p>
          </div>
        </div>
        
        <div class="text-sm text-gray-500 mt-2">
          <span>Participants Evaluated: {{ teamEvaluation.participant_count }}</span>
        </div>
      </div>

    </div>
  </UContainer>
</template>
