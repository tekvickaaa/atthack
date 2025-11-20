<script setup lang="ts">

</script>

<template>
  <UContainer>
    <div class="h-screen flex flex-col justify-center items-center gap-5">
      <div class="flex flex-col justify-center items-center gap-2 w-[870px]">
        <h1 class="font-bold text-5xl">Meetingy, ktoré konečne dávajú zmysel</h1>
        <p class="text-center">AI nástroj, ktorý premieňa meetingy na produktívnu hru. Sleduje fokus, odmeňuje badge-mi, ponúka questy, predpovedá priebeh a ukazuje reálny dopad meetingov. Viac rozhodnutí, menej času.</p>
      </div>
      <div class="flex gap-4">
        <UButton
            label="Otvoriť dashboard"
            size="xl"
            to="/dashboard"
        />
        <UButton
            label="Otvoriť preview pre manažérov"
            size="xl"
            variant="outline"
            to="/dashboard"
        />
      </div>
      </div>
  </UContainer>
</template>