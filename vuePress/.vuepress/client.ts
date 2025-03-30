import { defineClientConfig } from '@vuepress/client'
import ElementPlus from 'element-plus'
import { createPinia } from "pinia";
import 'element-plus/dist/index.css'
import login from "./src/login.vue"
import editor from "./src/editor.vue"
import profile from "./src/profile.vue"
import userList from "./src/userList.vue"
import addUser from "./src/addUser.vue"
import approveUser from "./src/approveUser.vue"
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
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
    app.component("user-list", userList)
    app.component("add-user", addUser)
    app.component("approve-user", approveUser)
    app.config.globalProperties.$message = ElMessage;

    
  }
})
