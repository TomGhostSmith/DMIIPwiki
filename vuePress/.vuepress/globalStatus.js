import { defineStore } from "pinia";
import { ref } from "vue";


export const userStatus = defineStore("user", {
  state: () => ({
    userRole: 'logout'
  }),

  actions: {
    login(role) {
      this.userRole = role
    },
    logout(){
      this.userRole = 'logout'
    }
  },
  persist: true
})

// export const userStatus = defineStore("user", () => {
//   const userRole = ref("logout");

//   const login = (role) => {
//   };

//   const logout = () => {
//     userRole.value = "logout"
//   };

//   return { userRole, login, logout };
// });