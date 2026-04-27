<template>
  <div class="customers-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><User /></el-icon>
        <h2>客户管理</h2>
        <el-tag type="info" class="count-tag">共 {{ totalServer }} 位客户</el-tag>
      </div>
      <div class="header-right">
        <el-button type="success" @click="showExportDialog = true" :icon="Download">
          导出数据
        </el-button>
        <el-button type="primary" @click="customerDialogsRef?.openAdd()" :icon="Plus">
          添加客户
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <CustomerSearch
      v-model:searchQuery="searchQuery"
      v-model:filterStatus="filterStatus"
      v-model:filterIndustry="filterIndustry"
      v-model:timeRange="timeRange"
      v-model:dateRange="dateRange"
      v-model:showAdvancedSearch="showAdvancedSearch"
      v-model:advancedFilters="advancedFilters"
      v-model:sortBy="sortBy"
      v-model:sortOrder="sortOrder"
      :industryOptions="industryOptions"
      :userList="userList"
      @search="handleSearch"
      @reset="resetFilters"
      @timeRangeChange="setTimeRange"
      @dateRangeChange="handleDateRangeChange"
    />

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
        <el-table-column prop="value_score" label="价值评分" width="150" align="center" sortable>
          <template #default="scope">
            <div class="score-display" @click="customerDialogsRef?.openScoreEdit(scope.row)">
              <el-rate 
                v-model="scope.row.value_score" 
                :max="5"
                disabled
                class="readonly-rate"
              />
              <el-icon class="edit-icon"><Edit /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="assignee" label="负责人" width="100" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.assignee" type="primary" size="small">
              {{ scope.row.assignee.username }}
            </el-tag>
            <span v-else class="text-gray">未分配</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button type="primary" link :icon="View" @click="customerDialogsRef?.openView(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link :icon="Edit" @click="customerDialogsRef?.openEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link :icon="User" @click="customerDialogsRef?.openAssign(scope.row)">
              分配
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

    <!-- 弹窗组件 -->
    <CustomerDialogs
      ref="customerDialogsRef"
      :industryOptions="industryOptions"
      @customer-added="handleCustomerAdded"
      @customer-updated="handleCustomerUpdated"
      @customer-assigned="handleCustomerAssigned"
      @score-updated="handleScoreUpdated"
    />

    <!-- 导出对话框 -->
    <ExportDialog
      v-model="showExportDialog"
      title="导出客户数据"
      data-type="customers"
      :fields="customerExportFields"
      :default-fields="defaultExportFields"
      :filters="currentFilters"
      :total-count="totalServer"
      :filtered-count="filteredTotal"
      @export-success="() => ElMessage.success('客户数据导出成功')"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Plus, View, Edit, Delete, Download } from '@element-plus/icons-vue'
import { getAvatarColor, formatDate, formatLocalDateInput } from '../utils/helpers'

import ExportDialog from './ExportDialog.vue'
import CustomerSearch from './customers/CustomerSearch.vue'
import CustomerDialogs from './customers/CustomerDialogs.vue'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ role: 'user' })
  }
})

const isAdmin = computed(() => props.currentUser?.role === 'admin')

const customers = ref([])
const loading = ref(false)
const customerDialogsRef = ref(null)
const showExportDialog = ref(false)

// 导出相关配置
const customerExportFields = [
  { key: 'id', label: '客户ID', description: '系统唯一标识' },
  { key: 'name', label: '客户姓名', description: '客户姓名' },
  { key: 'phone', label: '联系电话', description: '客户电话' },
  { key: 'email', label: '电子邮箱', description: '客户邮箱' },
  { key: 'company', label: '公司名称', description: '所属公司' },
  { key: 'industry', label: '所属行业', description: '行业分类' },
  { key: 'status', label: '客户状态', description: '潜在/活跃/流失' },
  { key: 'value_score', label: '价值评分', description: '1-5星评分' },
  { key: 'cooperation_stage', label: '合作阶段', description: '当前合作进度' },
  { key: 'assigned_to', label: '负责人ID', description: '负责人用户ID' },
  { key: 'assignee_name', label: '负责人姓名', description: '负责人姓名' },
  { key: 'created_at', label: '创建时间', description: '客户录入时间' },
  { key: 'updated_at', label: '更新时间', description: '最后更新时间' },
  { key: 'notes', label: '备注信息', description: '客户备注' }
]

const invalidCustomerExportFields = new Set(['assignee_name', 'notes'])
for (let i = customerExportFields.length - 1; i >= 0; i -= 1) {
  if (invalidCustomerExportFields.has(customerExportFields[i].key)) {
    customerExportFields.splice(i, 1)
  }
}

const defaultExportFields = ['name', 'phone', 'email', 'company', 'industry', 'status', 'value_score', 'created_at']

// 搜索和筛选状态
const searchQuery = ref('')
const filterStatus = ref('')
const filterIndustry = ref('')
const showAdvancedSearch = ref(false)
const advancedFilters = ref({
  cooperation_stage: '',
  assigned_to: null,
  value_score_min: 0,
  value_score_max: 5,
  phone_prefix: ''
})
const sortBy = ref('created_at')
const sortOrder = ref('desc')
const userList = ref([])
const timeRange = ref('month')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

