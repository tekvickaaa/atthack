<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()

const meetingId = route.params.meetingId
</script>

<template>
  <UContainer>
    <div class="px-48 pt-6 flex flex-col gap-5">
      <h1 class="text-3xl font-bold ">
        Summary of meeting {{ meetingId }}
      </h1>
      <div class="rounded-2xl border border-gray-200 pt-5 h-full overflow-hidden flex flex-col gap-5">
        <p>
          This is the summary page for meeting with ID: {{ meetingId }}.
        </p>
      </div>
    </div>
  </UContainer>

</template>
