<template>
    <div>
        <h2>登录</h2>
        <p v-if="errorMessage" style="color:red;">{{ errorMessage }}</p>
        <el-input v-model="username" placeholder="Username" />
        <br>
        <br>
        <el-input v-model="password" type="password" placeholder="Password" show-password @keydown.enter="login"/>
        <br>
        <br>
        <el-button type='primary' @click="login">登录</el-button> 
        <el-button type="text" @click="forgetPass">忘记密码？</el-button>
    </div>
</template>
    
<script setup>
    import { useRoute, useRouter } from 'vuepress/client'
    import { getCurrentInstance, ref } from 'vue'
    import CryptoJS from 'crypto-js';
    import { userStatus } from "../globalStatus.js"
    // import bcrypt from 'bcrypt'
    const status = userStatus()
    
    const route = useRoute()
    const router = useRouter()
    const redirectTo = route.query.redirect || '/'
    
    const username = ref('')
    const password = ref('')
    const errorMessage = ref('')

    const { proxy } = getCurrentInstance()

    const forgetPass = () => {
      router.push("/wiki/forgetPass")
    }
    
    
    const login = async () => {
      try {
        const saltResponse = await fetch('/api/getNance', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username.value})
        })
        if (saltResponse.ok)
        {
          let saltResp = await saltResponse.json()
          let salt = saltResp.salt
          let nance = saltResp.nance
          console.log(nance);
          console.log(salt);
          
          
          let saltedPassword = CryptoJS.PBKDF2(password.value, salt, {
            keySize: 64/4,
            iterations: 10,
            hasher: CryptoJS.algo.SHA256
          })
          console.log(saltedPassword.toString(CryptoJS.enc.Hex));
          
          let hashedSaltedPassword = CryptoJS.PBKDF2(saltedPassword.toString(CryptoJS.enc.Hex), nance, {
            keySize: 64/4,
            iterations: 10,
            hasher: CryptoJS.algo.SHA256
          })
          const response = await fetch('/api/login', {
            method: 'POST',
            credentials: 'include',  // Important: Allows cookies to be sent
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username.value, password: hashedSaltedPassword.toString(CryptoJS.enc.Hex), nance: nance })
          })
      
          if (response.ok) {
            console.log(response.status);
            
            // alert('Login successful!')
            let resp = await response.json()
            // console.log(resp);
            // console.log(redirectTo);
            // console.log(resp.role);
            // console.log(resp["role"]);
            status.login(resp.user, resp.role)
            if (resp.emptyEmail)
            {
              proxy.$message.success("登录成功，请完善邮箱信息以便找回密码")
              router.push("/wiki/profile.html")
            }
            else 
            {
              if (redirectTo === "/")
              {
                router.push("/wiki/") // Redirect after login
              }
              else
              {
                router.push(redirectTo) // Redirect after login
              }
              proxy.$message.success("登录成功")
            }
          // } else if (response.status === 302){
          } else {
            errorMessage.value = "用户名或密码错误"
          }
        } else {
          errorMessage.value = "用户名或密码错误"
        }
      } catch (error) {
        console.log(error);
        errorMessage.value = "无法连接到服务器"
      }
    }
</script>