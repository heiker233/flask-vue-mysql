<template>
  <div class="deals-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Money /></el-icon>
        <h2>交易管理</h2>
        <el-tag type="info" class="count-tag">共 {{ total }} 笔交易</el-tag>
      </div>
      <div class="header-right">
        <el-button type="success" @click="showExportDialog = true" :icon="Download">
          导出数据
        </el-button>
        <el-button type="primary" @click="handleAddDeal" :icon="Plus">
          添加交易
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <DealFilter
      v-model:searchQuery="searchQuery"
      v-model:filterStatus="filterStatus"
      v-model:timeRange="timeRange"
      v-model:dateRange="dateRange"
      @search="handleSearch"
    />

    <!-- 统计卡片 -->
    <DealOverview
      :total-amount="totalAmount"
      :closed-amount="closedAmount"
      :pending-approval-count="pendingApprovalCount"
      :unpaid-amount="unpaidAmount"
    />

    <!-- 交易表格 -->
    <DealTable
      :paginated-deals="paginatedDeals"
      :loading="loading"
      :current-user="currentUser"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :filtered-total="filteredTotal"
      @view="handleViewDeal"
      @edit="handleEditDeal"
      @approve="handleApproveDeal"
      @delete="deleteDeal"
    />

    <!-- 对话框 -->
    <DealDialogs
      ref="dialogsRef"
      :customer-options="customerOptions"
      :product-list="productList"
      :current-user="currentUser"
      @refresh="fetchDeals"
      @submit-approval="handleSubmitApproval"
    />

    <!-- 导出对话框 -->
    <ExportDialog
      v-model="showExportDialog"
      title="导出交易数据"
      data-type="deals"
      :fields="dealExportFields"
      :default-fields="defaultExportFields"
      :filters="currentFilters"
      :total-count="total"
      :filtered-count="filteredTotal"
      @export-success="handleExportSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Money, Plus, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { formatLocalDateInput } from '../utils/helpers'

import { useDeals } from '../composables/useDeals'
import DealOverview from './deals/DealOverview.vue'
import DealFilter from './deals/DealFilter.vue'
import DealTable from './deals/DealTable.vue'
import DealDialogs from './deals/DealDialogs.vue'
import ExportDialog from './ExportDialog.vue'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ role: 'user' })
  }
})

const {
  deals,
  customerOptions,
  productList,
  loading,
  searchQuery,
  filterStatus,
  timeRange,
  dateRange,
  currentPage,
  pageSize,
  paginatedDeals,
  filteredTotal,
  total,
  currentFilters,
  totalAmount,
  closedAmount,
  pendingApprovalCount,
  unpaidAmount,
  fetchDeals,
  fetchCustomers,
  fetchProducts,
  deleteDeal,
  submitApproval
} = useDeals()

const dialogsRef = ref(null)
const showExportDialog = ref(false)

const dealExportFields = [
  { key: 'id', label: '交易ID', description: '系统唯一标识' },
  { key: 'customer_id', label: '客户ID', description: '关联客户ID' },
  { key: 'customer_name', label: '客户姓名', description: '客户名称' },
  { key: 'product_id', label: '产品ID', description: '关联产品ID' },
  { key: 'product_name', label: '产品名称', description: '产品名称' },
  { key: 'quantity', label: '数量', description: '购买数量' },
  { key: 'unit_price', label: '单价', description: '产品单价' },
  { key: 'amount', label: '交易金额', description: '总金额' },
  { key: 'deal_status', label: '交易状态', description: '谈判中/已完成/已取消' },
  { key: 'payment_status', label: '付款状态', description: '未付款/部分付款/已付款' },
  { key: 'paid_amount', label: '已付金额', description: '实际已付金额' },
  { key: 'approval_status', label: '审批状态', description: '待审批/已批准/已拒绝' },
  { key: 'expected_close_date', label: '预期完成日期', description: '预计成交日期' },
  { key: 'actual_close_date', label: '实际完成日期', description: '实际成交日期' },
  { key: 'notes', label: '备注', description: '交易备注' },
  { key: 'created_at', label: '创建时间', description: '交易创建时间' },
  { key: 'updated_at', label: '更新时间', description: '最后更新时间' }
]

const invalidDealExportFields = new Set(['customer_name'])
for (let i = dealExportFields.length - 1; i >= 0; i -= 1) {
  if (invalidDealExportFields.has(dealExportFields[i].key)) {
    dealExportFields.splice(i, 1)
  }
}

const defaultExportFields = ['id', 'customer_id', 'product_name', 'quantity', 'unit_price', 'amount', 'deal_status', 'payment_status', 'created_at']

const handleSearch = () => {
  currentPage.value = 1
  fetchDeals()
}

const handleAddDeal = () => {
  dialogsRef.value?.openAdd()
}

import { watch } from 'vue'

watch([currentPage, pageSize], () => {
  fetchDeals()
})

const handleViewDeal = (deal) => {
  dialogsRef.value?.openView(deal)
}

const handleEditDeal = (deal) => {
  dialogsRef.value?.openEdit(deal)
}

const handleApproveDeal = (deal) => {
  dialogsRef.value?.openApprove(deal)
}

const handleSubmitApproval = async (approvalDeal, approvalForm) => {
  const success = await submitApproval(approvalDeal, approvalForm, props.currentUser)
  if (success) {
    dialogsRef.value?.closeApprovalDialog()
  } else {
    dialogsRef.value?.stopApproveLoading()
  }
}

const handleExportSuccess = () => {
  ElMessage.success('交易数据导出成功')
}

onMounted(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const start = new Date(year, month, 1)

  timeRange.value = 'month'
  dateRange.value = [
    formatLocalDateInput(start),
    formatLocalDateInput(now)
  ]

  fetchDeals()
  fetchCustomers()
  fetchProducts()
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
</style>
