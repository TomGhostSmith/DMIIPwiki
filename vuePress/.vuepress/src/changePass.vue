<template>
        <el-form :model="form" label-width="auto" style="max-width: 600px; margin-top: 20px;">
        <el-form-item label="原密码">
            <el-input v-model="form.oldPass" type="password" show-password/>
        </el-form-item>
        <el-form-item label="新密码">
            <el-input v-model="form.newPass" type="password" show-password/>
        </el-form-item>
        <el-form-item label="确认新密码">
            <el-input v-model="form.newPassRepeat" type="password" show-password/>
        </el-form-item>
        
    </el-form>
    <el-button type="primary" @click="changePass">修改密码</el-button>
</template>

<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"
import CryptoJS from 'crypto-js';
const form = ref({oldPass: "", newPass: "", newPassRepeat: ""})
const router = useRouter()
const status = userStatus()

const { proxy } = getCurrentInstance();

onMounted(async () => {
    
})

const changePass = async () => {
    if (form.value.newPass !== form.value.newPassRepeat)
    {
        proxy.$message.error('两次输入的密码不同')
        return
    }
    try {
        const saltResponse = await fetch('/api/getNance', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: status.userName})
        })
        if (saltResponse.ok)
        {
            let saltResp = await saltResponse.json()
            let salt = saltResp.salt
            let nance = saltResp.nance
            console.log(nance);
            console.log(salt);

            let saltedOldPassword = CryptoJS.PBKDF2(form.value.oldPass, salt, {
                keySize: 64/4,
                iterations: 10,
                hasher: CryptoJS.algo.SHA256
            })
            let saltedPassword = CryptoJS.PBKDF2(form.value.newPass, salt, {
                keySize: 64/4,
                iterations: 10,
                hasher: CryptoJS.algo.SHA256
            })
            let hashedSaltedPassword = CryptoJS.PBKDF2(saltedOldPassword.toString(CryptoJS.enc.Hex), nance, {
                keySize: 64/4,
                iterations: 10,
                hasher: CryptoJS.algo.SHA256
            })
            const response = await fetch('/api/modifyPasswd', {
                method: 'PUT',
                credentials: 'include',  // Important: Allows cookies to be sent
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    username: status.userName, 
                    passwd: saltedPassword.toString(CryptoJS.enc.Hex), 
                    oldPasswd: hashedSaltedPassword.toString(CryptoJS.enc.Hex), 
                    nance: nance 
                })
            })
        
            if (response.ok) {
                // alert('Login successful!')
                // let resp = await response.json()
                // console.log(resp);
                // console.log(redirectTo);
                // console.log(resp.role);
                // console.log(resp["role"]);
                proxy.$message.success('修改成功，请重新登陆')
                status.logout()
                router.push("/wiki/login")
                form.value = {oldPass: "", newPass: "", newPassRepeat: ""}
                
            } else {
                let resp = await response.json()
                proxy.$message.error(resp.error)
            }
        } else {
        }
    } catch (error) {
        console.log(error);
    }
}
</script>