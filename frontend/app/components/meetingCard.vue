<script setup lang="ts">

const props = defineProps<{
  meetingId: string
  meetingTitle: string
  meetingDescription: string
  meetingDetails: string[]
  buttonAction: "Intro" | "Outro" | "Sum"
}>()

</script>

<template>
  <div class="flex gap-5 items-start px-5 pb-5 border-b border-gray-200">
    <div class="flex flex-col w-full gap-1">
      <h2 class="font-bold text-xl ">
        {{ props.meetingTitle }}
      </h2>
      <p>
        {{ props.meetingDescription }}
      </p>
      <div class="flex gap-3">
        <p v-for="(detail, index) in props.meetingDetails" :key="index" class="text-sm">
          {{ detail }}
        </p>
      </div>
    </div>
    <UButton
        :label="props.buttonAction == 'Intro' ? 'Vyplniť vstupný dotazník' : props.buttonAction == 'Outro' ? 'Vyplniť zaverečný dotazník' : 'Prezrieť zhrnutie'"
        size="md"
        :to="props.buttonAction == 'Intro' ? `/question/${props.meetingId}?type='intro'&qN='1'` : props.buttonAction == 'Outro' ? `/question/${props.meetingId}?type='outro'&qN='1'` : `/summary/${props.meetingId}`"
    />
  </div>
</template>