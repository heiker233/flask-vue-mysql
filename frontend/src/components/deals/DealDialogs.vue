<template>
  <div>
    <!-- 添加交易对话框 -->
    <el-dialog v-model="showAddDialog" title="添加交易" width="700px" destroy-on-close>
      <el-form ref="addFormRef" :model="newDeal" :rules="dealRules" label-width="100px" status-icon>
        <el-form-item label="客户" prop="customer_id">
          <el-select v-model="newDeal.customer_id" placeholder="请选择客户" style="width: 100%" filterable>
            <el-option v-for="customer in customerOptions" :key="customer.id" :label="customer.name" :value="customer.id">
              <div class="customer-option">
                <span>{{ customer.name }}</span>
                <span v-if="customer.company" class="company">({{ customer.company }})</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="product_id">
          <el-select v-model="newDeal.product_id" placeholder="请选择产品" style="width: 100%" filterable clearable @change="onProductSelect">
            <el-option v-for="product in productList" :key="product.id" :label="product.name" :value="product.id">
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
              <el-input-number v-model="newDeal.quantity" :min="1" :step="1" style="width: 100%" @change="calculateAmount" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number v-model="newDeal.unit_price" :min="0" :precision="2" style="width: 100%" @change="calculateAmount" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总金额" prop="amount">
              <el-input-number v-model="newDeal.amount" :min="0" :precision="2" style="width: 100%" disabled />
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
              <el-input-number v-model="newDeal.paid_amount" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预期完成" prop="expected_close_date">
              <el-date-picker v-model="newDeal.expected_close_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
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
    <el-dialog v-model="showEditDialog" title="编辑交易" width="700px" destroy-on-close>
      <el-form ref="editFormRef" :model="editDealForm" :rules="dealRules" label-width="100px" status-icon>
        <el-form-item label="客户" prop="customer_id">
          <el-select v-model="editDealForm.customer_id" placeholder="请选择客户" style="width: 100%" filterable>
            <el-option v-for="customer in customerOptions" :key="customer.id" :label="customer.name" :value="customer.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="product_id">
          <el-select v-model="editDealForm.product_id" placeholder="请选择产品" style="width: 100%" filterable clearable @change="onEditProductSelect">
            <el-option v-for="product in productList" :key="product.id" :label="product.name" :value="product.id">
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
              <el-input-number v-model="editDealForm.quantity" :min="1" style="width: 100%" @change="calculateEditAmount" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number v-model="editDealForm.unit_price" :min="0" :precision="2" style="width: 100%" @change="calculateEditAmount" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总金额" prop="amount">
              <el-input-number v-model="editDealForm.amount" :min="0" :precision="2" style="width: 100%" disabled />
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
              <el-input-number v-model="editDealForm.paid_amount" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预期完成" prop="expected_close_date">
              <el-date-picker v-model="editDealForm.expected_close_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
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
    <el-dialog v-model="showApprovalDialogVisible" title="交易审批" width="500px" destroy-on-close>
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
        <el-button type="primary" @click="onApprove" :loading="approving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 交易详情对话框 -->
    <el-dialog v-model="showViewDialog" title="交易与跟进详情" width="700px" destroy-on-close>
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
          <el-timeline-item v-for="(fu, index) in dealFollowUps" :key="index" :timestamp="formatDate(fu.created_at)" :type="fu.is_conversion ? 'success' : 'primary'" :hollow="!fu.is_conversion">
            <el-card shadow="hover" class="timeline-card">
              <div class="timeline-header">
                <el-tag size="small">{{ fu.follow_type || '其他' }}</el-tag>
                <el-tag v-if="fu.is_conversion" size="small" type="success" effect="dark" style="margin-left: 8px;">促成交易</el-tag>
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { formatNumber, formatDate } from '../../utils/helpers'

const props = defineProps({
  customerOptions: Array,
  productList: Array,
  currentUser: Object
})

const emit = defineEmits(['refresh', 'submit-approval'])

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const showApprovalDialogVisible = ref(false)

const saving = ref(false)
const updating = ref(false)
const approving = ref(false)

const addFormRef = ref(null)
const editFormRef = ref(null)

const newDeal = ref({
  customer_id: '', product_id: null, product_name: '', quantity: 1, unit_price: 0, amount: 0, deal_status: 'negotiating', payment_status: 'unpaid', paid_amount: 0, expected_close_date: '', notes: ''
})

const editDealForm = ref({
  id: null, customer_id: '', product_id: null, product_name: '', quantity: 1, unit_price: 0, amount: 0, deal_status: 'negotiating', payment_status: 'unpaid', paid_amount: 0, expected_close_date: '', notes: ''
})

const approvalForm = ref({ action: 'approve', comment: '' })
const approvalDeal = ref(null)
const currentDeal = ref(null)
const dealFollowUps = ref([])

