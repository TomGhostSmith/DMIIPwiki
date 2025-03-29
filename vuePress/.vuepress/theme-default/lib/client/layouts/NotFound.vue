<script setup lang="ts">
import { useData } from '@theme/useData'
import { computed, onMounted, ref } from 'vue'
import { RouteLink, useRoute, useRouter } from 'vuepress/client'

import { userStatus } from "../../../../globalStatus.js"

const status = userStatus()

const { routeLocale, themeLocale } = useData()

const messages = computed(() => themeLocale.value.notFound ?? ['Not Found'])

const getMsg = (): string =>
  messages.value[Math.floor(Math.random() * messages.value.length)]

const homeLink = computed(() => themeLocale.value.home ?? routeLocale.value)
const homeText = computed(() => themeLocale.value.backToHome ?? 'Back to home')

const isAdmin = ref(false)

const router = useRouter()
const route = useRoute()

onMounted(() => {
    isAdmin.value = (status.userRole === "admin")
})

const edit = async () => {
  router.push({ path: '/wiki/editor', query: { redirect: route.path, create: "true" } })
}
</script>

<template>
  <div class="vp-theme-container" vp-container>
    <main class="page">
      <div vp-content>
        <h1>404</h1>

        <blockquote>{{ getMsg() }}</blockquote>

        <RouteLink :to="homeLink">{{ homeText }}</RouteLink> 
        <br>
        <el-button type="primary" v-if="isAdmin" @click="edit" style="margin-top: 20px;">创建该页面</el-button>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
.vp-theme-container {
  max-width: 740px;
  margin: 0 auto;
  padding: 2rem 2.5rem;

  @media (max-width: 959px) {
    padding: 2rem;
  }
}
</style>
