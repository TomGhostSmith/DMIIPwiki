<script setup lang="ts">
import VPPageMeta from '@theme/VPPageMeta.vue'
import VPPageNav from '@theme/VPPageNav.vue'
import type { VNode } from 'vue'
import { onBeforeMount, ref } from 'vue'
import { Content} from 'vuepress/client'
import { usePageData, useRouter, useRoute } from 'vuepress/client'
import { userStatus } from "../../../../globalStatus.js"

const status = userStatus()



defineSlots<{
  'top'?: (props: Record<never, never>) => VNode | VNode[] | null
  'bottom'?: (props: Record<never, never>) => VNode | VNode[] | null
  'content-top'?: (props: Record<never, never>) => VNode | VNode[] | null
  'content-bottom'?: (props: Record<never, never>) => VNode | VNode[] | null
}>()

const page = usePageData()
const router = useRouter()
const route = useRoute()

const publicVisible = page.value.frontmatter.scope === 'public'  // Default to false
const privateVisible = page.value.frontmatter.scope !== 'admin'  // Default to true
const privateEditable = page.value.frontmatter.modification === 'private'  // Default to false
const adminEditable = page.value.frontmatter.modification === 'admin' || page.value.frontmatter.modification === 'private'  // Default to false

const editable = (status.userRole === "admin" && adminEditable) || (status.userRole === "user" && privateEditable)
const isVisitor = status.userRole === "logout"

const lastModify = page.value.frontmatter.lastModify + ", " + page.value.frontmatter.lastModifyDate

const showFooter = page.value.frontmatter.foot != false
onBeforeMount(async () => {
  const role = status.userRole
  console.log("page mounted");
  console.log(route.path);
  console.log(role);

  console.log(showFooter);
  
  
  try{
    if (role === 'logout' && !publicVisible) {
        // alert('Session expired. Please login again.')
        router.push({ path: '/wiki/login', query: { redirect: route.path } })
    }
    else if (role === 'user' && !privateVisible)
    {
      router.push('/wiki/adminOnly')
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

const edit = async () => {
  router.push({ path: '/wiki/editor', query: { redirect: route.path, create: "false" } })
}

const history = async () => {
  router.push({ path: '/wiki/history', query: { redirect: route.path} })
}
</script>

<template>
  <main class="vp-page" style="min-height: 100%;display: flex;flex-direction: column;">
    <slot name="top" />

    <!-- <p v-if="publicVisible">public</p>
      <p v-if="!publicVisible && privateVisible">private</p>
      <p v-if="!privateVisible">admin</p>
      <p v-if="privateEditable">|private</p>
      <p v-if="!privateEditable">|admin</p> -->

    <div class="content-wrapper" style="width: 100%">
      <div vp-content style="display: block;">
        <slot name="content-top" />
  
        <h1>{{ page.frontmatter.title }}</h1>
        <Content />
  
        <slot name="content-bottom" />
      </div>
    </div>

    <div style="flex-grow: 1; padding: 20px;"></div>

    <!-- <VPPageMeta /> -->
    <!-- <div class="vp-footer" vp-footer style="padding: 0 300px 0"> -->
    <div class="vp-footer" vp-footer style="margin-top: auto;">
      <span v-if="!isVisitor && showFooter">最后编辑：{{ lastModify }}</span>
      <el-button v-if="editable && showFooter" type="text" @click="edit" style="display: inline; margin-left: 20px;margin-bottom: 5px;">编辑本页</el-button>
      <el-button v-if="!isVisitor && showFooter" type="text" @click="history" style="display: inline; margin-left: 20px;margin-bottom: 5px;">查看历史</el-button>
      <p style="max-width: 880px; margin: auto;;">MIT Licensed | Copyright © 2025-present Laboratory of Data Mining and Intellignet Information Processing, Institute of Science and Technology for Brain-Inspired Intelligence, Fudan University</p>
    </div>

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
#app{
  display: flex!important;
  flex-direction: column;
  flex-grow: 1;
  height: 100%!important
}
html {min-height: 100% !important}
body {height: 100% !important}
</style>
