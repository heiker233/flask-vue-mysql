<template>
  <div class="users-container">
    <div class="page-header">
      <h2>权限管理</h2>
      <el-button type="primary" @click="showAddDialog = true">添加用户</el-button>
    </div>
    <el-table :data="users" border stripe style="width: 100%" max-height="600">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role" label="角色" />
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button type="link" @click="editUser(scope.row)">编辑</el-button>
          <el-button type="link" danger @click="deleteUser(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="showAddDialog"
      title="添加用户"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="newUser" label-width="120px">
        <el-form-item label="用户名" prop="username" required>
          <el-input v-model="newUser.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" required>
          <el-input type="password" v-model="newUser.password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="newUser.role" placeholder="请选择用户角色">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const users = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const newUser = ref({
  username: '',
  password: '',
  role: 'user'
})
const editUserForm = ref({
  id: null,
  username: '',
  password: '',
  role: 'user'
})

const fetchUsers = async () => {
  try {
    const response = await axios.get('/api/users')
    users.value = response.data
  } catch (error) {
    console.error('获取用户失败:', error)
    const errorMessage = error.response?.data?.message || '获取用户列表失败'
    ElMessage.error(errorMessage)
  }
}

const saveUser = async () => {
  try {
    await axios.post('/api/users', newUser.value)
    ElMessage.success('用户添加成功')
    fetchUsers()
    showAddDialog.value = false
    resetForm()
  } catch (error) {
    console.error('保存用户失败:', error)
    const errorMessage = error.response?.data?.message || '保存用户失败'
    ElMessage.error(errorMessage)
  }
}

const deleteUser = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个用户吗？', '确认删除', {
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
      const errorMessage = error.response?.data?.message || '删除用户失败'
      ElMessage.error(errorMessage)
    }
  }
}

const editUser = (user) => {
  editUserForm.value = {
    id: user.id,
    username: user.username,
    password: '',
    role: user.role
  }
  showEditDialog.value = true
}

const updateUser = async () => {
  try {
    await axios.put(`/api/users/${editUserForm.value.id}`, editUserForm.value)
    ElMessage.success('用户更新成功')
    fetchUsers()
    showEditDialog.value = false
    resetEditForm()
  } catch (error) {
    console.error('更新用户失败:', error)
    const errorMessage = error.response?.data?.message || '更新用户失败'
    ElMessage.error(errorMessage)
  }
}

const resetForm = () => {
  newUser.value = {
    username: '',
    password: '',
    role: 'user'
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-container {
  height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>