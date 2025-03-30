<template>
    <el-table :data="table">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="用户组" />
        <el-table-column prop="register" label="注册时间" />
        <el-table-column prop="email" label="邮箱" />
    </el-table>
    <!-- <el-button type="danger" style="margin-top: 20px;" @click="logout">退出登录</el-button> -->
    <!-- <el-button style="margin-top: 20px; margin-left: 20px;" @click="cancel">Cancel</el-button> -->
</template>
<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"

const table = ref([])
const router = useRouter()
const status = userStatus()

onMounted(async () => {
    try
    {
        const response = await fetch('/api/getAllUser', {
          method: 'GET',
          credentials: 'include',  // Important: Allows cookies to be sent
        })

        if (response.ok)
        {
            let resp = await response.json()
            table.value = resp.data
            console.log(resp);
            
        }
        else
        {
            console.log("Failed to fetch user info");
        }

    }catch (error) {
        console.log(error);
    }
})
</script>