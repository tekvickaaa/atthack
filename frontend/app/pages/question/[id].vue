<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const meetingId = route.params.id
const quizType = route.query.type as string // 'intro' or 'outro'

const loading = ref(true)
const error = ref<string | null>(null)
const quizData = ref<any>(null)
const currentQuestionIndex = ref(0)
const selectedAnswer = ref<number | null>(null)
const answers = ref<Record<number, number>>({}) // questionId -> answerIndex
const submitting = ref(false)

const currentQuestion = computed(() => {
  if (!quizData.value || !quizData.value.questions) return null
  return quizData.value.questions[currentQuestionIndex.value]
})

const isLastQuestion = computed(() => {
  if (!quizData.value || !quizData.value.questions) return false
  return currentQuestionIndex.value === quizData.value.questions.length - 1
})

const progress = computed(() => {
  if (!quizData.value || !quizData.value.questions) return 0
  return ((currentQuestionIndex.value + 1) / quizData.value.questions.length) * 100
})

const fetchQuiz = async () => {
  loading.value = true
  error.value = null
  try {
    const endpoint = quizType === 'intro' ? 'intro-quiz' : 'outro-quiz'
    const response = await fetch(`/api/meeting/${meetingId}/${endpoint}`)
    
    if (!response.ok) {
      throw new Error('Failed to fetch quiz')
    }
    
    const data = await response.json()
    quizData.value = data
    
    // Initialize from query param if present
    const qN = parseInt(route.query.qN as string) || 1
    if (qN > 0 && data.questions && qN <= data.questions.length) {
      currentQuestionIndex.value = qN - 1
    }
    
  } catch (err: any) {
    error.value = err.message || 'Error loading quiz'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleNext = () => {
  if (selectedAnswer.value === null || !currentQuestion.value) return
  
  // Save answer
  answers.value[currentQuestion.value.id] = selectedAnswer.value
  
  if (isLastQuestion.value) {
    submitQuiz()
  } else {
    currentQuestionIndex.value++
    selectedAnswer.value = null
    // Update URL without reloading
    router.push({ 
      query: { ...route.query, qN: currentQuestionIndex.value + 1 } 
    })
  }
}

const submitQuiz = async () => {
  if (!quizData.value) return
  
  submitting.value = true
  try {
    const payload = {
      user_username: 'alice', // Hardcoded for now as per other parts
      answers: Object.entries(answers.value).map(([qId, aIdx]) => ({
        question_id: parseInt(qId),
        selected_answer_index: aIdx
      }))
    }
    
    const response = await fetch(`/api/quiz/${quizData.value.id}/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    
    if (!response.ok) {
      throw new Error('Failed to submit quiz')
    }
    
    const result = await response.json()
    console.log('Quiz result:', result)
    
    // Redirect to meetings page or summary
    router.push('/meetings')
    
  } catch (err: any) {
    error.value = err.message || 'Error submitting quiz'
    console.error(err)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchQuiz()
})
</script>

<template>
  <UContainer>
    <div class="px-48 pt-6 flex flex-col gap-5">
      <div v-if="loading" class="text-center py-10">
        <p>Načítavam kvíz...</p>
      </div>
      
      <div v-else-if="error" class="text-center py-10 text-red-500">
        <p>Chyba: {{ error }}</p>
        <UButton label="Späť na zoznam" to="/meetings" class="mt-4" />
      </div>
      
      <div v-else-if="quizData && currentQuestion" class="flex flex-col gap-6">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold">
            {{ quizType === 'intro' ? 'Vstupný dotazník' : 'Záverečný dotazník' }}
          </h1>
          <span class="text-gray-500">
            Otázka {{ currentQuestionIndex + 1 }} z {{ quizData.questions.length }}
          </span>
        </div>
        
        <UProgress :value="progress" />
        
        <div class="rounded-2xl border border-gray-200 dark:border-gray-800 p-6 flex flex-col gap-6 bg-white dark:bg-gray-900">
          <h2 class="text-xl font-medium dark:text-white">
            {{ currentQuestion.question_text }}
          </h2>
          
          <div class="flex flex-col gap-3">
            <div 
              v-for="(answer, index) in currentQuestion.answers" 
              :key="answer.id"
              class="flex items-center p-3 rounded-lg border cursor-pointer transition-colors"
              :class="selectedAnswer === index ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800'"
              @click="selectedAnswer = index"
            >
              <div class="w-5 h-5 rounded-full border flex items-center justify-center mr-3"
                :class="selectedAnswer === index ? 'border-primary-500' : 'border-gray-300 dark:border-gray-600'"
              >
                <div v-if="selectedAnswer === index" class="w-2.5 h-2.5 rounded-full bg-primary-500"></div>
              </div>
              <span class="dark:text-gray-200">{{ answer.answer_text }}</span>
            </div>
          </div>
          
          <div class="flex justify-end mt-4">
            <UButton 
              :label="isLastQuestion ? 'Odoslať' : 'Ďalej'" 
              size="lg"
              :loading="submitting"
              :disabled="selectedAnswer === null"
              @click="handleNext"
            />
          </div>
        </div>
      </div>
    </div>
  </UContainer>
</template>