<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo">客户管理系统</div>
      <div class="form-tabs">
        <el-tabs v-model="activeTab" @tab-click="resetForms">
          <el-tab-pane label="登录" name="login"></el-tab-pane>
          <el-tab-pane label="注册" name="register"></el-tab-pane>
        </el-tabs>
      </div>

      <!-- 登录表单 -->
      <el-form
        v-if="activeTab === 'login'"
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
        class="login-form"
        @keyup.enter="login"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
          ></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="请输入密码"
            type="password"
            prefix-icon="Lock"
            show-password
            clearable
          ></el-input>
        </el-form-item>
        <el-form-item class="form-actions">
          <el-button type="primary" @click="login" class="submit-btn" :loading="loginLoading">
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 注册表单 -->
      <el-form
        v-else
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="100px"
        class="register-form"
        @keyup.enter="register"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（3-20个字符）"
            prefix-icon="User"
            clearable
            maxlength="20"
            show-word-limit
          ></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            placeholder="请输入密码（6-20个字符）"
            type="password"
            prefix-icon="Lock"
            show-password
            clearable
            maxlength="20"
          ></el-input>
          <div class="password-strength" v-if="registerForm.password">
            <span>密码强度：</span>
            <el-tag :type="passwordStrength.type" size="small">{{ passwordStrength.text }}</el-tag>
          </div>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            placeholder="请再次输入密码"
            type="password"
            prefix-icon="Lock"
            show-password
            clearable
            maxlength="20"
          ></el-input>
        </el-form-item>
        <el-form-item class="form-actions">
          <el-button type="primary" @click="register" class="submit-btn" :loading="registerLoading">
            注册
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['login-success'])

const activeTab = ref('login')
const loginFormRef = ref(null)
const registerFormRef = ref(null)
const loginLoading = ref(false)
const registerLoading = ref(false)

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

// 登录表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应为6-20个字符', trigger: 'blur' }
  ]
}

// 自定义验证：确认密码
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.value.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 自定义验证：用户名格式
const validateUsername = (rule, value, callback) => {
  const reg = /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/
  if (!reg.test(value)) {
    callback(new Error('用户名只能包含字母、数字、下划线和中文'))
  } else {
    callback()
  }
}

// 注册表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' },
    { validator: validateUsername, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应为6-20个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 计算密码强度
const passwordStrength = computed(() => {
  const password = registerForm.value.password
  if (!password) {
    return { type: 'info', text: '未输入' }
  }
  
  let strength = 0
  // 长度检查
  if (password.length >= 8) strength++
  if (password.length >= 10) strength++
  // 包含数字
  if (/\d/.test(password)) strength++
  // 包含小写字母
  if (/[a-z]/.test(password)) strength++
  // 包含大写字母
  if (/[A-Z]/.test(password)) strength++
  // 包含特殊字符
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++
  
  if (strength <= 2) {
    return { type: 'danger', text: '弱' }
  } else if (strength <= 4) {
    return { type: 'warning', text: '中' }
  } else {
    return { type: 'success', text: '强' }
  }
})

const login = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loginLoading.value = true
      try {
        const response = await axios.post('/api/login', loginForm.value)
        if (response.data.success) {
          // 保存token到localStorage
          localStorage.setItem('token', response.data.token)
          // 设置axios默认请求头
          axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`
          ElMessage.success('登录成功')
          emit('login-success', response.data.user)
        } else {
          ElMessage.error(response.data.message || '登录失败')
        }
      } catch (error) {
        console.error('登录失败:', error)
        const errorMessage = error.response?.data?.message || '登录失败，请稍后重试'
        ElMessage.error(errorMessage)
      } finally {
        loginLoading.value = false
      }
    }
  })
}

const register = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      registerLoading.value = true
      try {
        const registerData = {
          username: registerForm.value.username,
          password: registerForm.value.password
        }

        const response = await axios.post('/api/register', registerData)
        if (response.data.success) {
          // 保存token到localStorage
          localStorage.setItem('token', response.data.token)
          // 设置axios默认请求头
          axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`
          ElMessage.success('注册成功，已自动登录')
          emit('login-success', response.data.user)
        } else {
          ElMessage.error(response.data.message || '注册失败')
        }
      } catch (error) {
        console.error('注册失败:', error)
        const errorMessage = error.response?.data?.message || '注册失败，请稍后重试'
        ElMessage.error(errorMessage)
      } finally {
        registerLoading.value = false
      }
    }
  })
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

.password-strength {
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

.password-strength span {
  margin-right: 5px;
}
</style>