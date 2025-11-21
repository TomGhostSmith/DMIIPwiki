<template>
    <div v-if="!isVisitor">
        <splitpanes style="height: 100%;">
    <pane min-size="20">
      <el-main style="height: 100%;padding:0">
          <splitpanes horizontal>
            <pane min-size="20">
                <h2>{{ form.fileName }}</h2>
                    <video
                    ref="videoRef"
                      controls
                      style="width: 100%; max-height: 80%;"
                      @timeupdate="onTimeUpdate"
                    ></video>
            </pane>
            <pane min-size="20">
              <h2>Meeting info</h2>
            </pane>
          </splitpanes>
        </el-main>
      </pane>
      <pane min-size="20" max-size="60" size="20">
        <el-aside style="height: 100%; width: 100%">
        <h2>Transcript</h2>
        <div style="text-align: left; padding: 20px">
          <div v-for="(seg, t) in scripts" :key="t" >
            <p class="speaker">{{ seg[0] }}: </p>
            <p>
              <span class="script" v-for="(s, t) in seg[1]" :key="t" :style="getColor(s[1], s[2])" @click="jumpTo(s[1])">{{ s[0] }}</span>
            </p>
          </div>
        </div>
        
      </el-aside>
    </pane>
    
  </splitpanes>
    </div>
</template>
<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import { userStatus } from "../globalStatus.js"
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import Hls from 'hls.js';

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

const scripts = ref([])
const hls = ref(null)
const currentTime = ref(0)
const videoRef = ref(null);

const uploading = ref(false)

const isVisitor = (status.userRole === "logout")

const cancel = () => {
    loadFileInfo()
}


const copyLink = () => {
    // const code = `<a href="http://10.138.42.155:9003/wiki/file?id=${fileID}">${fileName}</a>`
    // const blob = new Blob([code], {type: 'text/html'})
    // const clipboardItem = new ClipboardItem({'text/html': blob})

    // navigator.clipboard.write([clipboardItem])
    // .then(() => { proxy.$message.success("复制成功") })
    // .catch(err => {proxy.$message.error("复制失败"); console.log(err)})
    let fileName = form.fileName
    try
    {
        let url = `http://10.138.42.155:9003/wiki/file.html?id=${fileID}`
        const tempElement = document.createElement('div');
        tempElement.innerHTML = `<a href="${url}">${url}</a>`;  // replace "_" to avoid unwanted long unwrap file names
        document.body.appendChild(tempElement);
    
        const range = document.createRange();
        range.selectNodeContents(tempElement);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
    
        document.execCommand('copy'); // Copies the formatted hyperlink
        document.body.removeChild(tempElement);
        proxy.$message.success("复制成功")
    } catch (err)
    {
        proxy.$message.error("复制失败"); 
        console.log(err)
    }
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

        const video = videoRef.value
        let videoSrc = '/api/file/' + form.value.fileName.replace('mp4', '') + '/' + form.value.fileName.replace('mp4', '.m3u8')
        

        if (Hls.isSupported()) {
        hls.value = new Hls()
        hls.value.loadSource(videoSrc)
        hls.value.attachMedia(video)
        hls.value.on(Hls.Events.MANIFEST_PARSED, () => {
            hls.value.subtitleTrack = 0;
        //   console.log("Hi!!!");
        //   video.play()
        })
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        console.log("Hello!!!");
        video.src = videoSrc
        // video.addEventListener('loadedmetadata', () => {
        //   video.play()
        // })
        }

        const response2 = await fetch('/api/getScript/' + form.value.fileName.replace('mp4', ''), {
          method: 'GET',
          credentials: 'include',  // Important: Allows cookies to be sent
          headers: { 'Content-Type': 'application/json' },
        })

        if (response2.ok)
        {
            scripts.value = resp.data
        }

    }catch (error) {
        console.log(error);
        proxy.$message.error("未知错误")
    }
    modified.value = false

}

const getColor = (t1, t2) =>
{
        
        let _this = this        
        if ((t1 <= _this.currentTime) && (t2 > _this.currentTime))
        {
          return {background: "#fbbf69"}
        }
        else
        {
          return {}
        }
}
const onTimeUpdate = () => {
        
        currentTime = videoRef.value.currentTime;
        // console.log(this.currentTime);
}
const jumpTo = (t) => {
    videoRef.value.currentTime = t
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

onBeforeUnmount(async () => {
    if (hls.value) {
      hls.value.destroy();
    }
})
</script>