<template>
    <el-table :data="table" style="width: 100%" :fit="true">
        <el-table-column prop="username" label="用户名" width="100px"/>
        <el-table-column prop="role" label="用户组" width="100px"/>
        <el-table-column prop="register" label="注册时间" width="200px"/>
        <el-table-column prop="email" label="邮箱" min-width="300px"/>
        <el-table-column label="操作" width="100px" fixed="right">
            <template #default="scope">
                <el-button type="text" @click="detail(scope.row.username)" :disabled="scope.row.username == 'admin'">详情</el-button>
            </template>
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
const router = useRouter()
const status = userStatus()

const detail = (username) =>
{
    router.push({path: "/wiki/userProfile", query: {user: username}})
}

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

<style lang="css">
.el-table__header {
    margin-bottom: 0!important;
}
.el-table__body {
    margin-top: 0!important;
}
.el-table__header th, .el-table__body td {
    border: none
}
</style>