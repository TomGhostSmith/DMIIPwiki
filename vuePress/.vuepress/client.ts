import { defineClientConfig } from '@vuepress/client'
import ElementPlus from 'element-plus'
import { createPinia } from "pinia";
import 'element-plus/dist/index.css'
import login from "./src/login.vue"
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';


const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

export default defineClientConfig({
  enhance({ app }) {
    app.use(ElementPlus)  // ✅ Enable Element Plus globally
    app.use(pinia)
    app.component("login", login)
  }
})
