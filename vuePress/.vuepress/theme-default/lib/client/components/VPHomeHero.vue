<script setup lang="ts">
import VPAutoLink from '@theme/VPAutoLink.vue'
import { useDarkMode } from '@theme/useDarkMode'
import { useData } from '@theme/useData'
import type { FunctionalComponent } from 'vue'
import { computed, h, ref, onMounted } from 'vue'
import { ClientOnly, withBase } from 'vuepress/client'
import type { DefaultThemeHomePageFrontmatter } from '../../shared/index.js'

const { frontmatter, siteLocale } = useData<DefaultThemeHomePageFrontmatter>()
const isDarkMode = useDarkMode()

const heroText = computed(() => {
  if (frontmatter.value.heroText === null) {
    return null
  }
  return frontmatter.value.heroText || siteLocale.value.title || 'Hello'
})
const tagline = computed(() => {
  if (frontmatter.value.tagline === null) {
    return null
  }

  return (
    frontmatter.value.tagline ||
    siteLocale.value.description ||
    'Welcome to your VuePress site'
  )
})
const heroImage = computed(() => {
  if (isDarkMode.value && frontmatter.value.heroImageDark !== undefined) {
    return frontmatter.value.heroImageDark
  }
  return frontmatter.value.heroImage
})
const heroAlt = computed(
  () => frontmatter.value.heroAlt || heroText.value || 'hero',
)
const heroHeight = computed(() => frontmatter.value.heroHeight ?? 280)

const actions = computed(() => {
  if (!Array.isArray(frontmatter.value.actions)) {
    return []
  }

  return frontmatter.value.actions.map(({ type = 'primary', ...rest }) => ({
    type,
    ...rest,
  }))
})

const HomeHeroImage: FunctionalComponent = () => {
  if (!heroImage.value) return null

  const img = h('img', {
    class: 'vp-hero-image',
    src: withBase(heroImage.value),
    alt: heroAlt.value,
    height: heroHeight.value,
  })

  if (frontmatter.value.heroImageDark === undefined) {
    return img
  }

  // wrap hero image with <ClientOnly> to avoid ssr-mismatch
  // when using a different hero image in dark mode
  return h(ClientOnly, () => img)
}

const images = ref([])

onMounted(async () => {
  try {
        const response = await fetch('/api/getImages');
        const data = await response.json();
        let imageList = []
        console.log(data.images);
        
        for (let i = 0;i < data.images.length;i++)
        {
          imageList.push("http://10.138.42.155:9003" + data.images[i])
        }
        images.value = imageList
        // images.value = data.images;
      } catch (error) {
        console.error('Error fetching images:', error);
      }
})
</script>

<template>
  <header class="vp-hero">
    <HomeHeroImage />

    <!-- <h1 v-if="heroText" id="main-title">
      {{ heroText }}
    </h1> -->

    
    <img src="http://10.138.42.155:9003/api/images/DMIIP.png" style="margin-top: 50px;">
    <!-- <img src="../../../../../resources/scope.png" style="margin-top: 50px; width: 100%"> -->

    <!-- <p v-if="tagline" class="vp-hero-description">
      {{ tagline }}
    </p> -->

    <el-carousel trigger="click" :interval="4000" arrow="always" style="height: 400px;">
      <el-carousel-item v-for="(image, index) in images" :key="index"  style="height: 400px;">
        <img :src="image" alt="Carousel Image" class="carousel-image"/>
      </el-carousel-item>
    </el-carousel>

    <p v-if="actions.length" class="vp-hero-actions">
      <VPAutoLink
        v-for="action in actions"
        :key="action.text"
        class="vp-hero-action-button"
        :class="[action.type]"
        :config="action"
      />
    </p>
  </header>
</template>

<style lang="scss">
@use '../styles/variables' as *;

.vp-hero {
  text-align: center;
}

.vp-hero-image {
  display: block;
  max-width: 100%;
  max-height: 280px;
  margin: 3rem auto 1.5rem;

  @media (max-width: $MQMobileNarrow) {
    max-height: 210px;
    margin: 2rem auto 1.2rem;
  }
}

#main-title {
  font-size: 3rem;

  @media (max-width: $MQMobileNarrow) {
    font-size: 2rem;
  }
}

#main-title,
.vp-hero-description,
.vp-hero-actions {
  margin: 1.8rem auto;

  @media (max-width: $MQMobileNarrow) {
    margin: 1.2rem auto;
  }
}

.vp-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.vp-hero-description {
  max-width: 35rem;
  color: var(--vp-c-text-mute);
  font-size: 1.6rem;
  line-height: 1.3;

  @media (max-width: $MQMobileNarrow) {
    font-size: 1.2rem;
  }
}

.vp-hero-action-button {
  // display: inline-block;
  display: block;

  box-sizing: border-box;
  padding: 0.8rem 1.6rem;
  border: 2px solid var(--vp-c-accent-bg);
  border-radius: 4px;

  background-color: var(--vp-c-bg);
  color: var(--vp-c-accent);

  font-size: 1.2rem;

  transition: background-color border-color color var(--vp-t-color);

  @media (max-width: $MQMobileNarrow) {
    padding: 0.6rem 1.2rem;
    font-size: 1rem;
  }

  &:hover {
    color: var(--vp-c-accent-text);
  }

  &.plain {
    color: var(--vp-c-accent-bg);
    
    &:hover {
      color: var(--vp-c-accent-hover);
      border-color: var(--vp-c-accent-hover);
    }
  }

  &.primary {
    background-color: var(--vp-c-accent-bg);
    color: var(--vp-c-accent-text);

    &:hover {
      border-color: var(--vp-c-accent-hover);
      background-color: var(--vp-c-accent-hover);
    }
  }
}

.carousel-image {
  // width: 100%;
  // height: 400px; /* Adjust the height as needed */
  object-fit: contain; /* Ensures the image covers the entire carousel */
  max-width: 100%;
  max-height: 100%;
}
</style>
