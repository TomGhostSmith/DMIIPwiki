<template>
    <div>
    </div>
</template>
    
<script setup>
    import { useRoute, useRouter } from 'vuepress/client'
    import { getCurrentInstance, onMounted, ref } from 'vue'
    // import bcrypt from 'bcrypt'
    const router = useRouter()

    onMounted(() => {
        router.push('/wiki/')
    })
</script>