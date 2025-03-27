<template>
    <div>
        <h2>Login</h2>
        <p v-if="errorMessage" style="color:red;">{{ errorMessage }}</p>
        <el-input v-model="username" placeholder="Username" />
        <br>
        <br>
        <el-input v-model="password" type="password" placeholder="Password" />
        <br>
        <br>
        <el-button type='primary' @click="login">Log in</el-button>
    </div>
</template>
    
<script setup>
    import { useRoute, useRouter } from 'vuepress/client'
    import { ref } from 'vue'
    import { userStatus } from "../globalStatus.js"
    const status = userStatus()
    
    const route = useRoute()
    const router = useRouter()
    const redirectTo = route.query.redirect || '/'
    
    const username = ref('')
    const password = ref('')
    const errorMessage = ref('')
    
    
    const login = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/login', {
          method: 'POST',
          credentials: 'include',  // Important: Allows cookies to be sent
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username.value, password: password.value })
        })
    
        if (response.ok) {
        //   alert('Login successful!')
          status.login(response.json().role)
          router.push(redirectTo) // Redirect after login
        } else {
          errorMessage.value = "Invalid username or password"
        }
      } catch (error) {
        errorMessage.value = "Error connecting to server"
      }
    }
</script>