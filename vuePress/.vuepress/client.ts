import { defineClientConfig } from '@vuepress/client'
import ElementPlus from 'element-plus'
import { createPinia } from "pinia";
import 'element-plus/dist/index.css'
import login from "./src/login.vue"
import editor from "./src/editor.vue"
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
// import { el } from 'element-plus/es/locales.mjs';




export default defineClientConfig({
  enhance({ app }) {
    const pinia = createPinia();
    app.use(ElementPlus)  // ✅ Enable Element Plus globally
    if (typeof window !== "undefined") {
      alert("using persisted state");
      
      pinia.use(piniaPluginPersistedstate);
    }
    else
    {
      alert("using temperal state");
    }
    app.use(pinia)
    app.component("login", login)
    app.component("editor", editor)
  }
})
