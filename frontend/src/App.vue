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
          <el-menu-item index="stats">
            <el-icon><DataBoard /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
          <el-menu-item index="users">
            <el-icon><Setting /></el-icon>
            <span>权限管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <span class="header-title">客户管理系统</span>
          <div class="header-user">
            <el-text>欢迎, {{ currentUser.username }}</el-text>
            <el-button type="text" @click="logout">退出登录</el-button>
          </div>
        </el-header>
        <el-main class="main">
          <component :is="currentComponent" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { User, Message, Money, DataBoard, Setting } from '@element-plus/icons-vue'
import Login from './components/Login.vue'
import Customers from './components/Customers.vue'
import FollowUps from './components/FollowUps.vue'
import Deals from './components/Deals.vue'
import Stats from './components/Stats.vue'
import Users from './components/Users.vue'
import { ElMessage } from 'element-plus'

// 登录状态和用户信息
const isLoggedIn = ref(false)
const currentUser = ref({
  username: '',
  id: null,
  role: ''
})

const activeMenu = ref('customers')


const currentComponent = computed(() => {
  switch (activeMenu.value) {
    case 'customers':
      return Customers
    case 'follow-ups':
      return FollowUps
    case 'deals':
      return Deals
    case 'stats':
      return Stats
    case 'users':
      return Users
    default:
      return Customers
  }
})

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const handleLoginSuccess = (user) => {
  // 设置登录状态和用户信息
  isLoggedIn.value = true
  currentUser.value = user
  
  // 保存到本地存储，刷新页面后仍保持登录状态
  localStorage.setItem('user', JSON.stringify(user))
}

const logout = () => {
  // 清空登录状态
  isLoggedIn.value = false
  currentUser.value = {
    username: '',
    id: null,
    role: ''
  }
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
}

// 初始化时检查本地存储是否有用户信息
const initUser = () => {
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    try {
      const user = JSON.parse(savedUser)
      isLoggedIn.value = true
      currentUser.value = user
    } catch (e) {
      console.error('Failed to parse user from localStorage:', e)
      localStorage.removeItem('user')
    }
  }
}

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
</style>