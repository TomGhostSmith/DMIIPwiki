<template>
    <el-form :model="info" label-width="auto" style="max-width: 600px; margin-top: 20px;">
        <el-form-item label="用户名">
            <el-input v-model="info.userName"/>
        </el-form-item>
        <el-form-item label="邮箱">
            <el-input v-model="info.email"/>
        </el-form-item>
    </el-form>
    <el-button type="primary" @click="sendEmail" :loading="waitSend">{{ sendText }}</el-button>
    <div v-if="sent">
        <hr>
        <el-form :model="form" label-width="auto" style="max-width: 600px; margin-top: 20px;">
            <el-form-item label="验证码">
                <el-input v-model="form.verifyCode"/>
            </el-form-item>
            <el-form-item label="新密码">
                <el-input v-model="form.newPass" type="password" show-password/>
            </el-form-item>
            <el-form-item label="确认新密码">
                <el-input v-model="form.newPassRepeat" type="password" show-password/>
            </el-form-item>
        </el-form>
        <el-button type="primary" @click="changePass">修改密码</el-button>
    </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"
import CryptoJS from 'crypto-js';
const info = ref({userName: "", email: ""})
const form = ref({validateCode: "", newPass: "", newPassRepeat: ""})
const router = useRouter()
const status = userStatus()

const sent = ref(false)

const sendText = ref("发送验证码")
const waitSend = ref(false)

const { proxy } = getCurrentInstance();

onMounted(async () => {
    
})

const sendEmail = async () => {
    try
    {
        const response = await fetch('/api/forgetPass', {
            method: 'POST',
            credentials: 'include',  // Important: Allows cookies to be sent
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                username: info.value.userName, 
                email: info.value.email, 
            })
        })
    
        if (response.ok) {
            // alert('Login successful!')
            // let resp = await response.json()
            // console.log(resp);
            // console.log(redirectTo);
            // console.log(resp.role);
            // console.log(resp["role"]);
            proxy.$message.success('已发送邮件，请注意查收')
            sent.value = true
            let countdown = 60
            waitSend.value = true
            let timer = setInterval(() => {
                countdown --;
                if (countdown > 0)
                {
                    sendText.value = `请在 ${countdown}s 后重新发送`
                }
                else
                {
                    waitSend.value = false
                    sendText.value = "重新发送"
                    clearInterval(timer)
                }
            }, 1000)
            
        } else {
            let resp = await response.json()
            proxy.$message.error(resp.error)
        }
    }
    catch (error) {
        console.log(error)
    }
}

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
            body: JSON.stringify({ username: info.value.userName})
        })
        if (saltResponse.ok)
        {
            let saltResp = await saltResponse.json()
            let salt = saltResp.salt
            let nance = saltResp.nance
            console.log(nance);
            console.log(salt);

            let saltedPassword = CryptoJS.PBKDF2(form.value.newPass, salt, {
                keySize: 64/4,
                iterations: 10,
                hasher: CryptoJS.algo.SHA256
            })
            console.log(info.value)
            const response = await fetch('/api/modifyPasswdFromEmail', {
                method: 'PUT',
                credentials: 'include',  // Important: Allows cookies to be sent
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    username: info.value.userName, 
                    passwd: saltedPassword.toString(CryptoJS.enc.Hex), 
                    code: form.value.verifyCode, 
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