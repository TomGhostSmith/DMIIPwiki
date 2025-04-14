import { defineClientConfig } from '@vuepress/client'
import ElementPlus from 'element-plus'
import { createPinia } from "pinia";
import 'element-plus/dist/index.css'
import login from "./src/login.vue"
import editor from "./src/editor.vue"
import profile from "./src/profile.vue"
import file from "./src/file.vue"
import userList from "./src/userList.vue"
import addUser from "./src/addUser.vue"
import approveUser from "./src/approveUser.vue"
import changePass from "./src/changePass.vue"
import forgetPass from "./src/forgetPass.vue"
import userOperation from "./src/userOperation.vue"
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import historyList from "./src/historyList.vue"
import fileList from "./src/fileList.vue"
import jumpToMain from "./src/jumpToMain.vue"
import { ElMessage } from 'element-plus'
// import { el } from 'element-plus/es/locales.mjs';




export default defineClientConfig({
  enhance({ app }) {
    const pinia = createPinia();
    app.use(ElementPlus)  // ✅ Enable Element Plus globally
    if (typeof window !== "undefined") {
      // alert("using persisted state");
      
      pinia.use(piniaPluginPersistedstate);
    }
    else
    {
      // alert("using temperal state");
    }
    app.use(pinia)
    app.component("login", login)
    app.component("editor", editor)
    app.component("profile", profile)
    app.component("file", file)
    app.component("user-list", userList)
    app.component("add-user", addUser)
    app.component("approve-user", approveUser)
    app.component("change-pass", changePass)
    app.component("forget-pass", forgetPass)
    app.component("user-operation", userOperation)
    app.component("history", historyList)
    app.component("file-list", fileList)
    app.component("jump-to-main", jumpToMain)
    app.config.globalProperties.$message = ElMessage;

    
  }
})
