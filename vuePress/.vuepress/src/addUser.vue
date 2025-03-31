<template>
    <el-form :model="form" label-width="auto" style="max-width: 600px;margin-top: 20px;">
        <el-form-item label="用户名">
            <el-input v-model="form.name"/>
        </el-form-item>
        <el-form-item label="用户组">
            <el-radio-group v-model="form.group">
                <el-radio value="user">普通用户</el-radio>
                <el-radio value="admin">管理员</el-radio>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="邮箱">
            <el-input v-model="form.email"/>
        </el-form-item>
        
    </el-form>
    <el-button type="primary" style="margin-top: 10px;" @click="addUser">添加用户</el-button>
    <!-- <el-button style="margin-top: 20px; margin-left: 20px;" @click="cancel">Cancel</el-button> -->
</template>
<script setup>
import { ref, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"
import CryptoJS from 'crypto-js';

const form = ref({})
const router = useRouter()
const status = userStatus()
const { proxy } = getCurrentInstance();


const addUser = async () => {
    const now = new Date();
    const datePart = now.toISOString().split('T')[0]; // YYYY-MM-DD
    const timePart = now.toTimeString().split(' ')[0]; // HH-mm

    const register = `${datePart} ${timePart}`
    console.log(register);
    console.log(form);
    
    let response = await fetch('/api/addUser', { method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            username: form.value.name,
            email: form.value.email,
            role: form.value.group
        })

    })
    if (response.ok)
    {
        proxy.$message.success('添加成功')
        form.value = {}
        location.reload()
    }
    else
    {
        let data = await response.json()
        proxy.$message.error('添加失败: ' + data.error)
    }
}
</script>