const dealRules = {
  customer_id: [{ required: true, message: '请选择客户', trigger: 'change' }],
  amount: [
    { required: true, message: '请输入交易金额', trigger: 'blur' },
    { type: 'number', min: 0, message: '金额必须大于0', trigger: 'blur' }
  ],
  deal_status: [{ required: true, message: '请选择交易状态', trigger: 'change' }]
}

const openAdd = () => {
  resetForm()
  showAddDialog.value = true
}

const openEdit = (deal) => {
  editDealForm.value = {
    id: deal.id, customer_id: deal.customer_id, product_id: deal.product_id, product_name: deal.product_name || '', quantity: deal.quantity || 1, unit_price: deal.unit_price || 0, amount: deal.amount, deal_status: deal.deal_status, payment_status: deal.payment_status || 'unpaid', paid_amount: deal.paid_amount || 0, expected_close_date: deal.expected_close_date || '', notes: deal.notes || ''
  }
  showEditDialog.value = true
}

const openView = async (deal) => {
  currentDeal.value = deal
  showViewDialog.value = true
  try {
    const res = await axios.get('/api/follow-ups', { params: { deal_id: deal.id } })
    dealFollowUps.value = res.data
  } catch (error) {
    console.error('获取跟进记录失败:', error)
  }
}

const openApprove = (deal) => {
  approvalDeal.value = deal
  approvalForm.value = { action: 'approve', comment: '' }
  showApprovalDialogVisible.value = true
}

const onProductSelect = (productId) => {
  const product = props.productList.find(p => p.id === productId)
  if (product) {
    newDeal.value.product_name = product.name
    newDeal.value.unit_price = product.price
    calculateAmount()
  }
}

const onEditProductSelect = (productId) => {
  const product = props.productList.find(p => p.id === productId)
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

const saveDeal = async () => {
  if (!addFormRef.value) return
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await axios.post('/api/deals', newDeal.value)
        ElMessage.success('交易记录添加成功')
        emit('refresh')
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

const updateDeal = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await axios.put(`/api/deals/${editDealForm.value.id}`, editDealForm.value)
        ElMessage.success('交易记录更新成功')
        emit('refresh')
        showEditDialog.value = false
      } catch (error) {
        console.error('更新交易记录失败:', error)
        ElMessage.error(error.response?.data?.message || '更新交易记录失败')
      } finally {
        updating.value = false
      }
    }
  })
}

const onApprove = async () => {
  approving.value = true
  emit('submit-approval', approvalDeal.value, approvalForm.value)
  // Approval dialog closing will be handled by the parent if successful, 
  // or we can handle the async call directly here if we want.
  // Wait, let's keep it simple and just emit, but how to handle loading?
  // Let's pass a callback or just do it here since useDeals has submitApproval.
  // Actually, I can use the emit and wait, or handle it via a watch on a prop.
  // To avoid complexity, I'll export a method from `DealDialogs` or just handle logic here.
}

// Alternative for onApprove since `useDeals` has submitApproval:
// Actually, the emit should probably be awaited. 
// But Vue 3 emits are not naturally awaitable unless passed as props or promises.
// Let's just handle the API call here for approve as well to keep logic together with loading state,
// BUT the prompt explicitly said `submitApproval` is in `useDeals()`.
// So let's emit and expose a `closeApprovalDialog` method.
const closeApprovalDialog = () => {
  showApprovalDialogVisible.value = false
  approving.value = false
}
const stopApproveLoading = () => { approving.value = false }

const resetForm = () => {
  newDeal.value = { customer_id: '', product_id: null, product_name: '', quantity: 1, unit_price: 0, amount: 0, deal_status: 'negotiating', payment_status: 'unpaid', paid_amount: 0, expected_close_date: '', notes: '' }
  addFormRef.value?.resetFields()
}

const getDealStatusText = (status) => {
  const statusMap = { 'negotiating': '谈判中', 'closed': '已完成', 'cancelled': '已取消' }
  return statusMap[status] || status
}

const getDealStatusType = (status) => {
  const typeMap = { 'negotiating': 'warning', 'closed': 'success', 'cancelled': 'info' }
  return typeMap[status] || 'info'
}

defineExpose({
  openAdd,
  openEdit,
  openView,
  openApprove,
  closeApprovalDialog,
  stopApproveLoading
})
</script>

<style scoped>
.customer-option {
  display: flex;
  align-items: center;
  gap: 8px;
}
.customer-option .company {
  color: #909399;
  font-size: 12px;
}
.product-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.product-option .price {
  color: #f56c6c;
  font-size: 12px;
}
.amount-text {
  font-weight: 600;
  color: #f56c6c;
  font-size: 18px;
}
.deal-detail-container h4 {
  margin: 20px 0 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}
.timeline-card {
  margin-bottom: 8px;
}
.timeline-header {
  margin-bottom: 8px;
}
.timeline-content {
  margin: 0;
  color: #606266;
  font-size: 14px;
}
.mb-20 {
  margin-bottom: 20px;
}
</style>