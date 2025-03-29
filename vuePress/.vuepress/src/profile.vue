<template>
    <el-form :model="form" label-width="auto" style="max-width: 600px;">
        <el-form-item label="用户名">
            <el-input :readonly="true" v-model="form.name"/>
        </el-form-item>
        <el-form-item label="用户组">
            <el-input :readonly="true" v-model="form.group"/>
        </el-form-item>
        <el-form-item label="注册时间">
            <el-input :readonly="true" v-model="form.registerDate"/>
        </el-form-item>
        <el-form-item label="邮箱">
            <el-input :readonly="true" v-model="form.email"/>
            <el-button @click="changeEmail">修改邮箱</el-button>
        </el-form-item>
        <el-form-item label="密码">
            <el-button @click="changePassword">修改密码</el-button>
        </el-form-item>
        
    </el-form>
    <el-button type="danger" style="margin-top: 20px;" @click="logout">退出登录</el-button>
    <!-- <el-button style="margin-top: 20px; margin-left: 20px;" @click="cancel">Cancel</el-button> -->
</template>
<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"

const form = ref({})
const router = useRouter()
const status = userStatus()

const logout = async () => {
  await fetch('/api/logout', { method: 'POST', credentials: 'include' })
  // alert('Logged out successfully.')
  status.logout()
  router.push('/wiki/login')
}

onMounted(async () => {
    try
    {
        const response = await fetch('/api/getUserInfo', {
          method: 'GET',
          credentials: 'include',  // Important: Allows cookies to be sent
        })

        if (response.ok)
        {
            let resp = await response.json()
            let group = resp.role === "user"? "普通用户" : "管理员"
            form.value = {
                name: resp.user,
                group: group,
                registerDate: resp.registerDate,
                email: resp.email
            }
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