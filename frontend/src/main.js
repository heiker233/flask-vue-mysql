import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import axios from 'axios'

const app = createApp(App)

// 配置 Axios
// 不要设置 baseURL，这样请求会正确传递给代理
// axios.defaults.baseURL = '/api'

// Axios 拦截器
// 请求拦截器
axios.interceptors.request.use(
  (config) => {
    // 这里可以添加认证令牌等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axios.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 处理401未授权等错误
    if (error.response?.status === 401) {
      console.log('用户未登录，需要重新登录')
    }
    return Promise.reject(error)
  }
)

// 全局配置 Axios
app.config.globalProperties.$http = axios

// 注册 Element Plus
app.use(ElementPlus)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 挂载应用
app.mount('#app')