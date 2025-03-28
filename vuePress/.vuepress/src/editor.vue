<template>
    <span>Title:</span>
    <el-input style="display: inline;margin-left: 10px;" v-model="attrs.title"/>
    <br>
    <span>Visible:</span>
    <el-input style="display: inline;margin-left: 10px;" v-model="attrs.scope"/>
    <br>
    
    <span>Editable:</span>
    <el-input style="display: inline;margin-left: 10px;" v-model="attrs.modification"/>
    <br>

    <div id="editor" style="margin-top: 20px"></div>
    <el-button type="primary" style="margin-top: 20px;" @click="saveContent">Save</el-button>
    <el-button style="margin-top: 20px; margin-left: 20px;" @click="cancel">Cancel</el-button>
</template>
<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
// import { Editor } from '@toast-ui/editor'
// import Editor from '@toast-ui/editor'
import { useRoute, useRouter } from 'vuepress/client'
import '@toast-ui/editor/dist/toastui-editor.css'
// import EditorJS from '@editorjs/editorjs'
// import Header from '@editorjs/header'
// import List from '@editorjs/list'
// import Image from '@editorjs/image'

const mounted = ref(false)
const editorInstance = ref(null)
const route = useRoute()
const router = useRouter()
const file = ref("")
const redirectTo = route.query.redirect || '/'
const attrs = ref({title: "", scope: "", modification: ""})

const loadContent = async () => {
    // todo: modify this method to "GET"
    const module = await import("@toast-ui/editor");
    Editor = module.Editor;
    try
    {
        const response = await fetch('http://localhost:5000/api/loadContent', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({ fileName: file.value})
        })

        if (response.ok)
        {
            

            let a = await response.json()
            let c = a.content || ""
            attrs.value = a.attrs

            nextTick(() => {
        if (!editorInstance.value)
        {
            editorInstance.value = new Editor({
                el: document.getElementById("editor"),
                height: "600px",
                initialEditType: "wysiwyg", // or "wysiwyg"
                // initialEditType: "markdown", // or "wysiwyg"
                previewStyle: "vertical", // "tab" or "vertical"
                initialValue: c,
                // initialValue: content,
            });
        }
    })
            // console.log(a.content);
            // setTimeout(() => {
            //     if (editorInstance.value)
            //     {
            //         editorInstance.value.reset()
            //         editorInstance.value.setMarkdown(c)
            //     }
            //     else
            //     {
            //         console.log("editor instance not initialized");
                    
            //     }
            // }, 1000);
            // content.value = a.content
            
        }
        else
        {
            console.log(response);
            
            alert("failed to get content")
        }
    } catch (error)
    {
        console.log(error);
    }
}

const saveContent = async() => {
    try {
        console.log({ fileName: file.value, 
            "content": editorInstance.value.getMarkdown(),
        "attrs": attrs.value});
        const response = await fetch('http://localhost:5000/api/saveContent', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({ fileName: file.value, 
                "content": editorInstance.value.getMarkdown(),
            "attrs": attrs.value})
            
        })

        if (response.ok)
        {
            alert("saved")
            router.push(redirectTo)
        }
        else
        {
            console.log(response);
            
            alert("failed to get content")
        }
    } catch (error)
    {
        console.log(error);
        
    }
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