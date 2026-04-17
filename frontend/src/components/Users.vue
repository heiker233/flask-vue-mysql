<template>
  <div class="users-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Setting /></el-icon>
        <h2>权限管理</h2>
        <el-tag type="info" class="count-tag">共 {{ users.length }} 位用户</el-tag>
      </div>
      <el-button type="primary" @click="openAddDialog" :icon="Plus">
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
            <el-button type="primary" link :icon="Edit" @click="openEditDialog(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link :icon="Key" @click="openResetDialog(scope.row)">
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

    <UserDialogs ref="dialogsRef" @refresh="fetchUsers" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Plus, Edit, Delete, Key } from '@element-plus/icons-vue'
import { getAvatarColor, formatDate } from '../utils/helpers'
import UserDialogs from './users/UserDialogs.vue'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ id: null })
  }
})

const users = ref([])
const loading = ref(false)
const dialogsRef = ref(null)

const currentUserId = computed(() => props.currentUser?.id)

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

const openAddDialog = () => {
  dialogsRef.value?.openAdd()
}

const openEditDialog = (user) => {
  dialogsRef.value?.openEdit(user)
}

const openResetDialog = (user) => {
  dialogsRef.value?.openReset(user)
}

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
</style>
