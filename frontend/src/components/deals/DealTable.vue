<template>
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
      <el-table-column prop="product_name" label="产品" min-width="120" show-overflow-tooltip />
      <el-table-column prop="quantity" label="数量" width="80" align="center" />
      <el-table-column prop="unit_price" label="单价" width="100" align="right">
        <template #default="scope">
          ¥{{ formatNumber(scope.row.unit_price || 0) }}
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="交易金额" width="120" sortable align="right">
        <template #default="scope">
          <span class="amount-text">¥{{ formatNumber(scope.row.amount) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="deal_status" label="交易状态" width="90" align="center">
        <template #default="scope">
          <el-tag :type="getDealStatusType(scope.row.deal_status)" effect="light" size="small">
            {{ getDealStatusText(scope.row.deal_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="payment_status" label="付款状态" width="90" align="center">
        <template #default="scope">
          <el-tag :type="getPaymentStatusType(scope.row.payment_status)" effect="light" size="small">
            {{ getPaymentStatusText(scope.row.payment_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="approval_status" label="审批状态" width="90" align="center">
        <template #default="scope">
          <el-tag :type="getApprovalStatusType(scope.row.approval_status)" effect="light" size="small">
            {{ getApprovalStatusText(scope.row.approval_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="expected_close_date" label="预期完成" width="100" align="center">
        <template #default="scope">
          {{ scope.row.expected_close_date || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="scope">
          <el-button type="primary" link :icon="View" @click="emit('view', scope.row)">
            详情
          </el-button>
          <el-button type="primary" link :icon="Edit" @click="emit('edit', scope.row)" :disabled="scope.row.approval_status === 'pending'">
            编辑
          </el-button>
          <el-button 
            v-if="scope.row.approval_status === 'pending'" 
            type="success" 
            link 
            :icon="Check" 
            @click="emit('approve', scope.row)"
          >
            审批
          </el-button>
          <el-button type="danger" link :icon="Delete" @click="emit('delete', scope.row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        :current-page="currentPage"
        @update:current-page="val => emit('update:currentPage', val)"
        :page-size="pageSize"
        @update:page-size="val => emit('update:pageSize', val)"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredTotal"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </el-card>
</template>

<script setup>
import { View, Edit, Check, Delete } from '@element-plus/icons-vue'
import { getAvatarColor, formatNumber } from '../../utils/helpers'

const props = defineProps({
  paginatedDeals: Array,
  loading: Boolean,
  currentPage: Number,
  pageSize: Number,
  filteredTotal: Number
})

const emit = defineEmits(['view', 'edit', 'approve', 'delete', 'update:currentPage', 'update:pageSize'])

const getDealStatusText = (status) => {
  const statusMap = { 'negotiating': '谈判中', 'closed': '已完成', 'cancelled': '已取消' }
  return statusMap[status] || status
}

const getDealStatusType = (status) => {
  const typeMap = { 'negotiating': 'warning', 'closed': 'success', 'cancelled': 'info' }
  return typeMap[status] || 'info'
}

const getPaymentStatusText = (status) => {
  const statusMap = { 'unpaid': '未付款', 'partial': '部分付款', 'paid': '已付款' }
  return statusMap[status] || status
}

const getPaymentStatusType = (status) => {
  const typeMap = { 'unpaid': 'danger', 'partial': 'warning', 'paid': 'success' }
  return typeMap[status] || 'info'
}

const getApprovalStatusText = (status) => {
  const statusMap = { 'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝' }
  return statusMap[status] || status
}

const getApprovalStatusType = (status) => {
  const typeMap = { 'pending': 'warning', 'approved': 'success', 'rejected': 'danger' }
  return typeMap[status] || 'info'
}
</script>

<style scoped>
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
</style>