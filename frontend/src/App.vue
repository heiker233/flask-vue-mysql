<template>
  <div class="app-container">
    <!-- 未登录时显示登录页面 -->
    <Login v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
    
    <!-- 已登录时显示主应用界面 -->
    <el-container v-else style="height: 100vh">
      <el-aside width="200px" class="aside">
        <div class="logo">客户管理系统</div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical-demo"
          @select="handleMenuSelect"
        >
          <el-menu-item index="home">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="customers">
            <el-icon><User /></el-icon>
            <span>客户管理</span>
          </el-menu-item>
          <el-menu-item index="follow-ups">
            <el-icon><Message /></el-icon>
            <span>跟进记录</span>
          </el-menu-item>
          <el-menu-item index="deals">
            <el-icon><Money /></el-icon>
            <span>交易管理</span>
          </el-menu-item>
          <el-menu-item index="products">
            <el-icon><Box /></el-icon>
            <span>产品库</span>
          </el-menu-item>
          <el-menu-item index="stats">
            <el-icon><DataBoard /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
          <el-menu-item index="import">
            <el-icon><Upload /></el-icon>
            <span>数据导入</span>
          </el-menu-item>
          <el-menu-item v-if="isAdmin" index="users">
            <el-icon><Setting /></el-icon>
            <span>权限管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <span class="header-title">客户管理系统</span>
          <div class="header-user">
            <!-- 消息中心 -->
            <el-popover placement="bottom" :width="300" trigger="click" @show="fetchMessages">
              <template #reference>
                <el-badge :value="unreadCount" :max="99" class="msg-badge" :hidden="unreadCount === 0">
                  <el-icon class="msg-icon"><Bell /></el-icon>
                </el-badge>
              </template>
              <div class="msg-container">
                <div class="msg-header">
                  <span>消息通知</span>
                  <el-button type="text" size="small" @click="readAllMessages" v-if="unreadCount > 0">全部已读</el-button>
                </div>
                <div class="msg-list" v-loading="loadingMessages">
                  <div v-for="msg in messages" :key="msg.id" class="msg-item" :class="{ 'unread': !msg.is_read }" @click="readMessage(msg)">
                    <div class="msg-title">
                      <el-tag size="small" :type="getMsgTypeTag(msg.msg_type)">{{ msg.title }}</el-tag>
                      <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
                    </div>
                    <div class="msg-content">{{ msg.content }}</div>
                  </div>
                  <el-empty v-if="messages.length === 0" description="暂无消息" :image-size="60" />
                </div>
              </div>
            </el-popover>
            
            <el-text>欢迎, {{ currentUser.username }}</el-text>
            <el-button type="text" @click="logout">退出登录</el-button>
          </div>
        </el-header>
        <el-main class="main">
          <component :is="currentComponent" :current-user="currentUser" @navigate="handleNavigate" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { User, Message, Money, DataBoard, Setting, HomeFilled, Upload, Bell, Box } from '@element-plus/icons-vue'
import Login from './components/Login.vue'
import Home from './components/Home.vue'
import Customers from './components/Customers.vue'
import FollowUps from './components/FollowUps.vue'
import Deals from './components/Deals.vue'
import Stats from './components/Stats.vue'
import Users from './components/Users.vue'
import DataImport from './components/DataImport.vue'
import Products from './components/Products.vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 登录状态和用户信息
const isLoggedIn = ref(false)
const currentUser = ref({
  username: '',
  id: null,
  role: ''
})

const activeMenu = ref('home')

// 消息中心
const messages = ref([])
const loadingMessages = ref(false)
const unreadCount = computed(() => messages.value.filter(m => !m.is_read).length)
let messageTimer = null

const fetchMessages = async () => {
  if (!isLoggedIn.value || !currentUser.value.id) return
  loadingMessages.value = true
  try {
    const res = await axios.get('/api/messages', { params: { user_id: currentUser.value.id } })
    messages.value = res.data
  } catch (error) {
    console.error('获取消息失败', error)
  } finally {
    loadingMessages.value = false
  }
}

