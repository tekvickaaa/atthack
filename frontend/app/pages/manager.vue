<script setup lang="ts">

const teams = [
  {
    name: 'UX Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=ux&backgroundColor=6366f1',
    members: 8,
    credits: 12450,
    timeSaved: 156,
    decisionsPerHour: 0.87,
    offTopicFreeDays: 45
  },
  {
    name: 'Marketing Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=marketing&backgroundColor=ec4899',
    members: 6,
    credits: 10800,
    timeSaved: 132,
    decisionsPerHour: 0.72,
    offTopicFreeDays: 38
  },
  {
    name: 'Product Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=product&backgroundColor=8b5cf6',
    members: 7,
    credits: 11200,
    timeSaved: 145,
    decisionsPerHour: 0.81,
    offTopicFreeDays: 42
  },
  {
    name: 'Frontend Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=frontend&backgroundColor=3b82f6',
    members: 10,
    credits: 15600,
    timeSaved: 178,
    decisionsPerHour: 0.93,
    offTopicFreeDays: 52
  },
  {
    name: 'Sales Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=sales&backgroundColor=10b981',
    members: 5,
    credits: 8900,
    timeSaved: 98,
    decisionsPerHour: 0.65,
    offTopicFreeDays: 28
  },
  {
    name: 'HR Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=hr&backgroundColor=f59e0b',
    members: 4,
    credits: 7200,
    timeSaved: 87,
    decisionsPerHour: 0.58,
    offTopicFreeDays: 31
  },
  {
    name: 'Support Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=support&backgroundColor=14b8a6',
    members: 9,
    credits: 13400,
    timeSaved: 165,
    decisionsPerHour: 0.89,
    offTopicFreeDays: 47
  },
  {
    name: 'DevOps Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=devops&backgroundColor=6366f1',
    members: 6,
    credits: 10500,
    timeSaved: 128,
    decisionsPerHour: 0.76,
    offTopicFreeDays: 39
  },
  {
    name: 'QA Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=qa&backgroundColor=a855f7',
    members: 7,
    credits: 11800,
    timeSaved: 142,
    decisionsPerHour: 0.84,
    offTopicFreeDays: 43
  },
  {
    name: 'Backend Tím',
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=backend&backgroundColor=ef4444',
    members: 8,
    credits: 12300,
    timeSaved: 149,
    decisionsPerHour: 0.79,
    offTopicFreeDays: 41
  }
];

const selectedTeamIndex = ref(0);
const selectedTeam = computed(() => teams[selectedTeamIndex.value]!);

const teamBadges = computed(() => [
  {
    name: 'Topic Master',
    image: new URL('~/assets/images/dashboard/badges/TopicMaster.svg', import.meta.url).href,
    level: Math.floor(selectedTeam.value.members * 2.5)
  },
  {
    name: 'Facilitator',
    image: new URL('~/assets/images/dashboard/badges/Facilitator.svg', import.meta.url).href,
    level: Math.floor(selectedTeam.value.members * 3.2)
  },
  {
    name: 'Decision Maker',
    image: new URL('~/assets/images/dashboard/badges/DecisionMaker.svg', import.meta.url).href,
    level: Math.floor(selectedTeam.value.members * 2.8)
  },
  {
    name: 'Time Saver',
    image: new URL('~/assets/images/dashboard/badges/TimeSaver.svg', import.meta.url).href,
    level: Math.floor(selectedTeam.value.members * 2.1)
  },
  {
    name: 'Question Asker',
    image: new URL('~/assets/images/dashboard/badges/QuestionAsker.svg', import.meta.url).href,
    level: Math.floor(selectedTeam.value.members * 3.5)
  },
  {
    name: 'Insight Drop',
    image: new URL('~/assets/images/dashboard/badges/InsightDrop.svg', import.meta.url).href,
    level: Math.floor(selectedTeam.value.members * 1.8)
  }
]);

const companyStats = computed(() => ({
  totalTimeSaved: teams.reduce((sum, team) => sum + team.timeSaved, 0),
  averageDecisions: (teams.reduce((sum, team) => sum + team.decisionsPerHour, 0) / teams.length).toFixed(2),
  totalOffTopicFreeDays: teams.reduce((sum, team) => sum + team.offTopicFreeDays, 0)
}));

</script>

