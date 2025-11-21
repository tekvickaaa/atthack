<script setup lang="ts">

const props = defineProps<{
  "id"?: number,
  "name"?: string,
  "description"?: string,
  "temp_meeting_id"?: null,
  "summary"?: string,
  "begins_at"?: string,
  "duration"?: string,
  "created_at"?: string,
  "owner_username"?: string,
  "quiz_type"?: string
}>()

const getButtonLabel = () => {
  if (props.quiz_type === 'intro') return 'Vyplniť vstupný dotazník'
  if (props.quiz_type === 'outro') return 'Vyplniť záverečný dotazník'
  if (props.quiz_type === 'sum') return 'Prezrieť zhrnutie'
  return 'Vyplniť vstupný dotazník'
}

const getButtonLink = () => {
  if (props.quiz_type === 'intro') return `/question/${props.id}?type=intro&qN=1`
  if (props.quiz_type === 'outro') return `/question/${props.id}?type=outro&qN=1`
  if (props.quiz_type === 'sum') return `/summary/${props.id}`
  return `/question/${props.id}?type=intro&qN=1`
}

</script>

<template>
  <div class="flex gap-5 items-start px-5 pb-5 border-b border-gray-200">
    <div class="flex flex-col w-full gap-1">
      <h2 class="font-bold text-xl ">
        {{ props.name }}
      </h2>
      <p>
        {{ props.description }}
      </p>
    </div>
    <UButton
        :label="getButtonLabel()"
        size="md"
        :to="getButtonLink()"
    />
  </div>
</template>