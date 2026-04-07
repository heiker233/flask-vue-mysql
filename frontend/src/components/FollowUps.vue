<template>
  <div class="follow-ups-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Message /></el-icon>
        <h2>跟进记录</h2>
        <el-tag type="info" class="count-tag">共 {{ followUps.length }} 条记录</el-tag>
      </div>
      <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
        添加记录
      </el-button>
    </div>

    <!-- 搜索和筛选区域 -->
    <el-card class="search-card" shadow="never">
      <el-row :gutter="20" align="middle">
        <el-col :xs="24" :sm="24" :md="24" :lg="24">
          <div class="filter-container">
            <!-- 时间查询按钮组 -->
            <div class="time-filter-section">
              <el-button-group class="time-filter-buttons">
                <el-button 
                  :type="timeRange === 'all' ? 'primary' : 'default'" 
                  @click="setTimeRange('all')"
                >
                  <el-icon><Grid /></el-icon>
                  全部
                </el-button>
                <el-button 
                  :type="timeRange === 'month' ? 'primary' : 'default'" 
                  @click="setTimeRange('month')"
                >
                  <el-icon><Calendar /></el-icon>
                  本月
                </el-button>
                <el-button 
                  :type="timeRange === 'year' ? 'primary' : 'default'" 
                  @click="setTimeRange('year')"
                >
                  <el-icon><Calendar /></el-icon>
                  本年
                </el-button>
                <el-button 
                  :type="timeRange === 'custom' ? 'primary' : 'default'" 
                  @click="setTimeRange('custom')"
                >
                  <el-icon><Setting /></el-icon>
                  自定义
                </el-button>
              </el-button-group>
              
              <!-- 自定义日期选择器 -->
              <el-date-picker
                v-if="timeRange === 'custom'"
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                @change="handleDateRangeChange"
                class="date-range-picker"
                :unlink-panels="true"
              />
            </div>
            
            <!-- 其他筛选条件 -->
            <div class="other-filters">
              <el-input
                v-model="searchQuery"
                placeholder="搜索客户姓名、跟进内容"
                clearable
                :prefix-icon="Search"
                @input="handleSearch"
                class="search-input"
              />
              <el-select
                v-model="filterType"
                placeholder="筛选跟进方式"
                clearable
                @change="handleSearch"
                class="filter-select"
              >
                <el-option label="电话" value="电话" />
                <el-option label="邮件" value="邮件" />
                <el-option label="面谈" value="面谈" />
                <el-option label="微信" value="微信" />
                <el-option label="其他" value="其他" />
              </el-select>
              <el-button @click="resetFilters" :icon="RefreshRight">重置</el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 跟进记录表格 -->
    <el-card shadow="hover" class="table-card">
      <el-table
        :data="filteredFollowUps"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="customer_name" label="客户姓名" min-width="120">
          <template #default="scope">
            <div class="customer-name">
              <el-avatar :size="28" :style="{ backgroundColor: getAvatarColor(scope.row.customer_name) }">
                {{ scope.row.customer_name ? scope.row.customer_name.charAt(0) : '?' }}
              </el-avatar>
              <span>{{ scope.row.customer_name || '未知客户' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="跟进内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="follow_type" label="跟进方式" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getFollowTypeType(scope.row.follow_type)" effect="light" size="small">
              {{ scope.row.follow_type || '其他' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="next_follow_date" label="下次跟进时间" width="140">
          <template #default="scope">
            <span v-if="scope.row.next_follow_date" class="next-date">
              <el-icon><Calendar /></el-icon>
              {{ formatDate(scope.row.next_follow_date) }}
            </span>
            <span v-else class="no-date">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="记录时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" link :icon="Edit" @click="editFollowUp(scope.row)">
              编辑
            </el-button>
            <el-button type="danger" link :icon="Delete" @click="deleteFollowUp(scope.row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredTotal"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加跟进记录对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加跟进记录"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="addFormRef"
        :model="newFollowUp"
        :rules="followUpRules"
        label-width="120px"
        status-icon
      >
        <el-form-item label="客户" prop="customer_id">
          <el-select
            v-model="newFollowUp.customer_id"
            placeholder="请选择客户"
            style="width: 100%"
            filterable
            remote
            :remote-method="searchCustomers"
            :loading="customerLoading"
          >
            <el-option
              v-for="customer in customerOptions"
              :key="customer.id"
              :label="customer.name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="跟进内容" prop="content">
          <el-input
            type="textarea"
            v-model="newFollowUp.content"
            rows="4"
            placeholder="请输入跟进内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="跟进方式" prop="follow_type">
          <el-select v-model="newFollowUp.follow_type" placeholder="请选择跟进方式" style="width: 100%">
            <el-option label="电话" value="电话" />
            <el-option label="邮件" value="邮件" />
            <el-option label="面谈" value="面谈" />
            <el-option label="微信" value="微信" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="下次跟进时间" prop="next_follow_date">
          <el-date-picker
            v-model="newFollowUp.next_follow_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveFollowUp" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑跟进记录对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑跟进记录"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editFollowUpForm"
        :rules="followUpRules"
        label-width="120px"
        status-icon
      >
        <el-form-item label="客户" prop="customer_id">
          <el-select
            v-model="editFollowUpForm.customer_id"
            placeholder="请选择客户"
            style="width: 100%"
            filterable
            :loading="customerLoading"
          >
            <el-option
              v-for="customer in customerOptions"
              :key="customer.id"
              :label="customer.name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="跟进内容" prop="content">
          <el-input
            type="textarea"
            v-model="editFollowUpForm.content"
            rows="4"
            placeholder="请输入跟进内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="跟进方式" prop="follow_type">
          <el-select v-model="editFollowUpForm.follow_type" placeholder="请选择跟进方式" style="width: 100%">
            <el-option label="电话" value="电话" />
            <el-option label="邮件" value="邮件" />
            <el-option label="面谈" value="面谈" />
            <el-option label="微信" value="微信" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="下次跟进时间" prop="next_follow_date">
          <el-date-picker
            v-model="editFollowUpForm.next_follow_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateFollowUp" :loading="updating">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Message, Plus, Search, RefreshRight, Edit, Delete, Calendar, Setting, Grid } from '@element-plus/icons-vue'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ role: 'user' })
  }
})

