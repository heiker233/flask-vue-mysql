<template>
  <div>
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
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['refresh'])

const saving = ref(false)
const updating = ref(false)
const resetting = ref(false)

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showResetDialog = ref(false)

const addFormRef = ref(null)
const editFormRef = ref(null)

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

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== newUser.value.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

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

const saveUser = async () => {
  if (!addFormRef.value) return

  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const { confirmPassword, ...userData } = newUser.value
        await axios.post('/api/users', userData)
        ElMessage.success('用户添加成功')
        emit('refresh')
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
        emit('refresh')
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

const openAdd = () => {
  resetAddForm()
  showAddDialog.value = true
}

const openEdit = (user) => {
  editUserForm.value = {
    id: user.id,
    username: user.username,
    role: user.role
  }
  showEditDialog.value = true
}

const openReset = (user) => {
  resetForm.value = {
    id: user.id,
    username: user.username
  }
  showResetDialog.value = true
}

defineExpose({
  openAdd,
  openEdit,
  openReset
})
</script>

<style scoped>
.reset-password-content {
  padding: 10px 0;
}
.reset-user-info {
  margin-top: 20px;
}
</style>
