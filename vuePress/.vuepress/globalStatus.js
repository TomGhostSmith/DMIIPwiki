import { defineStore } from "pinia";
import { ref } from "vue";


// export const userStatus = defineStore("user", {
//   state: () => ({
//     userRole: 'logout'
//   }),

//   actions: {
//     login(role) {
//       this.userRole = role
//     },
//     logout(){
//       this.userRole = 'logout'
//     }
//   },
//   persist: {
//     enabled: true,
//     strategies: [
//       {
//         key: 'user-status',  // Custom key for storing the data
//         storage: localStorage,  // You can use sessionStorage as well
//       }
//     ]
//   }
// })

export const userStatus = defineStore("user", () => {
  const userRole = ref("logout");

  const login = (role) => {
    userRole.value = role
  };

  const logout = () => {
    userRole.value = "logout"
  };

  return { userRole, login, logout };
}, {
  persist: true
});