const readMessage = async (msg) => {
  if (msg.is_read) return
  try {
    await axios.put(`/api/messages/${msg.id}/read`)
    msg.is_read = true
  } catch (error) {
    console.error('标记已读失败', error)
  }
}

const readAllMessages = async () => {
  try {
    await axios.put('/api/messages/read_all', { user_id: currentUser.value.id })
    messages.value.forEach(m => m.is_read = true)
  } catch (error) {
    console.error('标记全部已读失败', error)
  }
}

const getMsgTypeTag = (type) => {
  const map = { 'deal': 'success', 'todo': 'danger', 'system': 'info' }
  return map[type] || 'info'
}

const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

// 判断当前用户是否为管理员
const isAdmin = computed(() => {
  return currentUser.value.role === 'admin'
})

// 如果非管理员访问权限管理页面，重定向到首页
const currentComponent = computed(() => {
  // 非管理员不能访问权限管理
  if (activeMenu.value === 'users' && !isAdmin.value) {
    activeMenu.value = 'home'
    ElMessage.warning('您没有权限访问此页面')
    return Home
  }
  switch (activeMenu.value) {
    case 'home':
      return Home
    case 'customers':
      return Customers
    case 'follow-ups':
      return FollowUps
    case 'deals':
      return Deals
    case 'products':
      return Products
    case 'stats':
      return Stats
    case 'import':
      return DataImport
    case 'users':
      return Users
    default:
      return Home
  }
})

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const handleNavigate = (route) => {
  activeMenu.value = route
}

const handleLoginSuccess = (user) => {
  // 设置登录状态和用户信息
  isLoggedIn.value = true
  currentUser.value = user
  
  // 保存到本地存储，刷新页面后仍保持登录状态
  localStorage.setItem('user', JSON.stringify(user))
  
  fetchMessages()
  messageTimer = setInterval(fetchMessages, 60000)
}

const logout = () => {
  // 清空登录状态
  isLoggedIn.value = false
  currentUser.value = {
    username: '',
    id: null,
    role: ''
  }
  // 清除用户信息和token
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  // 清除axios默认请求头
  delete axios.defaults.headers.common['Authorization']
  if (messageTimer) clearInterval(messageTimer)
  ElMessage.success('已退出登录')
}

// 初始化时检查本地存储是否有用户信息和token
const initUser = () => {
  const savedUser = localStorage.getItem('user')
  const savedToken = localStorage.getItem('token')
  
  if (savedUser && savedToken) {
    try {
      const user = JSON.parse(savedUser)
      isLoggedIn.value = true
      currentUser.value = user
      // 恢复axios请求头
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
      
      fetchMessages()
      messageTimer = setInterval(fetchMessages, 60000)
    } catch (e) {
      console.error('Failed to parse user from localStorage:', e)
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    }
  }
}

onUnmounted(() => {
  if (messageTimer) clearInterval(messageTimer)
})

// 初始化用户信息
initUser()
</script>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
}

.aside {
  background-color: #2c3e50;
  color: white;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  padding: 20px;
  border-bottom: 1px solid #34495e;
  color: white;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #3498db;
  color: white;
  padding: 0 20px;
}

.header-title {
  font-size: 24px;
  font-weight: bold;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main {
  padding: 20px;
}

.msg-badge {
  margin-right: 15px;
  cursor: pointer;
}

.msg-icon {
  font-size: 20px;
  color: white;
}

.msg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
  margin-bottom: 10px;
  font-weight: bold;
}

.msg-list {
  max-height: 300px;
  overflow-y: auto;
}

.msg-item {
  padding: 10px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.msg-item:hover {
  background-color: #f5f7fa;
}

.msg-item.unread {
  background-color: #fdf6ec;
}

.msg-item.unread:hover {
  background-color: #faecd8;
}

.msg-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.msg-time {
  font-size: 12px;
  color: #909399;
}

.msg-content {
  font-size: 13px;
  color: #606266;
}
</style>