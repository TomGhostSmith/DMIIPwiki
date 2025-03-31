<template>
    <el-table :data="table" style="width: 100%" :fit="true" empty-text="目前没有申请记录">
        <el-table-column prop="username" label="用户名" width="100px"/>
        <el-table-column prop="apply" label="申请时间" width="200px"/>
        <el-table-column prop="email" label="邮箱" min-width="300px"/>
        <el-table-column label="操作" width="400px" fixed="right">
            <el-button type="primary">设为管理员</el-button>
            <el-button type="primary">设为普通用户</el-button>
            <el-button type="danger" >拒绝申请</el-button>
        </el-table-column>
    </el-table>
    <!-- <el-button type="danger" style="margin-top: 20px;" @click="logout">退出登录</el-button> -->
    <!-- <el-button style="margin-top: 20px; margin-left: 20px;" @click="cancel">Cancel</el-button> -->
</template>
<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"

const table = ref([])
// const table = ref([{username: "tom", apply: "yesterday", email: "abc@gmail.com"}])
const router = useRouter()
const status = userStatus()

const logout = async () => {
  await fetch('/api/logout', { method: 'POST', credentials: 'include' })
  // alert('Logged out successfully.')
  status.logout()
  router.push('/wiki/login')
}

onMounted(async () => {
    
})
</script>