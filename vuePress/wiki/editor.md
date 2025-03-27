---
title: editor
scope: public
modification: admin
---
<div>
editor
<!-- <teditor v-if="mounted" v-model="content" :initialEditType="'markdown'" :height="'500px'" /> -->

 <div id="editor"></div>
end of editor
</div>


<script setup>
import { ref, onMounted } from 'vue'
import { Editor } from '@toast-ui/editor'
import '@toast-ui/editor/dist/toastui-editor.css'
// import EditorJS from '@editorjs/editorjs'
// import Header from '@editorjs/header'
// import List from '@editorjs/list'
// import Image from '@editorjs/image'

const mounted = ref(false)
const content = ref('')
const editorInstance = ref(null)
onMounted(() => {
  mounted.value = true

    editorInstance.value = new Editor({
    el: document.getElementById("editor"),
    height: "400px",
    initialEditType: "wysiwyg", // or "wysiwyg"
    previewStyle: "vertical", // "tab" or "vertical"
    initialValue: "Hello, **Toast UI Editor**!",
  });

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