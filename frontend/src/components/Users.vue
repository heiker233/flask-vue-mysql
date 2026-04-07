<template>
  <div class="users-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Setting /></el-icon>
        <h2>权限管理</h2>
        <el-tag type="info" class="count-tag">共 {{ users.length }} 位用户</el-tag>
      </div>
      <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
        添加用户
      </el-button>
    </div>

    <!-- 用户表格 -->
    <el-card shadow="hover" class="table-card">
      <el-table
        :data="users"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="username" label="用户名" min-width="150">
          <template #default="scope">
            <div class="user-info">
              <el-avatar :size="32" :style="{ backgroundColor: getAvatarColor(scope.row.username) }">
                {{ scope.row.username.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ scope.row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'info'" effect="light">
              {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button type="primary" link :icon="Edit" @click="editUser(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link :icon="Key" @click="resetPassword(scope.row)">
              重置密码
            </el-button>
            <el-button 
              type="danger" 
              link 
              :icon="Delete" 
              @click="deleteUser(scope.row.id)"
              :disabled="scope.row.id === currentUserId"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加用户对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加用户"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="addFormRef"
        :model="newUser"
        :rules="userRules"
        label-width="100px"
        status-icon
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="newUser.username" 
            placeholder="请输入用户名"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            type="password" 
            v-model="newUser.password" 
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            type="password" 
            v-model="newUser.confirmPassword" 
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="newUser.role">
            <el-radio-button label="user">普通用户</el-radio-button>
            <el-radio-button label="admin">管理员</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑用户"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editUserForm"
        :rules="editUserRules"
        label-width="100px"
        status-icon
      >
        <el-form-item label="用户名">
          <el-input v-model="editUserForm.username" disabled />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="editUserForm.role">
            <el-radio-button label="user">普通用户</el-radio-button>
            <el-radio-button label="admin">管理员</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateUser" :loading="updating">确定</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="showResetDialog"
      title="重置密码"
      width="400px"
      destroy-on-close
    >
      <div class="reset-password-content">
        <el-alert
          title="确定要重置该用户的密码吗？"
          description="重置后密码将变为：123456"
          type="warning"
          :closable="false"
          show-icon
        />
        <div class="reset-user-info">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ resetForm.username }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="showResetDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmResetPassword" :loading="resetting">确定重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Plus, Edit, Delete, Key } from '@element-plus/icons-vue'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ id: null })
  }
})

const users = ref([])
const loading = ref(false)
const saving = ref(false)
const updating = ref(false)
const resetting = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showResetDialog = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)

const currentUserId = computed(() => props.currentUser?.id)

// 表单数据
const newUser = ref({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'user'
})

const editUserForm = ref({
  id: null,
  username: '',
  role: 'user'
})

const resetForm = ref({
  id: null,
  username: ''
})

// 验证密码是否一致
const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== newUser.value.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '用户名只能包含字母、数字、下划线和中文', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ]
}

const editUserRules = {
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ]
}

// 头像颜色
const avatarColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8E44AD', '#16A085']
const getAvatarColor = (name) => {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return avatarColors[Math.abs(hash) % avatarColors.length]
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/users')
    users.value = response.data
  } catch (error) {
    console.error('获取用户失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 保存用户
const saveUser = async () => {
  if (!addFormRef.value) return

  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const { confirmPassword, ...userData } = newUser.value
        await axios.post('/api/users', userData)
        ElMessage.success('用户添加成功')
        fetchUsers()
        showAddDialog.value = false
        resetAddForm()
      } catch (error) {
        console.error('保存用户失败:', error)
        ElMessage.error(error.response?.data?.message || '保存用户失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 编辑用户
const editUser = (user) => {
  editUserForm.value = {
    id: user.id,
    username: user.username,
    role: user.role
  }
  showEditDialog.value = true
}

// 更新用户
const updateUser = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await axios.put(`/api/users/${editUserForm.value.id}`, {
          role: editUserForm.value.role
        })
        ElMessage.success('用户更新成功')
        fetchUsers()
        showEditDialog.value = false
        resetEditForm()
      } catch (error) {
        console.error('更新用户失败:', error)
        ElMessage.error(error.response?.data?.message || '更新用户失败')
      } finally {
        updating.value = false
      }
    }
  })
}

// 删除用户
const deleteUser = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个用户吗？此操作不可恢复！', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/users/${id}`)
    ElMessage.success('用户删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error(error.response?.data?.message || '删除用户失败')
    }
  }
}

// 重置密码
const resetPassword = (user) => {
  resetForm.value = {
    id: user.id,
    username: user.username
  }
  showResetDialog.value = true
}

// 确认重置密码
const confirmResetPassword = async () => {
  resetting.value = true
  try {
    await axios.put(`/api/users/${resetForm.value.id}`, {
      password: '123456'
    })
    ElMessage.success('密码重置成功，新密码为：123456')
    showResetDialog.value = false
  } catch (error) {
    console.error('重置密码失败:', error)
    ElMessage.error(error.response?.data?.message || '重置密码失败')
  } finally {
    resetting.value = false
  }
}

// 重置表单
const resetAddForm = () => {
  newUser.value = {
    username: '',
    password: '',
    confirmPassword: '',
    role: 'user'
  }
  addFormRef.value?.resetFields()
}

const resetEditForm = () => {
  editUserForm.value = {
    id: null,
    username: '',
    role: 'user'
  }
  editFormRef.value?.resetFields()
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 28px;
  color: #909399;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.count-tag {
  font-size: 14px;
}

.table-card {
  margin-bottom: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-weight: 500;
}

.reset-password-content {
  padding: 10px 0;
}

.reset-user-info {
  margin-top: 20px;
}
</style>
