<script setup lang="ts">
const props = defineProps<{
  badgeImage: string;
  badgeName: string;
  badgeCount: number;
}>();

</script>

<template>
  <div class="flex flex-col justify-center items-center gap-3 relative">
    <img
        :src="props.badgeImage"
        alt="Badge"
        class="rounded-full w-24 h-24"
    >
    <p>{{props.badgeName}}</p>
    <div class="p-1.5 flex justify-center text-md bg-gray-200 rounded-full absolute w-8 z-10 top-0 left-8 ">
      {{props.badgeCount}}
    </div>
  </div>
</template>

<style scoped>

</style>