const industryOptions = [
  'IT/互联网', '金融', '制造业', '教育', '医疗',
  '房地产', '零售', '餐饮', '物流', '其他'
]

const currentFilters = computed(() => ({
  keyword: searchQuery.value,
  status: filterStatus.value,
  industry: filterIndustry.value,
  cooperation_stage: advancedFilters.value.cooperation_stage,
  assigned_to: advancedFilters.value.assigned_to,
  value_score_min: advancedFilters.value.value_score_min,
  value_score_max: advancedFilters.value.value_score_max,
  phone_prefix: advancedFilters.value.phone_prefix,
  start_date: dateRange.value?.[0],
  end_date: dateRange.value?.[1]
}))

const filteredCustomers = computed(() => customers.value)
const filteredTotal = computed(() => totalServer.value)
const totalServer = ref(0)

// Helper methods
const getCustomerStatusText = (status) => {
  const statusMap = { 'potential': '潜在客户', 'active': '活跃客户', 'lost': '已流失客户' }
  return statusMap[status] || status
}

const getCustomerStatusType = (status) => {
  const typeMap = { 'potential': 'warning', 'active': 'success', 'lost': 'info' }
  return typeMap[status] || 'info'
}

// API Methods
const fetchCustomers = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (searchQuery.value) params.append('keyword', searchQuery.value)
    if (filterStatus.value) params.append('status', filterStatus.value)
    if (filterIndustry.value) params.append('industry', filterIndustry.value)
    if (advancedFilters.value.cooperation_stage) params.append('cooperation_stage', advancedFilters.value.cooperation_stage)
    if (advancedFilters.value.assigned_to) params.append('assigned_to', advancedFilters.value.assigned_to)
    if (advancedFilters.value.value_score_min > 0) params.append('value_score_min', advancedFilters.value.value_score_min)
    if (advancedFilters.value.value_score_max < 5) params.append('value_score_max', advancedFilters.value.value_score_max)
    if (advancedFilters.value.phone_prefix) params.append('phone_prefix', advancedFilters.value.phone_prefix)
    if (dateRange.value && dateRange.value.length === 2) {
      params.append('start_date', dateRange.value[0])
      params.append('end_date', dateRange.value[1])
    }
    params.append('sort_by', sortBy.value)
    params.append('sort_order', sortOrder.value)
    params.append('page', currentPage.value)
    params.append('pageSize', pageSize.value)
    
    const response = await axios.get(`/api/customers?${params.toString()}`)
    customers.value = response.data.items || response.data
    totalServer.value = response.data.total || response.data.length
  } catch (error) {
    console.error('获取客户失败:', error)
    ElMessage.error('获取客户列表失败')
  } finally {
    loading.value = false
  }
}

const fetchUserList = async () => {
  try {
    const response = await axios.get('/api/users')
    userList.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const deleteCustomer = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个客户吗？此操作不可恢复！', '确认删除', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
    })
    await axios.delete(`/api/customers/${id}`)
    const index = customers.value.findIndex(c => c.id === id)
    if (index !== -1) customers.value.splice(index, 1)
    ElMessage.success('客户删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除客户失败:', error)
      ElMessage.error(error.response?.data?.message || '删除客户失败')
    }
  }
}

// Events from CustomerSearch
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
      dateRange.value = [formatLocalDateInput(start), formatLocalDateInput(now)]
    } else if (range === 'year') {
      const start = new Date(year, 0, 1)
      dateRange.value = [formatLocalDateInput(start), formatLocalDateInput(now)]
    }
    handleSearch()
  }
}

const handleDateRangeChange = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    handleSearch()
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchCustomers()
}

const resetFilters = () => {
  searchQuery.value = ''
  filterStatus.value = ''
  filterIndustry.value = ''
  timeRange.value = 'month'
  showAdvancedSearch.value = false
  advancedFilters.value = {
    cooperation_stage: '', assigned_to: null, value_score_min: 0, value_score_max: 5, phone_prefix: ''
  }
  sortBy.value = 'created_at'
  sortOrder.value = 'desc'
  setTimeRange('month')
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchCustomers()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchCustomers()
}

// Events from CustomerDialogs
const handleCustomerAdded = (newCustomer) => {
  fetchCustomers()
}

const handleCustomerUpdated = (updatedCustomer) => {
  fetchCustomers()
}

const handleCustomerAssigned = (data) => {
  const index = customers.value.findIndex(c => c.id === data.id)
  if (index !== -1) {
    customers.value[index].assigned_to = data.assigned_to
    if (data.assignee) {
      customers.value[index].assignee = data.assignee
    }
  }
}

const handleScoreUpdated = (data) => {
  const customer = customers.value.find(c => c.id === data.id)
  if (customer) {
    customer.value_score = data.value_score
  }
}

onMounted(() => {
  fetchCustomers()
  fetchUserList()
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

/* 评分显示样式 */
.score-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.score-display:hover {
  background-color: #f5f7fa;
}

.score-display:hover .edit-icon {
  opacity: 1;
}

.readonly-rate {
  pointer-events: none;
}

.readonly-rate :deep(.el-rate__icon) {
  font-size: 18px;
}

.edit-icon {
  font-size: 14px;
  color: #409eff;
  opacity: 0;
  transition: opacity 0.3s;
}
</style>
