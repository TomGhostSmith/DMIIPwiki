<template>
    <div v-if="!isVisitor">
        <splitpanes style="height: 80vh;">
            <pane min-size="20">
                <el-main style="height: 100%;padding:0">
                    <splitpanes horizontal>
                        <pane min-size="20">
                                <video
                                ref="videoRef"
                                controls
                                style="width: calc(100% - 10px); max-height: calc(100% - 10px);"
                                @timeupdate="onTimeUpdate"
                                ></video>
                        </pane>
                        <pane min-size="20" style="overflow: scroll">
                        <h2>视频信息</h2>
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
                            <el-form-item v-if="fileID && !selectedFile" label="下载">
                                <el-button type="primary" @click="copyLink" style="display: block">复制链接</el-button>
                                <el-button type="text" @click="download">下载 {{ form.fileName }}</el-button>
                            </el-form-item>
                        </el-form>
                        </pane>
                    </splitpanes>
                </el-main>
            </pane>
            <pane min-size="20" max-size="60" size="20">
                <el-aside style="height: 100%; width: 100%;padding: 0 20px 0; overflow: hidden;">
                    <h2>文字记录</h2>
                    <div style="text-align: left; padding: 20px; height: 70vh; overflow: scroll;">
                        <div v-for="(seg, t) in scripts" :key="t" >
                            <p>
                                <span class="speaker">{{ seg[0] + ' ' }} </span>
                                <span>{{ formatTime(seg[1][0][1]) }} </span>
                            </p>
                            <p>
                            <span class="script" v-for="(s, t) in seg[1]" :key="t" :style="getColor(s[1], s[2])" @click="jumpTo(s[1])">{{ s[0] + ' ' }}</span>
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
    let fileName = form.fileName
    try
    {
        let url = `http://10.176.64.122/wiki/video.html?id=${fileID}`
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
        let videoSrc = '/api/file/' + form.value.fileName.replace('.mp4', '') + '/' + form.value.fileName.replace('.mp4', '.m3u8')
        

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

        const response2 = await fetch('/api/getScript/' + form.value.fileName.replace('.mp4', ''), {
          method: 'GET',
          credentials: 'include',  // Important: Allows cookies to be sent
          headers: { 'Content-Type': 'application/json' },
        })

        if (response2.ok)
        {
            scripts.value = await response2.json()
        }

    }catch (error) {
        console.log(error);
        proxy.$message.error("未知错误")
    }
    modified.value = false

}

const getColor = (t1, t2) =>
{
        
        if ((t1 <= currentTime.value) && (t2 > currentTime.value))
        {
          return {background: "#ffff69"}
        }
        else
        {
          return {}
        }
}
const onTimeUpdate = () => {
    currentTime.value = videoRef.value.currentTime;
    // console.log(currentTime.value);
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

const formatTime = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);   // or Math.round if you prefer

  return `${hours}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
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
    }

})

onBeforeUnmount(async () => {
    if (hls.value) {
      hls.value.destroy();
    }
})
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>

.splitpanes--vertical > .splitpanes__splitter {
  background-color: #dcdfe6; /* show a visible divider */
  width: 4px;                /* thickness of the bar */
  cursor: col-resize;        /* cursor for resizing */
  transition: background-color 0.2s;
}

.splitpanes--horizontal > .splitpanes__splitter {
  background-color: #dcdfe6; /* show a visible divider */
  height: 4px;                /* thickness of the bar */
  cursor: row-resize;        /* cursor for resizing */
  transition: background-color 0.2s;
}

.splitpanes__splitter:hover {
  background-color: #409EFF; /* highlight when hovered */
}

.fileItem{
  font-size: 20px!important;
}

.speaker{
  font-size: 20px;
  font-weight: bold
}
.script{
  cursor: pointer;
  font-size: 18px
}

.script:hover
{
  background-color: #ffff69;
}

    
</style>

<style lang="scss" scoped>
[vp-content]
{
    & {
        max-width: calc(100% - 5rem)!important;
    }
}
</style>