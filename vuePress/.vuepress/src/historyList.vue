<template>
    <h2>{{ redirectTo }}的历史版本</h2>
    <el-table :data="table" style="" :fit="true" :height="height">
        <el-table-column prop="user" label="编辑用户" width="200px"/>
        <el-table-column prop="time" label="编辑时间" min-width="200px"/>
        <el-table-column label="操作" width="100px">
            <template #default="scope">
                <el-button type="text" @click="detail(scope.row.time)">查看</el-button>
            </template>
        </el-table-column>
    </el-table>
    <h2>以下是{{ version }}版本的内容</h2>
        <div id="editor" style="margin-top: 20px"></div>
    <!-- <el-button type="danger" style="margin-top: 20px;" @click="logout">退出登录</el-button> -->
    <!-- <el-button style="margin-top: 20px; margin-left: 20px;" @click="cancel">Cancel</el-button> -->
</template>
<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"

// const table = ref([])
const table = ref([])
const route = useRoute()
const router = useRouter()
const status = userStatus()
const file = ref("")
const version = ref("")
const editorInstance = ref(null)

const redirectTo = route.query.redirect || '/'
let Editor

const detail = (modifyTime) =>
{
    version.value = modifyTime
    loadContent()
}

const height = ref(100)

onMounted(async () => {
    let fileName = redirectTo.replace(".html", ".md")
    if (fileName.charAt(redirectTo.length - 1) == "/")
    {
        fileName = fileName + "index.md"
    }
    fileName = "." + fileName
    file.value = fileName
    try
    {
        const response = await fetch('/api/getHistory', {
          method: 'POST',
          credentials: 'include',  // Important: Allows cookies to be sent
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file: file.value})
        })

        if (response.ok)
        {
            let resp = await response.json()
            table.value = resp.data
            version.value = resp.currentVersion
            console.log(resp);
            loadContent()
        }
        else
        {
            console.log("Failed to fetch history info");
        }

    }catch (error) {
        console.log(error);
    }

    if (table.value.length < 5)
    {
        height.value = table.value.length * 50 + 60
    }
    else
    {
        height.value = 310
    }
})

const loadContent = async () => {
    console.log("Loading content");
    // todo: modify this method to "GET"
    const module = await import("@toast-ui/editor");
    Editor = module.Editor;
    let c
    try
    {
        const response = await fetch('/api/getHistoryFile', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({ file: file.value, time: version.value})
        })

        
        if (response.ok)
        {
            let a = await response.json()
            c = a.content || ""
        }
        else
        {
            console.log(response);
            alert("failed to get content")
            router.push(redirectTo)
        }
    } catch (error)
    {
        console.log(error);
        router.push(redirectTo)
    }

    nextTick(() => {
                if (editorInstance.value)
                {
                    editorInstance.value.destroy()
                    editorInstance.value = null;
                }
                editorInstance.value = new Editor({
                    el: document.getElementById("editor"),
                    height: "600px",
                    initialEditType: "wysiwyg", // or "wysiwyg"
                    // initialEditType: "markdown", // or "wysiwyg"
                    previewStyle: "vertical", // "tab" or "vertical"
                    initialValue: c,
                    // initialValue: content,
                });
            })
}
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