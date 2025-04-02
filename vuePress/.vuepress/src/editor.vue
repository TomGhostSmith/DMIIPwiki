<template>
    <el-dialog v-model="dialogVisible" title="文件列表" width="800">

    </el-dialog>
    <h2>页面属性</h2>
    <el-form :model="attrs" label-width="auto" style="max-width: 600px;">
        <el-form-item label="页面地址">
            <el-input :readonly="true" v-model="redirectTo"/>
        </el-form-item>
        <el-form-item label="页面标题">
            <el-input :disabled="!isAdmin" v-model="attrs.title"/>
        </el-form-item>
        <el-form-item label="谁可以阅读">
            <el-radio-group :disabled="!isAdmin" v-model="attrs.scope">
                <el-radio value="public">所有人</el-radio>
                <el-radio value="private">仅课题组成员</el-radio>
                <el-radio value="admin">仅管理员</el-radio>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="谁可以编辑">
            <el-radio-group :disabled="!isAdmin" v-model="attrs.modification">
                <el-radio value="private">所有课题组成员</el-radio>
                <el-radio value="admin">仅管理员</el-radio>
            </el-radio-group>
        </el-form-item>
        <hr>
        <!-- <el-form-item label="最后修改">
            <el-input :readonly="true" v-model=""/>
        </el-form-item> -->
    </el-form>
    <p>最后修改：{{ attrs.lastModify }} {{ attrs.lastModifyDate }}</p>
    <!-- <span>Title:</span>
    <el-input style="display: inline;margin-left: 10px;" v-model="attrs.title"/>
    <br>
    <span>Visible:</span>
    <el-input style="display: inline;margin-left: 10px;" v-model="attrs.scope"/>
    <br>
    
    <span>Editable:</span>
    <el-input style="display: inline;margin-left: 10px;" v-model="attrs.modification"/>
    <br> -->
    <h2>添加文件链接</h2>
    <!-- <el-button type="primary" @click="showFiles"  style="margin-top: 20px">上传文件</el-button> -->
    <!-- <el-button type="primary" @click="showFiles"  style="margin-top: 20px">选择文件</el-button> -->
    <!-- <p>还没有上传？<el-button type="text" style="display: inline; font-size: 16px;">点击此处</el-button>去上传文件</p> -->
    <p>还没有上传？
        <router-link to="/wiki/file.html"><el-button type="text" style="font-size: 16px;margin-top: -2px;">点击此处</el-button></router-link>
         去上传文件</p>
    <file-list/>
    <h2>正文</h2>
    <div id="editor" style="margin-top: 20px"></div>
    <el-button type="primary" :loading="isSaving" style="margin-top: 20px;" @click="saveContent">保存</el-button>
    <el-button :loading="isSaving" style="margin-top: 20px; margin-left: 20px;" @click="cancel">取消</el-button>
</template>
<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vuepress/client'
import '@toast-ui/editor/dist/toastui-editor.css'

import { userStatus } from "../globalStatus.js"

const { proxy } = getCurrentInstance();

const status = userStatus()

const mounted = ref(false)
const editorInstance = ref(null)
const route = useRoute()
const router = useRouter()
const file = ref("")
const redirectTo = route.query.redirect || '/'
const newPage = route.query.create === "true"
const attrs = ref({url: "", title: "", scope: "", modification: ""})
const isSaving = ref(false)
const dialogVisible = ref(false)

let Editor
const isAdmin = ref(false)

const showFiles = () => {
    dialogVisible.value = true
}

const loadContent = async () => {
    console.log("Loading content");
    // todo: modify this method to "GET"
    const module = await import("@toast-ui/editor");
    Editor = module.Editor;
    let c
    if (newPage)
    {
        c = ""
        let terms = file.value.split("/")
        let titleName = terms[terms.length - 1]
        console.log(titleName);
        attrs.value = {title: titleName.substring(0, titleName.length - 3), scope: "private", modification: "admin", md5: "", lastModify: "", lastModifyDate: ""}
    }
    else
    {
        try
        {
            const response = await fetch('/api/loadContent', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({ fileName: file.value})
            })
    
            
            if (response.ok)
            {
                let a = await response.json()
                c = a.content || ""
                attrs.value = a.attrs
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

const saveContent = async() => {

    const now = new Date();
    
    // Get YYYY-MM-DD HH-mm
    const datePart = now.toISOString().split('T')[0]; // YYYY-MM-DD
    const timePart = now.toTimeString().split(' ')[0]; // HH-mm

    // Get timezone abbreviation
    const timeZone = Intl.DateTimeFormat('en-US', { timeZoneName: 'short' })
        .formatToParts(now)
        .find(part => part.type === 'timeZoneName').value;

    isSaving.value = true
    console.log(editorInstance.value.getMarkdown())
    console.log(attrs.value)
    try {
        attrs.value.lastModify = status.userName
        attrs.value.lastModifyDate = `${datePart} ${timePart} ${timeZone}`
        console.log({ fileName: file.value, 
            "content": editorInstance.value.getMarkdown(),
        "attrs": attrs.value});
        const response = await fetch('/api/saveContent', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({ fileName: file.value, 
                "content": editorInstance.value.getMarkdown(),
            "attrs": attrs.value})
            
        })

        if (response.ok)
        {
            proxy.$message.success('保存成功')
            router.push(redirectTo)
            setTimeout(() => {
                location.reload(); // Force reload after the page navigation
            }, 300); 
        }
        else if (response.status == 409)
        {
            proxy.$message.error('页面已被他人修改，请复制修改内容并刷新页面')
        }
        else
        {
            console.log(response);
            proxy.$message.error('未知错误')
        }
    } catch (error)
    {
        console.log(error);
        proxy.$message.error('未知错误')
        
    }
    isSaving.value = false
}

const cancel = () => {
    router.push(redirectTo)
}

onBeforeUnmount(() => {
    if (editorInstance.value)
    {
        editorInstance.value.destroy()
        editorInstance.value = null;
    }
})

onMounted(() => {
    mounted.value = true
    console.log(redirectTo);
    isAdmin.value = (status.userRole === "admin")
    let fileName = redirectTo.replace(".html", ".md")
    if (fileName.charAt(redirectTo.length - 1) == "/")
    {
        fileName = fileName + "index.md"
    }
    fileName = "." + fileName
    file.value = fileName
    console.log(fileName);

    


    // nextTick(() => {
    //     if (!editorInstance.value)
    //     {
    //         editorInstance.value = new Editor({
    //             el: document.getElementById("editor"),
    //             height: "400px",
    //             initialEditType: "wysiwyg", // or "wysiwyg"
    //             // initialEditType: "markdown", // or "wysiwyg"
    //             previewStyle: "vertical", // "tab" or "vertical"
    //             initialValue: "Hello, **Toast UI Editor**!",
    //             // initialValue: content,
    //         });
    //     }
    // })

    loadContent()

//   new EditorJS({
//     holder: 'editorjs',
//     tools: {
//       header: Header,
//       list: List,
//       image: Image
//     }
//   })
})
</script>