<template>
  <UContainer class="grid grid-cols-3 gap-5 pt-6">
    <!-- Ľavý stĺpec - Všeobecné štatistiky firmy -->
    <div class="flex flex-col gap-5 col-span-1">
      <div class="flex flex-col gap-4 rounded-2xl border border-gray-200 p-5">
        <h2 class="text-xl font-bold">Celková štatistika</h2>
      </div>

      <div class="flex flex-row gap-5 rounded-2xl border border-gray-200 p-5">
        <UIcon name="i-lucide-hourglass" size="64" />
        <div class="flex flex-col justify-center">
          <h3 class="font-bold text-2xl">
            {{ companyStats.totalTimeSaved }}h
          </h3>
          <p class="text-sm">celkový ušetrený čas</p>
        </div>
      </div>

      <div class="flex flex-row gap-5 rounded-2xl border border-gray-200 p-5">
        <UIcon name="i-lucide-trending-up" size="64" />
        <div class="flex flex-col justify-center">
          <h3 class="font-bold text-2xl">
            {{ companyStats.averageDecisions }}
          </h3>
          <p class="text-sm">priem. rozhodnutí/10min</p>
        </div>
      </div>

      <div class="flex flex-row gap-5 rounded-2xl border border-gray-200 p-5">
        <UIcon name="i-lucide-calendar-check" size="64" />
        <div class="flex flex-col justify-center">
          <h3 class="font-bold text-2xl">
            {{ companyStats.totalOffTopicFreeDays }}
          </h3>
          <p class="text-sm">celkové dni bez off-topicu</p>
        </div>
      </div>

      <div class="flex flex-row gap-5 rounded-2xl border border-gray-200 p-5">
        <UIcon name="i-lucide-users" size="64" />
        <div class="flex flex-col justify-center">
          <h3 class="font-bold text-2xl">
            {{ teams.length }}
          </h3>
          <p class="text-sm">aktívnych tímov</p>
        </div>
      </div>
    </div>

    <!-- Stredný stĺpec - Výber tímu a odznaky -->
    <div class="flex flex-col col-span-1 gap-5">
      <div class="flex flex-col gap-4 rounded-2xl border border-gray-200 p-5">
        <h2 class="text-xl font-bold">Vybraný tím</h2>
        <div class="flex flex-col gap-3">
          <div class="flex items-center gap-3 p-3 rounded-lg border border-gray-200">
            <img
              :src="selectedTeam.avatar"
              :alt="selectedTeam.name"
              class="w-12 h-12 rounded-full"
            >
            <select
              v-model="selectedTeamIndex"
              class="flex-1 bg-transparent font-semibold text-lg outline-none cursor-pointer"
            >
              <option v-for="(team, index) in teams" :key="team.name" :value="index">
                {{ team.name }}
              </option>
            </select>
          </div>

          <div class="flex flex-col gap-2 mt-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">Členovia:</span>
              <span class="font-semibold">{{ selectedTeam.members }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">Kredity:</span>
              <span class="font-semibold">{{ selectedTeam.credits }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-gray-200 p-5">
        <h2 class="text-xl font-bold mb-4">Odznaky tímu</h2>
        <div class="grid grid-cols-2 gap-4">
          <AchievementBadge
            v-for="(badge, index) in teamBadges"
            :key="index"
            :badgeImage="badge.image"
            :badgeName="badge.name"
            :badgeCount="badge.level"
          />
        </div>
      </div>
    </div>

    <!-- Pravý stĺpec - Štatistiky vybraného tímu -->
    <div class="flex flex-col col-span-1 gap-5">
      <div class="flex flex-col gap-4 rounded-2xl border border-gray-200 p-5">
        <h2 class="text-xl font-bold">Štatistika tímu</h2>
      </div>

      <div class="flex flex-col rounded-2xl border border-gray-200 p-5 items-center justify-center gap-3">
        <UIcon name="i-lucide-brick-wall-fire" size="48" class="bg-orange-500" />
        <h3 class="font-bold text-3xl">
          {{ selectedTeam.offTopicFreeDays }}
        </h3>
        <p class="text-sm text-center">dní bez off-topicu</p>
      </div>

      <div class="flex flex-col rounded-2xl border border-gray-200 p-5 items-center justify-center gap-3">
        <UIcon name="i-lucide-hourglass" size="48" />
        <h3 class="font-bold text-3xl">
          {{ selectedTeam.timeSaved }}h
        </h3>
        <p class="text-sm text-center">ušetrené hodiny</p>
      </div>

      <div class="flex flex-col rounded-2xl border border-gray-200 p-5 items-center justify-center gap-3">
        <UIcon name="i-lucide-check-check" size="48" />
        <h3 class="font-bold text-3xl">
          {{ selectedTeam.decisionsPerHour }}
        </h3>
        <p class="text-sm text-center">rozhodnutí za 10 minút</p>
      </div>
    </div>
  </UContainer>

</template>