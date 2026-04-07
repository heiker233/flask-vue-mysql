<template>
  <div class="deals-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Money /></el-icon>
        <h2>交易管理</h2>
        <el-tag type="info" class="count-tag">共 {{ total }} 笔交易</el-tag>
      </div>
      <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
        添加交易
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
                placeholder="搜索客户姓名、产品"
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
                <el-option label="谈判中" value="negotiating" />
                <el-option label="已完成" value="closed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
              <el-button @click="resetFilters" :icon="RefreshRight">重置</el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-label">总交易金额</div>
            <div class="stat-value amount">¥{{ formatAmount(totalAmount) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-label">已完成金额</div>
            <div class="stat-value success">¥{{ formatAmount(closedAmount) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-label">谈判中金额</div>
            <div class="stat-value warning">¥{{ formatAmount(negotiatingAmount) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 交易表格 -->
    <el-card shadow="hover" class="table-card">
      <el-table
        :data="paginatedDeals"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="customer_name" label="客户" min-width="120">
          <template #default="scope">
            <div class="customer-info">
              <el-avatar :size="28" :style="{ backgroundColor: getAvatarColor(scope.row.customer_name) }">
                {{ scope.row.customer_name?.charAt(0) || '?' }}
              </el-avatar>
              <span>{{ scope.row.customer_name || '未知客户' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="product" label="产品" min-width="120" show-overflow-tooltip />
        <el-table-column prop="amount" label="交易金额" width="140" sortable align="right">
          <template #default="scope">
            <span class="amount-text">¥{{ formatNumber(scope.row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="deal_status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getDealStatusType(scope.row.deal_status)" effect="light">
              {{ getDealStatusText(scope.row.deal_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="expected_close_date" label="预期完成时间" width="130" align="center">
          <template #default="scope">
            {{ scope.row.expected_close_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link :icon="Edit" @click="editDeal(scope.row)">
              编辑
            </el-button>
            <el-button type="danger" link :icon="Delete" @click="deleteDeal(scope.row.id)">
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

    <!-- 添加交易对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加交易"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="addFormRef"
        :model="newDeal"
        :rules="dealRules"
        label-width="100px"
        status-icon
      >
        <el-form-item label="客户" prop="customer_id">
          <el-select
            v-model="newDeal.customer_id"
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
            >
              <div class="customer-option">
                <el-avatar :size="24" :style="{ backgroundColor: getAvatarColor(customer.name) }">
                  {{ customer.name.charAt(0) }}
                </el-avatar>
                <span>{{ customer.name }}</span>
                <span v-if="customer.company" class="company">({{ customer.company }})</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="交易金额" prop="amount">
              <el-input-number
                v-model="newDeal.amount"
                :min="0"
                :precision="2"
                :step="1000"
                style="width: 100%"
                placeholder="请输入金额"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="deal_status">
              <el-select v-model="newDeal.deal_status" placeholder="请选择状态" style="width: 100%">
                <el-option label="谈判中" value="negotiating" />
                <el-option label="已完成" value="closed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="产品" prop="product">
          <el-input v-model="newDeal.product" placeholder="请输入产品名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="预期完成" prop="expected_close_date">
          <el-date-picker
            v-model="newDeal.expected_close_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDeal" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑交易对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑交易"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editDealForm"
        :rules="dealRules"
        label-width="100px"
        status-icon
      >
        <el-form-item label="客户" prop="customer_id">
          <el-select
            v-model="editDealForm.customer_id"
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
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="交易金额" prop="amount">
              <el-input-number
                v-model="editDealForm.amount"
                :min="0"
                :precision="2"
                :step="1000"
                style="width: 100%"
                placeholder="请输入金额"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="deal_status">
              <el-select v-model="editDealForm.deal_status" placeholder="请选择状态" style="width: 100%">
                <el-option label="谈判中" value="negotiating" />
                <el-option label="已完成" value="closed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="产品" prop="product">
          <el-input v-model="editDealForm.product" placeholder="请输入产品名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="预期完成" prop="expected_close_date">
          <el-date-picker
            v-model="editDealForm.expected_close_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateDeal" :loading="updating">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Money, Plus, Search, RefreshRight, Edit, Delete, Calendar, Setting, Grid } from '@element-plus/icons-vue'

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

const deals = ref([])
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
const filterStatus = ref('')

// 时间筛选
const timeRange = ref('month')
const dateRange = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 表单数据
const newDeal = ref({
  customer_id: '',
  amount: 0,
  deal_status: 'negotiating',
  product: '',
  expected_close_date: ''
})

const editDealForm = ref({
  id: null,
  customer_id: '',
  amount: 0,
  deal_status: 'negotiating',
  product: '',
  expected_close_date: ''
})

// 表单验证规则
const dealRules = {
  customer_id: [
    { required: true, message: '请选择客户', trigger: 'change' }
  ],
  amount: [
    { required: true, message: '请输入交易金额', trigger: 'blur' },
    { type: 'number', min: 0, message: '金额必须大于0', trigger: 'blur' }
  ],
  deal_status: [
    { required: true, message: '请选择交易状态', trigger: 'change' }
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

// 交易状态映射
const getDealStatusText = (status) => {
  const statusMap = {
    'negotiating': '谈判中',
    'closed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const getDealStatusType = (status) => {
  const typeMap = {
    'negotiating': 'warning',
    'closed': 'success',
    'cancelled': 'info'
  }
  return typeMap[status] || 'info'
}

// 格式化金额
const formatAmount = (amount) => {
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

const formatNumber = (num) => {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
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

// 统计数据
const totalAmount = computed(() => {
  return filteredDeals.value.reduce((sum, deal) => sum + (parseFloat(deal.amount) || 0), 0)
})

const closedAmount = computed(() => {
  return filteredDeals.value
    .filter(deal => deal.deal_status === 'closed')
    .reduce((sum, deal) => sum + (parseFloat(deal.amount) || 0), 0)
})

const negotiatingAmount = computed(() => {
  return filteredDeals.value
    .filter(deal => deal.deal_status === 'negotiating')
    .reduce((sum, deal) => sum + (parseFloat(deal.amount) || 0), 0)
})

// 筛选后的交易列表
const filteredDeals = computed(() => {
  let result = deals.value

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(deal =>
      deal.customer_name?.toLowerCase().includes(query) ||
      deal.product?.toLowerCase().includes(query)
    )
  }

  // 状态筛选
  if (filterStatus.value) {
    result = result.filter(deal => deal.deal_status === filterStatus.value)
  }

  // 日期筛选 - 按创建时间筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    endDate.setHours(23, 59, 59, 999)
    result = result.filter(deal => {
      const dealDate = new Date(deal.created_at)
      return dealDate >= startDate && dealDate <= endDate
    })
  }

  return result
})

// 分页后的数据
const paginatedDeals = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDeals.value.slice(start, end)
})

const filteredTotal = computed(() => filteredDeals.value.length)
const total = computed(() => deals.value.length)

// 获取交易列表
const fetchDeals = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/deals')
    deals.value = response.data
  } catch (error) {
    console.error('获取交易记录失败:', error)
    ElMessage.error('获取交易记录列表失败')
  } finally {
    loading.value = false
  }
}

// 获取客户列表
const fetchCustomers = async () => {
  try {
    const response = await axios.get('/api/customers')
    customers.value = response.data
    customerOptions.value = response.data
  } catch (error) {
    console.error('获取客户列表失败:', error)
  }
}

// 搜索客户
const searchCustomers = (query) => {
  if (query) {
    customerLoading.value = true
    setTimeout(() => {
      customerOptions.value = customers.value.filter(customer =>
        customer.name.toLowerCase().includes(query.toLowerCase())
      )
      customerLoading.value = false
    }, 200)
  } else {
    customerOptions.value = customers.value
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

// 保存交易
const saveDeal = async () => {
  if (!addFormRef.value) return

  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await axios.post('/api/deals', newDeal.value)
        ElMessage.success('交易记录添加成功')
        fetchDeals()
        showAddDialog.value = false
        resetForm()
      } catch (error) {
        console.error('保存交易记录失败:', error)
        ElMessage.error(error.response?.data?.message || '保存交易记录失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 更新交易
const updateDeal = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await axios.put(`/api/deals/${editDealForm.value.id}`, editDealForm.value)
        ElMessage.success('交易记录更新成功')
        fetchDeals()
        showEditDialog.value = false
        resetEditForm()
      } catch (error) {
        console.error('更新交易记录失败:', error)
        ElMessage.error(error.response?.data?.message || '更新交易记录失败')
      } finally {
        updating.value = false
      }
    }
  })
}

// 删除交易
const deleteDeal = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条交易记录吗？此操作不可恢复！', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/deals/${id}`)
    ElMessage.success('交易记录删除成功')
    fetchDeals()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除交易记录失败:', error)
      ElMessage.error(error.response?.data?.message || '删除交易记录失败')
    }
  }
}

// 编辑交易
const editDeal = async (deal) => {
  editDealForm.value = {
    id: deal.id,
    customer_id: deal.customer_id,
    amount: deal.amount,
    deal_status: deal.deal_status,
    product: deal.product,
    expected_close_date: deal.expected_close_date
  }
  // 加载所有客户到选项中
  customerLoading.value = true
  try {
    const response = await axios.get('/api/customers')
    customerOptions.value = response.data
  } catch (error) {
    console.error('加载客户列表失败:', error)
    // 如果加载失败，至少加载当前客户
    if (!customerOptions.value.find(c => c.id === deal.customer_id)) {
      customerOptions.value = [...customerOptions.value, {
        id: deal.customer_id,
        name: deal.customer_name
      }]
    }
  } finally {
    customerLoading.value = false
  }
  showEditDialog.value = true
}

// 重置表单
const resetForm = () => {
  newDeal.value = {
    customer_id: '',
    amount: 0,
    deal_status: 'negotiating',
    product: '',
    expected_close_date: ''
  }
  addFormRef.value?.resetFields()
}

const resetEditForm = () => {
  editDealForm.value = {
    id: null,
    customer_id: '',
    amount: 0,
    deal_status: 'negotiating',
    product: '',
    expected_close_date: ''
  }
  editFormRef.value?.resetFields()
}

onMounted(() => {
  fetchDeals()
  fetchCustomers()
  // 默认选择本月
  setTimeRange('month')
})
</script>

<style scoped>
.deals-container {
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
  color: #67c23a;
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

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-item {
  padding: 10px 0;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
}

.stat-value.amount {
  color: #409eff;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.warning {
  color: #e6a23c;
}

.table-card {
  margin-bottom: 20px;
}

.customer-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.amount-text {
  font-weight: 600;
  color: #f56c6c;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.customer-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.customer-option .company {
  color: #909399;
  font-size: 12px;
}
</style>
