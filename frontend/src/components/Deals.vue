<template>
  <div class="deals-container">
    <div class="page-header">
      <h2>交易管理</h2>
      <el-button type="primary" @click="showAddDialog = true">添加交易</el-button>
    </div>
    <el-table :data="deals" border stripe style="width: 100%" max-height="600">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="customer_id" label="客户ID" />
      <el-table-column prop="amount" label="交易金额" />
      <el-table-column prop="deal_status" label="状态" />
      <el-table-column prop="product" label="产品" />
      <el-table-column prop="expected_close_date" label="预期完成时间" />
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button type="link" @click="editDeal(scope.row)">编辑</el-button>
          <el-button type="link" danger @click="deleteDeal(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="showAddDialog"
      title="添加交易"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="newDeal" label-width="120px">
        <el-form-item label="客户ID" prop="customer_id" required>
          <el-input v-model.number="newDeal.customer_id" placeholder="请输入客户ID" />
        </el-form-item>
        <el-form-item label="交易金额" prop="amount" required>
          <el-input v-model.number="newDeal.amount" placeholder="请输入交易金额" />
        </el-form-item>
        <el-form-item label="产品" prop="product">
          <el-input v-model="newDeal.product" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="状态" prop="deal_status">
          <el-select v-model="newDeal.deal_status" placeholder="请选择交易状态">
            <el-option label="谈判中" value="negotiating" />
            <el-option label="已完成" value="closed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="预期完成时间" prop="expected_close_date">
          <el-date-picker
            v-model="newDeal.expected_close_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDeal">确定</el-button>
      </template>
    </el-dialog>
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑交易"
      width="600px"
      @close="resetEditForm"
    >
      <el-form :model="editDealForm" label-width="120px"
      >
        <el-form-item label="客户ID" prop="customer_id" required
        >
          <el-input v-model.number="editDealForm.customer_id" placeholder="请输入客户ID" />
        </el-form-item>
        <el-form-item label="交易金额" prop="amount" required
        >
          <el-input v-model.number="editDealForm.amount" placeholder="请输入交易金额" />
        </el-form-item>
        <el-form-item label="产品" prop="product"
        >
          <el-input v-model="editDealForm.product" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="状态" prop="deal_status"
        >
          <el-select v-model="editDealForm.deal_status" placeholder="请选择交易状态"
          >
            <el-option label="谈判中" value="negotiating" />
            <el-option label="已完成" value="closed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="预期完成时间" prop="expected_close_date"
        >
          <el-date-picker
            v-model="editDealForm.expected_close_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateDeal">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const deals = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const newDeal = ref({
  customer_id: '',
  amount: '',
  deal_status: 'negotiating',
  product: '',
  expected_close_date: ''
})
const editDealForm = ref({
  id: null,
  customer_id: '',
  amount: '',
  deal_status: 'negotiating',
  product: '',
  expected_close_date: ''
})

const fetchDeals = async () => {
  try {
    const response = await axios.get('/api/deals')
    deals.value = response.data
  } catch (error) {
    console.error('获取交易记录失败:', error)
    const errorMessage = error.response?.data?.message || '获取交易记录列表失败'
    ElMessage.error(errorMessage)
  }
}

const saveDeal = async () => {
  try {
    await axios.post('/api/deals', newDeal.value)
    ElMessage.success('交易记录添加成功')
    fetchDeals()
    showAddDialog.value = false
    resetForm()
  } catch (error) {
    console.error('保存交易记录失败:', error)
    const errorMessage = error.response?.data?.message || '保存交易记录失败'
    ElMessage.error(errorMessage)
  }
}

const deleteDeal = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条交易记录吗？', '确认删除', {
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
      const errorMessage = error.response?.data?.message || '删除交易记录失败'
      ElMessage.error(errorMessage)
    }
  }
}

const editDeal = (deal) => {
  editDealForm.value = {
    id: deal.id,
    customer_id: deal.customer_id,
    amount: deal.amount,
    deal_status: deal.deal_status,
    product: deal.product,
    expected_close_date: deal.expected_close_date
  }
  showEditDialog.value = true
}

const updateDeal = async () => {
  try {
    await axios.put(`/api/deals/${editDealForm.value.id}`, editDealForm.value)
    ElMessage.success('交易记录更新成功')
    fetchDeals()
    showEditDialog.value = false
    resetEditForm()
  } catch (error) {
    console.error('更新交易记录失败:', error)
    const errorMessage = error.response?.data?.message || '更新交易记录失败'
    ElMessage.error(errorMessage)
  }
}

const resetForm = () => {
  newDeal.value = {
    customer_id: '',
    amount: '',
    deal_status: 'negotiating',
    product: '',
    expected_close_date: ''
  }
}

const resetEditForm = () => {
  editDealForm.value = {
    id: null,
    customer_id: '',
    amount: '',
    deal_status: 'negotiating',
    product: '',
    expected_close_date: ''
  }
}

onMounted(() => {
  fetchDeals()
})
</script>

<style scoped>
.deals-container {
  height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>