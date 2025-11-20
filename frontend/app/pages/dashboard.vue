<script setup lang="ts">

const items = [
  {
    avatar: 'https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793',
    name: 'Petr Balabolkin',
    points: 1500
  },
  {
    avatar: 'https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793',
    name: 'Anna Nováková',
    points: 1200
  },
  {
    avatar: 'https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793',
    name: 'Jan Svoboda',
    points: 1100
  },
  {
    avatar: 'https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793',
    name: 'Eva Dvořáková',
    points: 900
  },
  {
    avatar: 'https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793',
    name: 'Karel Černý',
    points: 800
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
            alt="Petr Balabolkin"
            class="rounded-full w-24 h-24"
        >
        <div class="flex flex-col gap-2">
          <h2 class="text-xl font-bold">Petr Balabolkin</h2>
          <div class="flex flex-row justify-items-start items-start gap-2">
            <UBadge label="Facilitator" color="secondary" variant="solid" />
            <UBadge label="UX/UI Designer" color="neutral" variant="solid" />
            <UBadge label="NoFlowCharts" color="neutral" variant="solid" />
          </div>
          <div>
            Credits: 3450
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
            0,87
          </h3>
          <p>rozhodnutí za 10 minút</p>
        </div>
      </div>
    </div>
    <div class="flex flex-col col-span-2 col-start-2 col-end-2 gap-5">
      <div class="flex flex-col rounded-2xl border border-gray-200 p-5 items-center gap-5">
        <UIcon name="i-lucide-brick-wall-fire" size="96" />
        <h3 class="font-bold text-6xl">
          78
        </h3>
        <p>
          dnov bez off-topicu na meetingoch
        </p>
      </div>
      <div class="rounded-2xl border border-gray-200 p-5 h-full">
        <div class="grid grid-cols-2 grid-rows-3 gap-5 justify-around">
          <div class="flex flex-col justify-center items-center gap-3">
            <div class="bg-red-500 p-2 rounded-full w-fit">
              <div class="bg-white p-1 rounded-full w-fit">
                <img
                    src="https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793"
                    alt="Badge 1"
                    class="rounded-full w-24 h-24"
                >
              </div>
            </div>
            <p>frevrew</p>
          </div>

          <div class="flex flex-col justify-center items-center gap-3">
            <div class="bg-red-500 p-2 rounded-full w-fit">
              <div class="bg-white p-1 rounded-full w-fit">
                <img
                    src="https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793"
                    alt="Badge 1"
                    class="rounded-full w-24 h-24"
                >
              </div>
            </div>
            <p>frevrew</p>
          </div>
          <div class="flex flex-col justify-center items-center gap-3">
            <div class="bg-red-500 p-2 rounded-full w-fit">
              <div class="bg-white p-1 rounded-full w-fit">
                <img
                    src="https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793"
                    alt="Badge 1"
                    class="rounded-full w-24 h-24"
                >
              </div>
            </div>
            <p>frevrew</p>
          </div>
          <div class="flex flex-col justify-center items-center gap-3">
            <div class="bg-red-500 p-2 rounded-full w-fit">
              <div class="bg-white p-1 rounded-full w-fit">
                <img
                    src="https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793"
                    alt="Badge 1"
                    class="rounded-full w-24 h-24"
                >
              </div>
            </div>
            <p>frevrew</p>
          </div>
          <div class="flex flex-col justify-center items-center gap-3">
            <div class="bg-red-500 p-2 rounded-full w-fit">
              <div class="bg-white p-1 rounded-full w-fit">
                <img
                    src="https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793"
                    alt="Badge 1"
                    class="rounded-full w-24 h-24"
                >
              </div>
            </div>
            <p>frevrew</p>
          </div>
          <div class="flex flex-col justify-center items-center gap-3">
            <div class="bg-red-500 p-2 rounded-full w-fit">
              <div class="bg-white p-1 rounded-full w-fit">
                <img
                    src="https://i.im.cz/ac/GD28XJSSHLRfouD6jTtWyiz0RE_mDKmhbRvpeQoF/48?r2=0.4625850170554793"
                    alt="Badge 1"
                    class="rounded-full w-24 h-24"
                >
              </div>
            </div>
            <p>frevrew</p>
          </div>

        </div>
      </div>
    </div>
    <div class="col-start-3 col-end-3 rounded-2xl border border-gray-200 p-5 flex flex-col gap-5">
        <h2 class="font-bold text-2xl">
          Leaderboard
        </h2>
        <div class="flex flex-col gap-5">
          <div v-for="(item, index) in items" :key="item.name" class="flex flex-row items-center gap-3">
            <p>{{ index + 1 }}.</p>
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