<template>
    <div v-if="!isVisitor">
        <h2 v-if="fileID">{{ form.fileName }}</h2>
        <h2 v-if="!fileID">待上传</h2>
        <el-form :model="form" label-width="auto" style="max-width: 600px;">
            <el-form-item v-if="fileID || selectedFile" label="文件名">
                <el-input :readonly="!canModifyScope || selectedFile" v-model="form.fileName" @change="modify"/>
            </el-form-item>
            <el-form-item v-if="fileID && !selectedFile" label="文件大小">
                <el-input :readonly="true" v-model="form.fileSize"/>
            </el-form-item>
            <el-form-item v-if="fileID || selectedFile" label="上传用户">
                <el-input :readonly="true" v-model="form.uploadUser"/>
            </el-form-item>
            <el-form-item v-if="fileID && !selectedFile" label="上传时间">
                <el-input :readonly="true" v-model="form.uploadDate"/>
            </el-form-item>
            <el-form-item v-if="fileID || selectedFile" label="可见范围">
                <el-radio-group :disabled="!canModifyScope" v-model="form.scope" @change="modify">
                    <el-radio value="public">公开</el-radio>
                    <el-radio value="lab">课题组成员</el-radio>
                    <el-radio value="private">仅自己</el-radio>
                </el-radio-group>
                <!-- <el-input  v-model="form.group"/> -->
            </el-form-item>
            <el-form-item :label="uploadText"  v-if="canModifyScope">
                <el-upload
                    class="upload-demo"
                    action=""
                    :limit="1"
                    :auto-upload="false"
                    :show-file-list="true"
                    @change="fileChange"
                    >
                    <el-button type="success">选择文件</el-button>
                </el-upload>
                <!-- :before-upload="" -->
            </el-form-item>
        </el-form>
        <el-button v-if="fileID || selectedFile" :disabled="!modified" type="primary" style="margin-top: 20px;" @click="save" :loading="uploading">{{ saveText }}</el-button>
        <el-button v-if="fileID" :disabled="!modified" style="margin-top: 20px; margin-left: 20px;" @click="cancel">取消修改</el-button>
        <el-popconfirm
        v-if="fileID && !selectedFile && canModifyScope"
        confirm-button-text="确认"
        cancel-button-text="取消"
        title="确认要删除吗？"
        @confirm="deleteFile"
    >
        <template #reference>
            <el-button   type="danger" style="margin-top: 20px;" >删除文件</el-button>
        </template>
    </el-popconfirm>
    </div>
    
    <div v-if="fileID && !selectedFile">
        <h2>下载</h2>
        <el-button type="text" @click="download">{{ form.fileName }}</el-button>
    </div>
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
const fileID = route.query.id

const canModifyScope = ref(false)
const modified = ref(false)
const selectedFile = ref(null)

const uploadText = ref("") 
const saveText = ref("")

const modify = () => {
    console.log("modified");
    modified.value = true
}

const uploading = ref(false)

const isVisitor = (status.userRole === "logout")

const cancel = () => {
    loadFileInfo()
}

const deleteFile = async() => {
    try{
        const response = await fetch('/api/deleteFile/' + fileID, { method: 'DELETE', credentials: 'include'})
        if (response.ok)
        {
            proxy.$message.success("删除成功")
            router.push("/wiki/fileList")
        }
        else
        {
            let resp = await response.json()
            proxy.$message.error(resp.error)
        }
    }catch (error)
    {
        console.log(error);
        proxy.$message.error("未知错误")
    }
}

const download = async () => {
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

        const a = document.createElement("a");
        a.href = url;
        a.download = form.value.fileName;
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

// const extractFilename = (response) => {
//       const contentDisposition = response.headers.get("Content-Disposition");
//       if (contentDisposition) {
//         const matches = contentDisposition.match(/filename="(.+)"/);
//         return matches ? matches[1] : "downloaded_file";
//       }
//       return "downloaded_file";
// }

const save = async () => {
    if (selectedFile.value == null)
    {
        updateMeta()
    }
    else if (fileID)
    {
        reUpload()
    }
    else
    {
        upload()
    }
}

const updateMeta = async() => {
    let response = await fetch('/api/updateFileMeta', { method: 'PUT', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            id: fileID,
            fileName: form.value.fileName,
            scope: form.value.scope,
        })

    })
    if (response.ok)
    {
        proxy.$message.success('修改成功')
        loadFileInfo()
    }
    else
    {
        let data = await response.json()
        proxy.$message.error('修改失败: ' + data.error)
    }
}

