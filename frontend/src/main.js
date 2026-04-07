import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
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
    // 从 localStorage 获取token并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
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

// 注册 Element Plus，配置中文语言
app.use(ElementPlus, {
  locale: zhCn,
})

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 挂载应用
app.mount('#app')