<script setup lang="ts">
import VPNavbarBrand from '@theme/VPNavbarBrand.vue'
import VPNavbarItems from '@theme/VPNavbarItems.vue'
import VPToggleColorModeButton from '@theme/VPToggleColorModeButton.vue'
import VPToggleSidebarButton from '@theme/VPToggleSidebarButton.vue'
import { useData } from '@theme/useData'
import { DeviceType, useUpdateDeviceStatus } from '@theme/useUpdateDeviceStatus'
import { hasGlobalComponent } from '@vuepress/helper/client'
import type { VNode } from 'vue'
import { computed, ref, resolveComponent, useTemplateRef } from 'vue'
import { onMounted, provide } from 'vue'
import { usePageData, useRouter, useRoute } from 'vuepress/client'
import { userStatus } from "../../../../globalStatus.js"

defineEmits<{
  toggleSidebar: []
}>()

defineSlots<{
  before?: (props: Record<never, never>) => VNode | VNode[] | null
  after?: (props: Record<never, never>) => VNode | VNode[] | null
}>()

const status = userStatus()

const SearchBox = hasGlobalComponent('SearchBox')
  ? resolveComponent('SearchBox')
  : (): null => null

const { themeLocale } = useData()

const navbar = useTemplateRef<HTMLElement | null>('navbar')
const navbarBrand = useTemplateRef<HTMLElement | null>('navbar-brand')

const linksWrapperMaxWidth = ref(0)
const linksWrapperStyle = computed(() => {
  if (!linksWrapperMaxWidth.value) {
    return {}
  }
  return {
    maxWidth: `${linksWrapperMaxWidth.value}px`,
  }
})

const getCssValue = (el: HTMLElement | null, property: string): number => {
  // NOTE: Known bug, will return 'auto' if style value is 'auto'
  const val = el?.ownerDocument.defaultView?.getComputedStyle(el, null)[
    property as keyof CSSStyleDeclaration
  ]

  const num = Number.parseInt(val as string, 10)

  return Number.isNaN(num) ? 0 : num
}

useUpdateDeviceStatus(
  DeviceType.Mobile,
  (mobileDesktopBreakpoint: number): void => {
    // avoid overlapping of long title and long navbar links
    const navbarHorizontalPadding =
      getCssValue(navbar.value, 'paddingLeft') +
      getCssValue(navbar.value, 'paddingRight')
    if (window.innerWidth < mobileDesktopBreakpoint) {
      linksWrapperMaxWidth.value = 0
    } else {
      linksWrapperMaxWidth.value =
        navbar.value!.offsetWidth -
        navbarHorizontalPadding -
        (navbarBrand.value?.offsetWidth ?? 0)
    }
  },
)


// const page = usePageData()
const router = useRouter()
const route = useRoute()

// const publicVisible = page.value.frontmatter.scope === 'public'  // Default to false
// const privateVisible = page.value.frontmatter.scope !== 'admin'  // Default to true
// const privateEditable = page.value.frontmatter.modification === 'private'  // Default to false

// const role = ref('logout')
// provide("role", role)
// const role = defineModel();



onMounted(async () => {
  console.log(status.userRole);
  
    try {
      const response = await fetch('/api/check-auth', {
        credentials: 'include'
      })
      const data = await response.json()
      
      status.login(data.user, data.role)
    } catch {
    // alert('Error checking authentication. Please login again.')
    router.push({ path: '/wiki/login', query: { redirect: route.path } })
  }
  console.log(status.userRole);
})

const login = async () => {
    router.push('/wiki/login')
}
  
const profile = async() => {
  router.push('/wiki/profile')
}

const manage = async() => {
  router.push('/wiki/userManage')
}

const logout = async () => {
  await fetch('/api/logout', { method: 'POST', credentials: 'include' })
  // alert('Logged out successfully.')
  status.logout()
  router.push('/wiki/login')
}


</script>

<template>
  <header ref="navbar" class="vp-navbar" vp-navbar>
    <VPToggleSidebarButton @toggle="$emit('toggleSidebar')" />
    <span ref="navbar-brand">
      <VPNavbarBrand />
    </span>


    <div class="vp-navbar-items-wrapper" :style="linksWrapperStyle">
      <slot name="before" />
      <VPNavbarItems class="vp-hide-mobile" />
      <slot name="after" />
      <el-button v-if="status.userRole === 'logout'" type="text" @click="login" style="margin-left: 20px;margin-top: 2px;">登录</el-button>
      <el-button v-if="status.userRole !== 'logout'" type="text" @click="profile" style="margin-left: 20px;margin-top: 2px;">{{ status.userName }}</el-button>
      <el-button v-if="status.userRole !== 'logout'" type="text" @click="logout" style="margin-left: 20px;margin-top: 2px;">退出登录</el-button>
      <el-button v-if="status.userRole === 'admin'" type="text" @click="manage" style="margin-left: 20px;margin-top: 2px;">用户管理</el-button>
      <VPToggleColorModeButton v-if="themeLocale.colorModeSwitch" />
      <SearchBox />
      <!-- <el-button type="text" @click="edit">edit</el-button> -->
    </div>
  </header>
</template>

<style lang="scss">
@use '../styles/variables' as *;

.vp-navbar {
  --navbar-line-height: calc(
    var(--navbar-height) - 2 * var(--navbar-padding-v)
  );

  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 20;

  box-sizing: border-box;
  height: var(--navbar-height);
  padding: var(--navbar-padding-v) var(--navbar-padding-h);
  border-bottom: 1px solid var(--vp-c-border);

  background-color: var(--vp-navbar-c-bg);

  line-height: var(--navbar-line-height);

  transition:
    background-color var(--vp-t-color),
    border-color var(--vp-t-color);

  @media screen and (max-width: $MQMobile) {
    padding-inline-start: 4rem;
  }
}

.vp-navbar-items-wrapper {
  position: absolute;
  inset-inline-end: var(--navbar-padding-h);
  top: var(--navbar-padding-v);

  display: flex;

  box-sizing: border-box;
  height: var(--navbar-line-height);
  padding-inline-start: var(--navbar-padding-h);

  font-size: 0.9rem;
  white-space: nowrap;
}
</style>
