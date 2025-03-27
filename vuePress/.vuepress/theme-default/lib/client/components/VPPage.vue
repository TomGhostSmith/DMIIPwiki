<script setup lang="ts">
import VPPageMeta from '@theme/VPPageMeta.vue'
import VPPageNav from '@theme/VPPageNav.vue'
import type { VNode } from 'vue'
import { onMounted, inject, ref } from 'vue'
import { Content} from 'vuepress/client'
import { usePageData, useRouter, useRoute } from 'vuepress/client'
import { userStatus } from "../../../../globalStatus.js"
import { stat } from 'fs'


const status = userStatus()



defineSlots<{
  'top'?: (props: Record<never, never>) => VNode | VNode[] | null
  'bottom'?: (props: Record<never, never>) => VNode | VNode[] | null
  'content-top'?: (props: Record<never, never>) => VNode | VNode[] | null
  'content-bottom'?: (props: Record<never, never>) => VNode | VNode[] | null
}>()

const role = status.userRole

const page = usePageData()
const router = useRouter()
const route = useRoute()

const publicVisible = page.value.frontmatter.scope === 'public'  // Default to false
const privateVisible = page.value.frontmatter.scope !== 'admin'  // Default to true
const privateEditable = page.value.frontmatter.modification === 'private'  // Default to false


onMounted(async () => {
  console.log("page mounted");
  console.log(route.path);
  console.log(role);
  
  
  try{
    if (role === 'logout' && !publicVisible) {
        // alert('Session expired. Please login again.')
        router.push({ path: '/wiki/login', query: { redirect: route.path } })
    }
    else if (role !== 'logout' && route.path === '/wiki/login.html')
    {
      router.push('/wiki/')
    }
  } catch {
    // alert('Error checking authentication. Please login again.')
    router.push({ path: '/wiki/login', query: { redirect: route.path } })
  }
})


</script>

<template>
  <main class="vp-page">
    <slot name="top" />

    <p v-if="publicVisible">public</p>
      <p v-if="!publicVisible && privateVisible">private</p>
      <p v-if="!privateVisible">admin</p>
      <p v-if="privateEditable">|private</p>
      <p v-if="!privateEditable">|admin</p>

    <div vp-content>
      <slot name="content-top" />

      <Content />

      <slot name="content-bottom" />
    </div>

    <VPPageMeta />

    <VPPageNav />

    <slot name="bottom" />
  </main>
</template>

<style lang="scss">
@use '../styles/mixins';
@use '../styles/variables' as *;

.vp-page {
  display: block;

  // leave space for navbar
  padding-top: var(--navbar-height);
  padding-bottom: 2rem;

  // leave space for sidebar
  padding-inline-start: var(--sidebar-width);

  // narrow desktop / iPad
  @media (max-width: $MQNarrow) {
    // leave space for sidebar
    padding-inline-start: var(--sidebar-width-mobile);
  }

  // wide mobile
  @media (max-width: $MQMobile) {
    // sidebar is collapsed
    padding-inline-start: 0;
  }

  [vp-content] {
    @include mixins.content-wrapper;

    & {
      padding-top: 0;
    }
  }
}
</style>
