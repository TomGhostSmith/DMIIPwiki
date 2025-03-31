<template>
    <el-popconfirm
        confirm-button-text="确认"
        cancel-button-text="取消"
        title="确认要重置吗？"
        @confirm="resetPassword"
        @cancel="cancelEvent"
    >
        <template #reference>
        <el-button :disabled="!canModify" type="danger">重置密码</el-button>
        </template>
    </el-popconfirm>


    
    <el-popconfirm
        confirm-button-text="确认"
        cancel-button-text="取消"
        title="确认要删除吗？"
        @confirm="deleteUser"
    >
        <template #reference>
            <el-button :disabled="!canModify" type="danger">删除用户</el-button>
        </template>
    </el-popconfirm>

</template>

<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"

const form = ref({})
const route = useRoute()
const router = useRouter()
const status = userStatus()
const username = ref("")

const canModify = ref(false)
const { proxy } = getCurrentInstance()

const deleteUser = async () => {
    try
    {
        const response = await fetch('/api/deleteUser', {
          method: 'POST',
          credentials: 'include',  // Important: Allows cookies to be sent
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username.value})
        })

        if (response.ok)
        {
            proxy.$message.success("删除成功")
            router.push("/wiki/userManage")
        }
        else
        {
            let resp = await response.json()
            proxy.$message.error("删除失败：" + resp.error)
        }
        
    }catch (error) {
        proxy.$message.error("删除失败：未知错误" )
    }
}

const resetPassword = async () => {
    try
    {
        const response = await fetch('/api/resetPasswd', {
          method: 'PUT',
          credentials: 'include',  // Important: Allows cookies to be sent
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username.value})
        })

        if (response.ok)
        {
            proxy.$message.success("重置成功")
        }
        else
        {
            let resp = await response.json()
            proxy.$message.error("重置失败：" + resp.error)
        }
        
    }catch (error) {
        proxy.$message.error("重置失败：未知错误" )
    }
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

    canModify.value = (status.userName === "admin" && username.value !== "admin")

})
</script>