// 判断是否为管理员
const isAdmin = computed(() => {
  return props.currentUser?.role === 'admin'
})

const followUps = ref([])
const customers = ref([])
const customerOptions = ref([])
const loading = ref(false)
const saving = ref(false)
const updating = ref(false)
const customerLoading = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)

// 搜索和筛选
const searchQuery = ref('')
const filterType = ref('')

// 时间筛选
const timeRange = ref('month')
const dateRange = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 表单数据
const newFollowUp = ref({
  customer_id: '',
  content: '',
  follow_type: '',
  next_follow_date: ''
})

const editFollowUpForm = ref({
  id: null,
  customer_id: '',
  content: '',
  follow_type: '',
  next_follow_date: ''
})

// 表单验证规则
const followUpRules = {
  customer_id: [
    { required: true, message: '请选择客户', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入跟进内容', trigger: 'blur' },
    { min: 5, max: 500, message: '内容长度在 5 到 500 个字符', trigger: 'blur' }
  ],
  follow_type: [
    { required: true, message: '请选择跟进方式', trigger: 'change' }
  ]
}

// 头像颜色
const avatarColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8E44AD', '#16A085']
const getAvatarColor = (name) => {
  if (!name) return '#909399'
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return avatarColors[Math.abs(hash) % avatarColors.length]
}

// 跟进方式标签类型
const getFollowTypeType = (type) => {
  const typeMap = {
    '电话': 'primary',
    '邮件': 'success',
    '面谈': 'warning',
    '微信': 'info'
  }
  return typeMap[type] || 'info'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
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

// 搜索客户
const searchCustomers = async (query) => {
  if (query) {
    customerLoading.value = true
    try {
      const response = await axios.get(`/api/customers?search=${query}`)
      customerOptions.value = response.data
    } catch (error) {
      console.error('搜索客户失败:', error)
    } finally {
      customerLoading.value = false
    }
  }
}

// 获取跟进记录列表
const fetchFollowUps = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/follow-ups')
    followUps.value = response.data
  } catch (error) {
    console.error('获取跟进记录失败:', error)
    ElMessage.error('获取跟进记录列表失败')
  } finally {
    loading.value = false
  }
}

// 筛选后的跟进记录
const filteredFollowUps = computed(() => {
  let result = followUps.value

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(followUp =>
      (followUp.customer_name && followUp.customer_name.toLowerCase().includes(query)) ||
      (followUp.content && followUp.content.toLowerCase().includes(query))
    )
  }

  // 跟进方式筛选
  if (filterType.value) {
    result = result.filter(followUp => followUp.follow_type === filterType.value)
  }

  // 日期范围筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    result = result.filter(followUp => {
      const followDate = new Date(followUp.created_at)
      return followDate >= startDate && followDate <= endDate
    })
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 筛选后的总数
const filteredTotal = computed(() => {
  let result = followUps.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(followUp =>
      (followUp.customer_name && followUp.customer_name.toLowerCase().includes(query)) ||
      (followUp.content && followUp.content.toLowerCase().includes(query))
    )
  }

  if (filterType.value) {
    result = result.filter(followUp => followUp.follow_type === filterType.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    result = result.filter(followUp => {
      const followDate = new Date(followUp.created_at)
      return followDate >= startDate && followDate <= endDate
    })
  }

  return result.length
})

