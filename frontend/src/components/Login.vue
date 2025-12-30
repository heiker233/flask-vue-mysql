<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo">客户管理系统</div>
      <div class="form-tabs">
        <el-tabs v-model:active-name="activeTab" @tab-click="resetForms">
          <el-tab-pane label="登录" name="login"></el-tab-pane>
          <el-tab-pane label="注册" name="register"></el-tab-pane>
        </el-tabs>
      </div>

      <!-- 登录表单 -->
      <el-form
        v-if="activeTab === 'login'"
        :model="loginForm"
        label-width="80px"
        class="login-form"
      >
        <el-form-item label="用户名" prop="username" required>
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
          ></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password" required>
          <el-input
            v-model="loginForm.password"
            placeholder="请输入密码"
            type="password"
            prefix-icon="Lock"
          ></el-input>
        </el-form-item>
        <el-form-item class="form-actions">
          <el-button type="primary" @click="login" class="submit-btn">
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 注册表单 -->
      <el-form
        v-else
        :model="registerForm"
        label-width="80px"
        class="register-form"
      >
        <el-form-item label="用户名" prop="username" required>
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（至少3个字符）"
            prefix-icon="User"
          ></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password" required>
          <el-input
            v-model="registerForm.password"
            placeholder="请输入密码（至少6个字符）"
            type="password"
            prefix-icon="Lock"
          ></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword" required>
          <el-input
            v-model="registerForm.confirmPassword"
            placeholder="请再次输入密码"
            type="password"
            prefix-icon="Lock"
          ></el-input>
        </el-form-item>
        <el-form-item class="form-actions">
          <el-button type="primary" @click="register" class="submit-btn">
            注册
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['login-success'])

const activeTab = ref('login')
const loginForm = ref({
  username: '',
  password: ''
})
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const login = async () => {
  try {
    if (!loginForm.value.username || !loginForm.value.password) {
      ElMessage.error('请填写完整的登录信息')
      return
    }

    const response = await axios.post('/api/login', loginForm.value)
    if (response.data.success) {
      ElMessage.success('登录成功')
      emit('login-success', response.data.user)
    } else {
      ElMessage.error(response.data.message || '登录失败')
    }
  } catch (error) {
    console.error('登录失败:', error)
    const errorMessage = error.response?.data?.message || '登录失败，请稍后重试'
    ElMessage.error(errorMessage)
  }
}

const register = async () => {
  try {
    if (!registerForm.value.username || !registerForm.value.password || !registerForm.value.confirmPassword) {
      ElMessage.error('请填写完整的注册信息')
      return
    }

    if (registerForm.value.password !== registerForm.value.confirmPassword) {
      ElMessage.error('两次输入的密码不一致')
      return
    }

    if (registerForm.value.username.length < 3) {
      ElMessage.error('用户名长度至少为3个字符')
      return
    }

    if (registerForm.value.password.length < 6) {
      ElMessage.error('密码长度至少为6个字符')
      return
    }

    const registerData = {
      username: registerForm.value.username,
      password: registerForm.value.password
    }

    const response = await axios.post('/api/register', registerData)
    if (response.data.success) {
      ElMessage.success('注册成功，已自动登录')
      emit('login-success', response.data.user)
    } else {
      ElMessage.error(response.data.message || '注册失败')
    }
  } catch (error) {
    console.error('注册失败:', error)
    const errorMessage = error.response?.data?.message || '注册失败，请稍后重试'
    ElMessage.error(errorMessage)
  }
}

const resetForms = () => {
  loginForm.value = {
    username: '',
    password: ''
  }
  registerForm.value = {
    username: '',
    password: '',
    confirmPassword: ''
  }
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  background-color: white;
  border-radius: 10px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.logo {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: #3498db;
}

.form-tabs {
  margin-bottom: 30px;
}

.login-form,
.register-form {
  margin-top: 20px;
}

.form-actions {
  margin-top: 30px;
}

.submit-btn {
  width: 100%;
}
</style>