<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const route = useRoute()

const items = computed<NavigationMenuItem[]>(() => [{
  label: 'Dashboard',
  to: '/dashboard',
  active: route.path.startsWith('/dashboard')
}, {
  label: 'Meetings',
  to: '/meetings',
  active: route.path.startsWith('/meetings')
}, {
  label: 'Garden',
  to: '/garden',
  active: route.path.startsWith('/garden')
}])
</script>

<template>
  <div>
    <NuxtRouteAnnouncer />
    <UHeader
        title="Shorten it up"
        template="colored"
        class="flex justify-between"
    >
      <template #right>
        <UButton v-for="item in items"
                 :key="item.label"
                 :to="item.to"
                 :label="item.label"
                 :color="item.active ? 'primary' : 'neutral'"
                 :variant="item.active ? 'solid' : 'outline'"
        />
      </template>
    </UHeader>
    <NuxtPage />
  </div>
</template>