// 设置时间范围
const setTimeRange = (range) => {
  timeRange.value = range
  if (range === 'all') {
    dateRange.value = []
    handleSearch()
  } else if (range !== 'custom') {
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth()
    
    if (range === 'month') {
      const start = new Date(year, month, 1)
      dateRange.value = [
        start.toISOString().split('T')[0],
        now.toISOString().split('T')[0]
      ]
    } else if (range === 'year') {
      const start = new Date(year, 0, 1)
      dateRange.value = [
        start.toISOString().split('T')[0],
        now.toISOString().split('T')[0]
      ]
    }
    handleSearch()
  }
}

// 处理日期范围变化
const handleDateRangeChange = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    handleSearch()
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 重置筛选
const resetFilters = () => {
  searchQuery.value = ''
  filterType.value = ''
  timeRange.value = 'month'
  setTimeRange('month')
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 保存跟进记录
const saveFollowUp = async () => {
  if (!addFormRef.value) return

  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await axios.post('/api/follow-ups', newFollowUp.value)
        ElMessage.success('跟进记录添加成功')
        fetchFollowUps()
        showAddDialog.value = false
        resetAddForm()
      } catch (error) {
        console.error('保存跟进记录失败:', error)
        ElMessage.error(error.response?.data?.message || '保存跟进记录失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 编辑跟进记录
const editFollowUp = async (followUp) => {
  editFollowUpForm.value = {
    id: followUp.id,
    customer_id: followUp.customer_id,
    content: followUp.content,
    follow_type: followUp.follow_type,
    next_follow_date: followUp.next_follow_date
  }
  // 加载所有客户到选项中
  customerLoading.value = true
  try {
    const response = await axios.get('/api/customers')
    customerOptions.value = response.data
  } catch (error) {
    console.error('加载客户列表失败:', error)
    // 如果加载失败，至少加载当前客户
    if (followUp.customer_id && followUp.customer_name) {
      customerOptions.value = [{ id: followUp.customer_id, name: followUp.customer_name }]
    }
  } finally {
    customerLoading.value = false
  }
  showEditDialog.value = true
}

// 更新跟进记录
const updateFollowUp = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await axios.put(`/api/follow-ups/${editFollowUpForm.value.id}`, editFollowUpForm.value)
        ElMessage.success('跟进记录更新成功')
        fetchFollowUps()
        showEditDialog.value = false
        resetEditForm()
      } catch (error) {
        console.error('更新跟进记录失败:', error)
        ElMessage.error(error.response?.data?.message || '更新跟进记录失败')
      } finally {
        updating.value = false
      }
    }
  })
}

// 删除跟进记录
const deleteFollowUp = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条跟进记录吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/follow-ups/${id}`)
    ElMessage.success('跟进记录删除成功')
    fetchFollowUps()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除跟进记录失败:', error)
      ElMessage.error(error.response?.data?.message || '删除跟进记录失败')
    }
  }
}

// 重置表单
const resetAddForm = () => {
  newFollowUp.value = {
    customer_id: '',
    content: '',
    follow_type: '',
    next_follow_date: ''
  }
  customerOptions.value = []
  addFormRef.value?.resetFields()
}

const resetEditForm = () => {
  editFollowUpForm.value = {
    id: null,
    customer_id: '',
    content: '',
    follow_type: '',
    next_follow_date: ''
  }
  customerOptions.value = []
  editFormRef.value?.resetFields()
}

onMounted(() => {
  fetchFollowUps()
  // 默认选择本月
  setTimeRange('month')
})
</script>

<style scoped>
.follow-ups-container {
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

.search-card {
  margin-bottom: 20px;
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.time-filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.time-filter-buttons {
  display: flex;
}

.time-filter-buttons .el-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

.date-range-picker {
  width: 240px;
}

.other-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-input {
  width: 240px;
}

.filter-select {
  width: 140px;
}

.table-card {
  margin-bottom: 20px;
}

.customer-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.next-date {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #67C23A;
}

.no-date {
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
