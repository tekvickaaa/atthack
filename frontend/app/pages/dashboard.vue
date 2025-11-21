<script setup lang="ts">

const { credits, setCredits } = useCredit();
const score = ref(0);
const username = ref('Alice');

onMounted(async () => {
  try {
    const data = await $fetch<any>('/api/user/alice');
    if (data) {
      username.value = data.username.charAt(0).toUpperCase() + data.username.slice(1);
      setCredits(data.credits);
      score.value = data.score;
    }
  } catch (e) {
    console.error('Failed to fetch user data', e);
  }
});

const badges = [
  {
    name: 'Topic Master',
    image: new URL('~/assets/images/dashboard/badges/TopicMaster.svg', import.meta.url).href,
    level: 3
  },
  {
    name: 'Facilitator',
    image: new URL('~/assets/images/dashboard/badges/Facilitator.svg', import.meta.url).href,
    level: 12
  },
  {
    name: 'Decision Maker',
    image: new URL('~/assets/images/dashboard/badges/DecisionMaker.svg', import.meta.url).href,
    level: 4
  },
  {
    name: 'Time Saver',
    image: new URL('~/assets/images/dashboard/badges/TimeSaver.svg', import.meta.url).href,
    level: 1
  },
  {
    name: 'Question Asker',
    image: new URL('~/assets/images/dashboard/badges/QuestionAsker.svg', import.meta.url).href,
    level: 5
  },
  {
    name: 'Insight Drop',
    image: new URL('~/assets/images/dashboard/badges/InsightDrop.svg', import.meta.url).href,
    level: 2
  }
]

const leaderboard = [
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=ux&backgroundColor=6366f1',
    name: 'UX Tím',
    points: 2850
  },
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=marketing&backgroundColor=ec4899',
    name: 'Marketing Tím',
    points: 2650
  },
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=product&backgroundColor=8b5cf6',
    name: 'Product Tím',
    points: 2400
  },
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=frontend&backgroundColor=3b82f6',
    name: 'Frontend Tím',
    points: 2150
  },
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=sales&backgroundColor=10b981',
    name: 'Sales Tím',
    points: 1950
  },
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=hr&backgroundColor=f59e0b',
    name: 'HR Tím',
    points: 1800
  },
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=support&backgroundColor=14b8a6',
    name: 'Support Tím',
    points: 1650
  },
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=devops&backgroundColor=6366f1',
    name: 'DevOps Tím',
    points: 1500
  },
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=qa&backgroundColor=a855f7',
    name: 'QA Tím',
    points: 1350
  },
  {
    avatar: 'https://api.dicebear.com/7.x/shapes/svg?seed=backend&backgroundColor=ef4444',
    name: 'Backend Tím',
    points: 1200
  }
];

</script>

<template>
  <UContainer
      class="grid grid-cols-3 gap-5 pt-6"
  >
    <div class="flex flex-col gap-5 col-span-1 col-end-2 justify-start h-[740px]">
      <div class="flex flex-col gap-4 rounded-2xl border border-gray-200 p-5">
                <img
            src="../assets/images/dashboard/profil.png"
            :alt="username"
            class="rounded-full w-24 h-24"
        >
        <div class="flex flex-col gap-2">
          <h2 class="text-xl font-bold">{{ username }}</h2>
          <div class="flex flex-row justify-items-start items-start gap-2">
            <UBadge label="Facilitator" color="secondary" variant="solid" />
            <UBadge label="UX/UI Designer" color="neutral" variant="solid" />
            <UBadge label="NoFlowCharts" color="neutral" variant="solid" />
          </div>
          <div>
            Credits: {{ credits }}
          </div>
        </div>
      </div>
      <div class="flex flex-row gap-5 rounded-2xl border border-gray-200 p-5">
        <UIcon name="i-lucide-hourglass" size="64" />
        <div class="flex flex-col justify-center">
          <h3 class="font-bold text-2xl">
            32 hodín
          </h3>
          <p>ušetrený čas na meetingoch</p>
        </div>
      </div>
            <div class="flex flex-row gap-5 rounded-2xl border border-gray-200 p-5">
        <UIcon name="i-lucide-check-check" size="64" />
        <div class="flex flex-col justify-center">
          <h3 class="font-bold text-2xl">
            {{ score }}
          </h3>
          <p>rozhodnutí za 10 minút</p>
        </div>
      </div>
    </div>
    <div class="flex flex-col col-span-2 col-start-2 col-end-2 gap-5">
      <div class="flex flex-col rounded-2xl border border-gray-200 p-5 items-center gap-5">
        <UIcon name="i-lucide-brick-wall-fire" size="96" class="bg-orange-500" />
        <h3 class="font-bold text-6xl">
          78
        </h3>
        <p>
          dní bez off-topicu na meetingoch
        </p>
      </div>
      <div class="rounded-2xl border border-gray-200 p-5 h-full">
        <div class="grid grid-cols-2 grid-rows-3 gap-5 justify-around">
          <AchievementBadge
              v-for="(badge, index) in badges"
              :key="index"
              :badgeImage="badge.image"
              :badgeName="badge.name"
              :badgeCount="badge.level"
          />
        </div>
      </div>
    </div>
    <div class="col-start-3 col-end-3 rounded-2xl border border-gray-200 p-5 flex flex-col gap-5 h-[740px] overflow-y-auto">
        <h2 class="font-bold text-2xl">
          Leaderboard
        </h2>
        <div class="flex flex-col gap-5 h-[700px] overflow-y-auto">
          <div
            v-for="(item, index) in leaderboard"
            :key="item.name"
            class="flex flex-row items-center gap-3 px-4 py-2 rounded-lg"
            :class="{ 'bg-gray-100 border border-gray-300': item.name === 'UX Tím' }"
          >
            <p class="w-4">{{ index + 1 }}.</p>
            <img
                :src="item.avatar"
                :alt="item.name"
                class="rounded-full w-12 h-12 inline-block"
            >
            <div class="flex flex-row w-full justify-between">
              <h3 class="font-bold text-lg inline-block">{{ item.name }}</h3>
              <p class="inline-block ml-3">{{ item.points }} bodov</p>
            </div>
          </div>
         </div>

    </div>
  </UContainer>
</template>