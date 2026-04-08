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
        <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
          添加交易
        </el-button>
      </div>
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
      <el-col :xs="24" :sm="8" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-label">总交易金额</div>
            <div class="stat-value amount">¥{{ formatAmount(totalAmount) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-label">已完成金额</div>
            <div class="stat-value success">¥{{ formatAmount(closedAmount) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-label">待审批交易</div>
            <div class="stat-value warning">{{ pendingApprovalCount }} 笔</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-label">未收款金额</div>
            <div class="stat-value danger">¥{{ formatAmount(unpaidAmount) }}</div>
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
            <el-button type="primary" link :icon="View" @click="viewDealDetails(scope.row)">
              详情
            </el-button>
            <el-button type="primary" link :icon="Edit" @click="editDeal(scope.row)" :disabled="scope.row.approval_status === 'pending'">
              编辑
            </el-button>
            <el-button 
              v-if="scope.row.approval_status === 'pending'" 
              type="success" 
              link 
              :icon="Check" 
              @click="showApprovalDialog(scope.row)"
            >
              审批
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
      width="700px"
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
          >
            <el-option
              v-for="customer in customerOptions"
              :key="customer.id"
              :label="customer.name"
              :value="customer.id"
            >
              <div class="customer-option">
                <span>{{ customer.name }}</span>
                <span v-if="customer.company" class="company">({{ customer.company }})</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="product_id">
          <el-select
            v-model="newDeal.product_id"
            placeholder="请选择产品"
            style="width: 100%"
            filterable
            clearable
            @change="onProductSelect"
          >
            <el-option
              v-for="product in productList"
              :key="product.id"
              :label="product.name"
              :value="product.id"
            >
              <div class="product-option">
                <span>{{ product.name }}</span>
                <span class="price">¥{{ product.price }}/{{ product.unit }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="数量" prop="quantity">
              <el-input-number
                v-model="newDeal.quantity"
                :min="1"
                :step="1"
                style="width: 100%"
                @change="calculateAmount"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number
                v-model="newDeal.unit_price"
                :min="0"
                :precision="2"
                style="width: 100%"
                @change="calculateAmount"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总金额" prop="amount">
              <el-input-number
                v-model="newDeal.amount"
                :min="0"
                :precision="2"
                style="width: 100%"
                disabled
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="交易状态" prop="deal_status">
              <el-select v-model="newDeal.deal_status" placeholder="请选择状态" style="width: 100%">
                <el-option label="谈判中" value="negotiating" />
                <el-option label="方案制定" value="proposal" />
                <el-option label="已完成" value="closed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="付款状态" prop="payment_status">
              <el-select v-model="newDeal.payment_status" placeholder="请选择付款状态" style="width: 100%">
                <el-option label="未付款" value="unpaid" />
                <el-option label="部分付款" value="partial" />
                <el-option label="已付款" value="paid" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="已付金额" prop="paid_amount">
              <el-input-number
                v-model="newDeal.paid_amount"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预期完成" prop="expected_close_date">
              <el-date-picker
                v-model="newDeal.expected_close_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="newDeal.notes" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
        <el-alert v-if="newDeal.amount >= 100000" type="warning" :closable="false" show-icon style="margin-top: 10px;">
          交易金额超过10万元，需要管理员审批
        </el-alert>
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
      width="700px"
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
          >
            <el-option
              v-for="customer in customerOptions"
              :key="customer.id"
              :label="customer.name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="product_id">
          <el-select
            v-model="editDealForm.product_id"
            placeholder="请选择产品"
            style="width: 100%"
            filterable
            clearable
            @change="onEditProductSelect"
          >
            <el-option
              v-for="product in productList"
              :key="product.id"
              :label="product.name"
              :value="product.id"
            >
              <div class="product-option">
                <span>{{ product.name }}</span>
                <span class="price">¥{{ product.price }}/{{ product.unit }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="数量" prop="quantity">
              <el-input-number
                v-model="editDealForm.quantity"
                :min="1"
                style="width: 100%"
                @change="calculateEditAmount"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number
                v-model="editDealForm.unit_price"
                :min="0"
                :precision="2"
                style="width: 100%"
                @change="calculateEditAmount"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总金额" prop="amount">
              <el-input-number
                v-model="editDealForm.amount"
                :min="0"
                :precision="2"
                style="width: 100%"
                disabled
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="交易状态" prop="deal_status">
              <el-select v-model="editDealForm.deal_status" placeholder="请选择状态" style="width: 100%">
                <el-option label="谈判中" value="negotiating" />
                <el-option label="方案制定" value="proposal" />
                <el-option label="已完成" value="closed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="付款状态" prop="payment_status">
              <el-select v-model="editDealForm.payment_status" placeholder="请选择付款状态" style="width: 100%">
                <el-option label="未付款" value="unpaid" />
                <el-option label="部分付款" value="partial" />
                <el-option label="已付款" value="paid" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="已付金额" prop="paid_amount">
              <el-input-number
                v-model="editDealForm.paid_amount"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预期完成" prop="expected_close_date">
              <el-date-picker
                v-model="editDealForm.expected_close_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="editDealForm.notes" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateDeal" :loading="updating">确定</el-button>
      </template>
    </el-dialog>

    <!-- 审批对话框 -->
    <el-dialog
      v-model="showApprovalDialogVisible"
      title="交易审批"
      width="500px"
      destroy-on-close
    >
      <div v-if="approvalDeal" class="approval-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="客户">{{ approvalDeal.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="产品">{{ approvalDeal.product_name }}</el-descriptions-item>
          <el-descriptions-item label="交易金额" :span="2">
            <span class="amount-text">¥{{ formatNumber(approvalDeal.amount) }}</span>
          </el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <el-form :model="approvalForm" label-width="80px">
          <el-form-item label="审批意见">
            <el-radio-group v-model="approvalForm.action">
              <el-radio label="approve">批准</el-radio>
              <el-radio label="reject">拒绝</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="approvalForm.comment" type="textarea" :rows="3" placeholder="请输入审批备注" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showApprovalDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApproval" :loading="approving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 交易详情对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="交易与跟进详情"
      width="700px"
      destroy-on-close
    >
      <div v-if="currentDeal" class="deal-detail-container">
        <el-descriptions :column="2" border class="mb-20">
          <el-descriptions-item label="客户姓名">{{ currentDeal.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="交易金额">
            <span class="amount-text">¥{{ formatNumber(currentDeal.amount) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="交易状态">
            <el-tag :type="getDealStatusType(currentDeal.deal_status)" effect="light">
              {{ getDealStatusText(currentDeal.deal_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="产品">{{ currentDeal.product || '-' }}</el-descriptions-item>
        </el-descriptions>

        <h4>关联跟进记录</h4>
        <el-timeline v-if="dealFollowUps.length > 0">
          <el-timeline-item
            v-for="(fu, index) in dealFollowUps"
            :key="index"
            :timestamp="formatDate(fu.created_at)"
            :type="fu.is_conversion ? 'success' : 'primary'"
            :hollow="!fu.is_conversion"
          >
            <el-card shadow="hover" class="timeline-card">
              <div class="timeline-header">
                <el-tag size="small">{{ fu.follow_type || '其他' }}</el-tag>
                <el-tag v-if="fu.is_conversion" size="small" type="success" effect="dark" style="margin-left: 8px;">
                  促成交易
                </el-tag>
              </div>
              <p class="timeline-content">{{ fu.content }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无关联跟进记录" />
      </div>
      <template #footer>
        <el-button @click="showViewDialog = false">关闭</el-button>
      </template>
    </el-dialog>

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
      @export-success="() => ElMessage.success('交易数据导出成功')"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Money, Plus, Search, RefreshRight, Edit, Delete, View, Calendar, Setting, Grid, Check, Download } from '@element-plus/icons-vue'
import ExportDialog from './ExportDialog.vue'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ role: 'user' })
  }
})

const isAdmin = computed(() => {
  return props.currentUser?.role === 'admin'
})

const deals = ref([])
const customers = ref([])
const customerOptions = ref([])
const productList = ref([])
const loading = ref(false)
const saving = ref(false)
const updating = ref(false)
const approving = ref(false)
const customerLoading = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const showApprovalDialogVisible = ref(false)
const currentDeal = ref(null)
const approvalDeal = ref(null)
const dealFollowUps = ref([])
const addFormRef = ref(null)
const editFormRef = ref(null)

const searchQuery = ref('')
const filterStatus = ref('')

const timeRange = ref('month')
const dateRange = ref([])

// 导出对话框
const showExportDialog = ref(false)

// 交易导出字段定义
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

// 默认导出字段
const defaultExportFields = ['id', 'customer_name', 'product_name', 'quantity', 'unit_price', 'amount', 'deal_status', 'payment_status', 'created_at']

// 获取当前筛选条件
const currentFilters = computed(() => {
  return {
    keyword: searchQuery.value,
    status: filterStatus.value,
    start_date: dateRange.value?.[0],
    end_date: dateRange.value?.[1]
  }
})

const currentPage = ref(1)
const pageSize = ref(10)

const newDeal = ref({
  customer_id: '',
  product_id: null,
  product_name: '',
  quantity: 1,
  unit_price: 0,
  amount: 0,
  deal_status: 'negotiating',
  payment_status: 'unpaid',
  paid_amount: 0,
  expected_close_date: '',
  notes: ''
})

const editDealForm = ref({
  id: null,
  customer_id: '',
  product_id: null,
  product_name: '',
  quantity: 1,
  unit_price: 0,
  amount: 0,
  deal_status: 'negotiating',
  payment_status: 'unpaid',
  paid_amount: 0,
  expected_close_date: '',
  notes: ''
})

const approvalForm = ref({
  action: 'approve',
  comment: ''
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

// 格式化日期 - 正确处理UTC时间
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  // 加上8小时时差（中国时区）
  const localDate = new Date(date.getTime() + 8 * 60 * 60 * 1000)
  return localDate.toLocaleString('zh-CN', {
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

const pendingApprovalCount = computed(() => {
  return filteredDeals.value.filter(deal => deal.approval_status === 'pending').length
})

const unpaidAmount = computed(() => {
  return filteredDeals.value
    .filter(deal => deal.payment_status !== 'paid')
    .reduce((sum, deal) => sum + ((parseFloat(deal.amount) || 0) - (parseFloat(deal.paid_amount) || 0)), 0)
})

const filteredDeals = computed(() => {
  let result = deals.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(deal =>
      deal.customer_name?.toLowerCase().includes(query) ||
      deal.product_name?.toLowerCase().includes(query)
    )
  }

  if (filterStatus.value) {
    result = result.filter(deal => deal.deal_status === filterStatus.value)
  }

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

const paginatedDeals = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDeals.value.slice(start, end)
})

const filteredTotal = computed(() => filteredDeals.value.length)
const total = computed(() => deals.value.length)

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

const fetchCustomers = async () => {
  try {
    const response = await axios.get('/api/customers')
    customers.value = response.data
    customerOptions.value = response.data
  } catch (error) {
    console.error('获取客户列表失败:', error)
  }
}

const fetchProducts = async () => {
  try {
    const response = await axios.get('/api/products')
    productList.value = response.data
  } catch (error) {
    console.error('获取产品列表失败:', error)
  }
}

const onProductSelect = (productId) => {
  const product = productList.value.find(p => p.id === productId)
  if (product) {
    newDeal.value.product_name = product.name
    newDeal.value.unit_price = product.price
    calculateAmount()
  }
}

const onEditProductSelect = (productId) => {
  const product = productList.value.find(p => p.id === productId)
  if (product) {
    editDealForm.value.product_name = product.name
    editDealForm.value.unit_price = product.price
    calculateEditAmount()
  }
}

const calculateAmount = () => {
  newDeal.value.amount = (newDeal.value.quantity || 1) * (newDeal.value.unit_price || 0)
}

const calculateEditAmount = () => {
  editDealForm.value.amount = (editDealForm.value.quantity || 1) * (editDealForm.value.unit_price || 0)
}

const getPaymentStatusText = (status) => {
  const statusMap = {
    'unpaid': '未付款',
    'partial': '部分付款',
    'paid': '已付款'
  }
  return statusMap[status] || status
}

const getPaymentStatusType = (status) => {
  const typeMap = {
    'unpaid': 'danger',
    'partial': 'warning',
    'paid': 'success'
  }
  return typeMap[status] || 'info'
}

const getApprovalStatusText = (status) => {
  const statusMap = {
    'pending': '待审批',
    'approved': '已批准',
    'rejected': '已拒绝'
  }
  return statusMap[status] || status
}

const getApprovalStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return typeMap[status] || 'info'
}

const showApprovalDialog = (deal) => {
  approvalDeal.value = deal
  approvalForm.value = { action: 'approve', comment: '' }
  showApprovalDialogVisible.value = true
}

const submitApproval = async () => {
  if (!approvalDeal.value) return
  
  approving.value = true
  try {
    const response = await axios.post(`/api/deals/${approvalDeal.value.id}/approve`, {
      action: approvalForm.value.action,
      comment: approvalForm.value.comment,
      approver_id: props.currentUser?.id || 1
    })
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
      showApprovalDialogVisible.value = false
      fetchDeals()
    } else {
      ElMessage.error(response.data.message || '审批失败')
    }
  } catch (error) {
    console.error('审批失败:', error)
    ElMessage.error(error.response?.data?.message || '审批失败')
  } finally {
    approving.value = false
  }
}

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

// 查看详情
const viewDealDetails = async (deal) => {
  currentDeal.value = deal
  showViewDialog.value = true
  try {
    const res = await axios.get('/api/follow-ups', { params: { deal_id: deal.id } })
    dealFollowUps.value = res.data
  } catch (error) {
    console.error('获取跟进记录失败:', error)
  }
}

// 编辑交易
const editDeal = async (deal) => {
  editDealForm.value = {
    id: deal.id,
    customer_id: deal.customer_id,
    product_id: deal.product_id,
    product_name: deal.product_name || '',
    quantity: deal.quantity || 1,
    unit_price: deal.unit_price || 0,
    amount: deal.amount,
    deal_status: deal.deal_status,
    payment_status: deal.payment_status || 'unpaid',
    paid_amount: deal.paid_amount || 0,
    expected_close_date: deal.expected_close_date || '',
    notes: deal.notes || ''
  }
  customerLoading.value = true
  try {
    const response = await axios.get('/api/customers')
    customerOptions.value = response.data
  } catch (error) {
    console.error('加载客户列表失败:', error)
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
    product_id: null,
    product_name: '',
    quantity: 1,
    unit_price: 0,
    amount: 0,
    deal_status: 'negotiating',
    payment_status: 'unpaid',
    paid_amount: 0,
    expected_close_date: '',
    notes: ''
  }
  addFormRef.value?.resetFields()
}

const resetEditForm = () => {
  editDealForm.value = {
    id: null,
    customer_id: '',
    product_id: null,
    product_name: '',
    quantity: 1,
    unit_price: 0,
    amount: 0,
    deal_status: 'negotiating',
    payment_status: 'unpaid',
    paid_amount: 0,
    expected_close_date: '',
    notes: ''
  }
  editFormRef.value?.resetFields()
}

onMounted(() => {
  fetchDeals()
  fetchCustomers()
  fetchProducts()
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
