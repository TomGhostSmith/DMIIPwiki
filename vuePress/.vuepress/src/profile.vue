<template>
    <el-form :model="form" label-width="auto" style="max-width: 600px;">
        <el-form-item label="用户名">
            <el-input :readonly="true" v-model="form.name"/>
        </el-form-item>
        <el-form-item label="用户组">
            <el-radio-group :disabled="!canModifyRole" v-model="form.group" @change="modify">
                <el-radio value="user">普通用户</el-radio>
                <el-radio value="admin">管理员</el-radio>
            </el-radio-group>
            <!-- <el-input  v-model="form.group"/> -->
        </el-form-item>
        <el-form-item label="注册时间">
            <el-input :readonly="true" v-model="form.registerDate"/>
        </el-form-item>
        <el-form-item label="邮箱">
            <el-input v-model="form.email" @change="modify"/>
            <!-- <el-button @click="changeEmail" type="primary" style="margin-top: 10px;display: inline;">修改邮箱</el-button> -->
        </el-form-item>
        <!-- <el-form-item label="密码">
            <el-button @click="changePassword" type="primary">修改密码</el-button>
        </el-form-item> -->
        
    </el-form>
    <el-button :disabled="!modified" type="primary" style="margin-top: 20px;" @click="save">保存修改</el-button>
    <el-button :disabled="!modified" style="margin-top: 20px; margin-left: 20px;" @click="cancel">取消修改</el-button>
</template>
<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"

const { proxy } = getCurrentInstance();

const form = ref({})
const route = useRoute()
const router = useRouter()
const status = userStatus()
const username = ref("")

const canModifyRole = ref(false)
const modified = ref(false)

const modify = () => {
    console.log("modified");
    modified.value = true
}

const cancel = () => {
    loadUserInfo()
}

const save = async() => {
    let response = await fetch('/api/modifyUser', { method: 'PUT', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            username: form.value.name,
            email: form.value.email,
            role: form.value.group
        })

    })
    if (response.ok)
    {
        proxy.$message.success('修改成功')
        loadUserInfo()
    }
    else
    {
        let data = await response.json()
        proxy.$message.error('修改失败: ' + data.error)
    }
}

const loadUserInfo = async () => {

    try
    {
        const response = await fetch('/api/getUserInfo', {
          method: 'POST',
          credentials: 'include',  // Important: Allows cookies to be sent
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username.value})
        })

        if (response.ok)
        {
            let resp = await response.json()
            form.value = {
                name: resp.user,
                group: resp.role,
                registerDate: resp.registerDate,
                email: resp.email
            }
        }
        else
        {
            let resp = await response.json()
            proxy.$message.error(resp.error)
        }
        
    }catch (error) {
        proxy.$message.error("未知错误")
    }
    modified.value = false

}

onMounted(async () => {
    if (route.path === "/wiki/profile.html")
    {
        username.value = status.userName
        console.log("use cookie name");
        
    }
    else
    {
        username.value = route.query.user
        console.log("use name from router");
    }

    canModifyRole.value = (status.userName === "admin" && username.value !== "admin")

    loadUserInfo()
    
})
</script>