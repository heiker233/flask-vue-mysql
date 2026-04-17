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
      console.log('用户未登录或登录过期，需要重新登录')
      // 清除本地 token 缓存，防止持续发送无效请求
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete axios.defaults.headers.common['Authorization']
      
      // 触发全局事件，让 App.vue 捕获并强制退出到登录页
      window.dispatchEvent(new CustomEvent('unauthorized'))
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