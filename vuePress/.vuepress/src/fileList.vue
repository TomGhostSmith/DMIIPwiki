<template>
    <el-table :data="table" style="" :fit="true" >
        <el-table-column prop="fileName" label="文件名" min-width="200px"/>
        <el-table-column prop="uploadDate" label="上传时间" width="200px"/>
        <el-table-column prop="uploadUser" label="上传用户" width="100px"/>
        <el-table-column prop="fileSize" label="文件大小" width="100px"/>
        <el-table-column v-if="!showSelect" label="操作" width="120px">
            <template #default="scope">
                <el-button type="text" @click="detail(scope.row.id)">查看</el-button>
                <el-button type="text" @click="download(scope.row.id, scope.row.fileName)">下载</el-button>
            </template>
        </el-table-column>
        <el-table-column v-if="showSelect" label="操作" width="100px">
            <template #default="scope">
                <el-button type="text" @click="copuLink(scope.row.id)">复制链接</el-button>
            </template>
        </el-table-column>
    </el-table>
</template>
<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, getCurrentInstance } from 'vue'
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

const { proxy } = getCurrentInstance()

const redirectTo = route.query.redirect || '/'
let Editor

const detail = (fileID) =>
{
    console.log(fileID)
    let routeData = router.resolve({path: "/wiki/file.html", query: { "id": fileID }})
    console.log(routeData)
    window.open(routeData.href, '_blank')
}

const showSelect = route.path === "/wiki/editor.html"


const getFileSizeText = (bytes) => {
    let num = bytes
    let units = ["B", "KB", "MB", "GB", "TB"]
    let idx = 0
    while (num > 1024)
    {
        num = num / 1024
        idx ++
    }
    let res = idx == 0? `${num} ${units[idx]}` : `${num.toFixed(2)} ${units[idx]}`
    return res
}


const download = async (fileID, fileName) => {
    try {
        const response = await fetch(`/api/downloadFile/${fileID}`);

        if (!response.ok) {
            let data = await response.json()
            proxy.$message.error('下载失败: ' + data.error)
        }
        // Convert response to arrayBuffer first (handles large files better)
        const arrayBuffer = await response.arrayBuffer();
        const blob = new Blob([arrayBuffer]); 
        const url = window.URL.createObjectURL(blob);

        // const blob = await response.blob();
        // const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        proxy.$message.success("开始下载");
      } catch (error) {
        console.error("Download error:", error);
        proxy.$message.error("未知错误");
      }
}

onMounted(async () => {

    try
    {
        const response = await fetch('/api/getLabFiles', {
          method: 'GET',
          credentials: 'include',  // Important: Allows cookies to be sent
        })

        if (response.ok)
        {
            let resp = await response.json()
            let res = []
            for (let i= 0;i < resp.data.length;i++)
            {
                res.push({
                    id: resp.data[i].id,
                    fileName: resp.data[i].fileName,
                    uploadDate: resp.data[i].uploadDate,
                    uploadUser: resp.data[i].uploadUser,
                    fileSize: getFileSizeText(resp.data[i].fileSize)
                })
            }
            table.value = res
            // table.value = resp.data
        }
        else
        {
            console.log("Failed to fetch history info");
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