const fileChange = (file) => {
    selectedFile.value = file
    modified.value = true
    form.value.uploadUser = status.userName
    form.value.fileName = file.name
    form.value.scope = "lab"
    
    return false
}

const reUpload = async () => {
    let formData = new FormData();
      formData.append("file", selectedFile.value.raw);
      formData.append("id", fileID);
      formData.append("scope", form.value.scope);
    uploading.value = true
    try
    {
        let response = await fetch('/api/reUploadFile', { method: 'PUT', credentials: 'include',
            // headers: { 'Content-Type': 'multipart/form-data' },
            body: formData
        })
        if (response.ok)
        {
            proxy.$message.success('修改成功')
            loadFileInfo()
        }
        else if (response.status === 413)
        {
            proxy.$message.error("目前只允许上传500MB以内的文件")
        }
        else
        {
            let data = await response.json()
            proxy.$message.error(data.error)
        }
    }
    catch (error)
    {
        console.log(error);
    }
    uploading.value = false
}

const upload = async () => {
    let formData = new FormData();
      formData.append("file", selectedFile.value.raw);
      formData.append("user", form.value.uploadUser);
      formData.append("scope", form.value.scope);
      console.log(form.value.uploadUser)
    uploading.value = true
    try
    {
        let response = await fetch('/api/uploadFile', { method: 'POST', credentials: 'include',
            // headers: { 'Content-Type': 'multipart/form-data' },
            body: formData
        })
        if (response.ok)
        {
            proxy.$message.success('上传成功')
            let resp = await response.json()
            router.push({ path: '/wiki/file', query: { id: resp.id } })
            setTimeout(() => {
                location.reload(); // Force reload after the page navigation
            }, 300); 
            // fileID = resp.id
            // loadFileInfo()
        }
        else if (response.status === 413)
        {
            proxy.$message.error("目前只允许上传500MB以内的文件")
        }
        else
        {
            let data = await response.json()
            proxy.$message.error(data.error)
        }
    }
    catch (err)
    {
        console.log(err);
    }
    uploading.value = false
}

const loadFileInfo = async () => {

    try
    {
        const response = await fetch('/api/getFileInfo', {
          method: 'POST',
          credentials: 'include',  // Important: Allows cookies to be sent
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: fileID})
        })

        if (response.ok)
        {
            let resp = await response.json()
            form.value = {
                fileName: resp.file.fileName,
                fileSize: getFileSizeText(resp.file.fileSize),
                uploadUser: resp.file.uploadUser,
                uploadDate: resp.file.uploadDate,
                scope: resp.file.scope
            }
            // form.value = resp.file
            canModifyScope.value = (form.value.uploadUser === status.userName)
        }
        else
        {
            let resp = await response.json()
            proxy.$message.error(resp.error)
            if (response.status === 401 && isVisitor)
            {
                router.push('/wiki/login')
            }
        }
        
    }catch (error) {
        console.log(error);
        proxy.$message.error("未知错误")
    }
    modified.value = false

}

const getFileSizeText = (bytes) => {
    let num = bytes
    let units = ["Byte", "KB", "MB", "GB", "TB"]
    let idx = 0
    while (num > 1024)
    {
        num = num / 1024
        idx ++
    }
    let res = idx == 0? `${num} ${units[idx]}` : `${num.toFixed(2)} ${units[idx]}`
    return res
}

onMounted(async () => {
    console.log(fileID)
    if (fileID == undefined)
    {
        uploadText.value = "上传文件"
        saveText.value = "上传"
        canModifyScope.value = true
        if (status.userRole === "logout")
        {
            router.push({ path: '/wiki/login', query: { redirect: route.path } })
        }
    }
    else
    {
        loadFileInfo()
        uploadText.value = "重新上传"
        saveText.value = "保存修改"
    }
})
</script>