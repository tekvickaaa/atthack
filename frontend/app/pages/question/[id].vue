<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()

const meetingId = route.params.meetingId
const questionNumber = route.query.questionNumber

type question = {
  id: number
  text: string
  answer: string[]
  correctAnswer: number
}



</script>

<template>
  <UContainer>
    <div class="px-48 pt-6 flex flex-col gap-5">
      <h1 class="text-3xl font-bold ">
        Meetings Page
      </h1>
      <div class="rounded-2xl border border-gray-200 pt-5 h-full overflow-hidden flex flex-col gap-5">
        <URadioGroup
          v-model="j"
          :options="[
            { label: 'Question 1', value: 1 },
            { label: 'Question 2', value: 2 },
            { label: 'Question 3', value: 3 },
          ]"
          class="px-5 pb-5 border-b border-gray-200"
        />
      </div>
    </div>
  </UContainer>
</template>