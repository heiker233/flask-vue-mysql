<template>
  <div class="customers-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><User /></el-icon>
        <h2>客户管理</h2>
        <el-tag type="info" class="count-tag">共 {{ total }} 位客户</el-tag>
      </div>
      <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
        添加客户
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
                placeholder="搜索客户姓名、电话、公司"
                clearable
                :prefix-icon="Search"
                @input="handleSearch"
                class="search-input"
              />
              <el-select
                v-model="filterStatus"
                placeholder="筛选状态"
                clearable
                @change="handleSearch"
                class="filter-select"
              >
                <el-option label="潜在客户" value="potential" />
                <el-option label="活跃客户" value="active" />
                <el-option label="已流失客户" value="lost" />
              </el-select>
              <el-select
                v-model="filterIndustry"
                placeholder="筛选行业"
                clearable
                @change="handleSearch"
                class="filter-select"
              >
                <el-option
                  v-for="industry in industryOptions"
                  :key="industry"
                  :label="industry"
                  :value="industry"
                />
              </el-select>
              <el-button @click="resetFilters" :icon="RefreshRight">重置</el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 客户表格 -->
    <el-card shadow="hover" class="table-card">
      <el-table
        :data="filteredCustomers"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="姓名" min-width="100" sortable>
          <template #default="scope">
            <div class="customer-name">
              <el-avatar :size="32" :style="{ backgroundColor: getAvatarColor(scope.row.name) }">
                {{ scope.row.name.charAt(0) }}
              </el-avatar>
              <span>{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="company" label="公司" min-width="150" show-overflow-tooltip />
        <el-table-column prop="industry" label="行业" min-width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.industry" size="small" effect="plain">
              {{ scope.row.industry }}
            </el-tag>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center" sortable>
          <template #default="scope">
            <el-tag :type="getCustomerStatusType(scope.row.status)" effect="light">
              {{ getCustomerStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link :icon="View" @click="viewCustomer(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link :icon="Edit" @click="editCustomer(scope.row)">
              编辑
            </el-button>
            <el-button type="danger" link :icon="Delete" @click="deleteCustomer(scope.row.id)">
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

    <!-- 添加客户对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加客户"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="addFormRef"
        :model="newCustomer"
        :rules="customerRules"
        label-width="100px"
        status-icon
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="newCustomer.name" placeholder="请输入客户姓名" maxlength="50" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话" prop="phone">
              <el-input v-model="newCustomer.phone" placeholder="请输入客户电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="newCustomer.email" placeholder="请输入客户邮箱" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="公司" prop="company">
              <el-input v-model="newCustomer.company" placeholder="请输入客户公司" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="行业" prop="industry">
              <el-select v-model="newCustomer.industry" placeholder="请选择行业" style="width: 100%" allow-create filterable>
                <el-option
                  v-for="industry in industryOptions"
                  :key="industry"
                  :label="industry"
                  :value="industry"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="newCustomer.status">
            <el-radio-button label="potential">潜在客户</el-radio-button>
            <el-radio-button label="active">活跃客户</el-radio-button>
            <el-radio-button label="lost">已流失</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="newCustomer.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入客户备注信息"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCustomer" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑客户对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑客户"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editCustomerForm"
        :rules="customerRules"
        label-width="100px"
        status-icon
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="editCustomerForm.name" placeholder="请输入客户姓名" maxlength="50" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话" prop="phone">
              <el-input v-model="editCustomerForm.phone" placeholder="请输入客户电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editCustomerForm.email" placeholder="请输入客户邮箱" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="公司" prop="company">
              <el-input v-model="editCustomerForm.company" placeholder="请输入客户公司" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="行业" prop="industry">
              <el-select v-model="editCustomerForm.industry" placeholder="请选择行业" style="width: 100%" allow-create filterable>
                <el-option
                  v-for="industry in industryOptions"
                  :key="industry"
                  :label="industry"
                  :value="industry"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="editCustomerForm.status">
            <el-radio-button label="potential">潜在客户</el-radio-button>
            <el-radio-button label="active">活跃客户</el-radio-button>
            <el-radio-button label="lost">已流失</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="editCustomerForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入客户备注信息"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateCustomer" :loading="updating">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看客户详情对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="客户详情"
      width="700px"
    >
      <div v-if="currentCustomer" class="customer-detail">
        <div class="detail-header">
          <el-avatar :size="64" :style="{ backgroundColor: getAvatarColor(currentCustomer.name), fontSize: '24px' }">
            {{ currentCustomer.name.charAt(0) }}
          </el-avatar>
          <div class="detail-title">
            <h3>{{ currentCustomer.name }}</h3>
            <el-tag :type="getCustomerStatusType(currentCustomer.status)" effect="light">
              {{ getCustomerStatusText(currentCustomer.status) }}
            </el-tag>
          </div>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="电话">{{ currentCustomer.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentCustomer.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="公司">{{ currentCustomer.company || '-' }}</el-descriptions-item>
          <el-descriptions-item label="行业">{{ currentCustomer.industry || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentCustomer.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(currentCustomer.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentCustomer.notes || '-' }}</el-descriptions-item>
        </el-descriptions>
        <div class="detail-actions">
          <el-button type="primary" @click="showViewDialog = false; editCustomer(currentCustomer)">
            编辑客户
          </el-button>
          <el-button @click="showViewDialog = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Plus, Search, RefreshRight, View, Edit, Delete, Calendar, Setting, Grid } from '@element-plus/icons-vue'

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

const customers = ref([])
const loading = ref(false)
const saving = ref(false)
const updating = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)

// 搜索和筛选
const searchQuery = ref('')
const filterStatus = ref('')
const filterIndustry = ref('')

// 时间筛选
const timeRange = ref('month')
const dateRange = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 行业选项
const industryOptions = [
  'IT/互联网',
  '金融',
  '制造业',
  '教育',
  '医疗',
  '房地产',
  '零售',
  '餐饮',
  '物流',
  '其他'
]

// 表单数据
const newCustomer = ref({
  name: '',
  phone: '',
  email: '',
  company: '',
  industry: '',
  status: 'potential',
  notes: ''
})

const editCustomerForm = ref({
  id: null,
  name: '',
  phone: '',
  email: '',
  company: '',
  industry: '',
  status: 'potential',
  notes: ''
})

const currentCustomer = ref(null)

// 表单验证规则
const customerRules = {
  name: [
    { required: true, message: '请输入客户姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$|^\d{3,4}-\d{7,8}$|^\d{7,8}$/, message: '请输入正确的电话号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择客户状态', trigger: 'change' }
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

// 客户状态映射
const getCustomerStatusText = (status) => {
  const statusMap = {
    'potential': '潜在客户',
    'active': '活跃客户',
    'lost': '已流失客户'
  }
  return statusMap[status] || status
}

const getCustomerStatusType = (status) => {
  const typeMap = {
    'potential': 'warning',
    'active': 'success',
    'lost': 'info'
  }
  return typeMap[status] || 'info'
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

// 筛选后的客户列表
const filteredCustomers = computed(() => {
  let result = customers.value

  // 时间筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    endDate.setHours(23, 59, 59, 999)
    
    result = result.filter(customer => {
      const createdAt = new Date(customer.created_at)
      return createdAt >= startDate && createdAt <= endDate
    })
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(customer =>
      customer.name?.toLowerCase().includes(query) ||
      customer.phone?.includes(query) ||
      customer.company?.toLowerCase().includes(query)
    )
  }

  // 状态筛选
  if (filterStatus.value) {
    result = result.filter(customer => customer.status === filterStatus.value)
  }

  // 行业筛选
  if (filterIndustry.value) {
    result = result.filter(customer => customer.industry === filterIndustry.value)
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

const filteredTotal = computed(() => {
  let result = customers.value

  // 时间筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    endDate.setHours(23, 59, 59, 999)
    
    result = result.filter(customer => {
      const createdAt = new Date(customer.created_at)
      return createdAt >= startDate && createdAt <= endDate
    })
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(customer =>
      customer.name?.toLowerCase().includes(query) ||
      customer.phone?.includes(query) ||
      customer.company?.toLowerCase().includes(query)
    )
  }

  if (filterStatus.value) {
    result = result.filter(customer => customer.status === filterStatus.value)
  }

  if (filterIndustry.value) {
    result = result.filter(customer => customer.industry === filterIndustry.value)
  }

  return result.length
})

const total = computed(() => customers.value.length)

// 获取客户列表
const fetchCustomers = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/customers')
    customers.value = response.data
  } catch (error) {
    console.error('获取客户失败:', error)
    ElMessage.error('获取客户列表失败')
  } finally {
    loading.value = false
  }
}

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
  filterStatus.value = ''
  filterIndustry.value = ''
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

// 保存客户
const saveCustomer = async () => {
  if (!addFormRef.value) return

  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await axios.post('/api/customers', newCustomer.value)
        ElMessage.success('客户添加成功')
        fetchCustomers()
        showAddDialog.value = false
        resetForm()
      } catch (error) {
        console.error('保存客户失败:', error)
        ElMessage.error(error.response?.data?.message || '保存客户失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 更新客户
const updateCustomer = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await axios.put(`/api/customers/${editCustomerForm.value.id}`, editCustomerForm.value)
        ElMessage.success('客户更新成功')
        fetchCustomers()
        showEditDialog.value = false
        resetEditForm()
      } catch (error) {
        console.error('更新客户失败:', error)
        ElMessage.error(error.response?.data?.message || '更新客户失败')
      } finally {
        updating.value = false
      }
    }
  })
}

// 删除客户
const deleteCustomer = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个客户吗？此操作不可恢复！', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/customers/${id}`)
    ElMessage.success('客户删除成功')
    fetchCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除客户失败:', error)
      ElMessage.error(error.response?.data?.message || '删除客户失败')
    }
  }
}

// 查看客户
const viewCustomer = (customer) => {
  currentCustomer.value = customer
  showViewDialog.value = true
}

// 编辑客户
const editCustomer = (customer) => {
  editCustomerForm.value = {
    id: customer.id,
    name: customer.name,
    phone: customer.phone,
    email: customer.email,
    company: customer.company,
    industry: customer.industry,
    status: customer.status,
    notes: customer.notes || ''
  }
  showEditDialog.value = true
}

// 重置表单
const resetForm = () => {
  newCustomer.value = {
    name: '',
    phone: '',
    email: '',
    company: '',
    industry: '',
    status: 'potential',
    notes: ''
  }
  addFormRef.value?.resetFields()
}

const resetEditForm = () => {
  editCustomerForm.value = {
    id: null,
    name: '',
    phone: '',
    email: '',
    company: '',
    industry: '',
    status: 'potential',
    notes: ''
  }
  editFormRef.value?.resetFields()
}

onMounted(() => {
  fetchCustomers()
  // 默认选择本月
  setTimeRange('month')
})
</script>

<style scoped>
.customers-container {
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
  color: #409eff;
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

.text-gray {
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.customer-detail {
  padding: 10px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.detail-title {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-title h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.detail-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
