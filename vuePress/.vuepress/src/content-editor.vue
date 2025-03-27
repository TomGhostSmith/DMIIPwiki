<template>
 <div id="editor"></div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
// import pkg from '@toast-ui/editor'
// import { Editor } from '@toast-ui/editor'  // for dev
// import '@toast-ui/editor/dist/toastui-editor.css'

// import 'codemirror/lib/codemirror.css'
import '@toast-ui/editor/dist/toastui-editor.css'
// import defaultOptions from './default-options'
                        
// const { Editor } = pkg
const mounted = ref(false)
const content = ref('')
const editorInstance = ref(null)
let Editor
onMounted(async () => {
  const module = await import("@toast-ui/editor");
  Editor = module.Editor;

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