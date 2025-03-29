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
  const userName = ref("")

  const login = (name, role) => {
    userRole.value = role
    userName.value = name
  };

  const logout = () => {
    userRole.value = "logout"
  };

  return { userRole, userName, login, logout };
}, {
  persist: true
});