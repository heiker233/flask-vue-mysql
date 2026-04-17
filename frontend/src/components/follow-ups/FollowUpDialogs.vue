<template>
  <div>
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
        <el-form-item label="关联交易" prop="deal_id">
          <el-select
            v-model="newFollowUp.deal_id"
            placeholder="请选择关联交易（可选）"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="deal in currentCustomerDeals"
              :key="deal.id"
              :label="deal.product ? deal.product + ' (¥' + deal.amount + ')' : '交易 ¥' + deal.amount"
              :value="deal.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="促成交易" prop="is_conversion">
          <el-switch v-model="newFollowUp.is_conversion" active-text="是" inactive-text="否" />
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
        <el-form-item label="关联交易" prop="deal_id">
          <el-select
            v-model="editFollowUpForm.deal_id"
            placeholder="请选择关联交易（可选）"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="deal in currentCustomerDeals"
              :key="deal.id"
              :label="deal.product ? deal.product + ' (¥' + deal.amount + ')' : '交易 ¥' + deal.amount"
              :value="deal.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="促成交易" prop="is_conversion">
          <el-switch v-model="editFollowUpForm.is_conversion" active-text="是" inactive-text="否" />
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
import { ref, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['refresh'])

// Dialog states
const showAddDialog = ref(false)
const showEditDialog = ref(false)

// Action states
const saving = ref(false)
const updating = ref(false)
const customerLoading = ref(false)

const addFormRef = ref(null)
const editFormRef = ref(null)

const customerOptions = ref([])
const currentCustomerDeals = ref([])

// Form datas
const newFollowUp = ref({
  customer_id: '',
  content: '',
  follow_type: '',
  next_follow_date: '',
  deal_id: null,
  is_conversion: false
})

const editFollowUpForm = ref({
  id: null,
  customer_id: '',
  content: '',
  follow_type: '',
  next_follow_date: '',
  deal_id: null,
  is_conversion: false
})

// Validation
const followUpRules = {
  customer_id: [{ required: true, message: '请选择客户', trigger: 'change' }],
  content: [
    { required: true, message: '请输入跟进内容', trigger: 'blur' },
    { min: 5, max: 500, message: '内容长度在 5 到 500 个字符', trigger: 'blur' }
  ],
  follow_type: [{ required: true, message: '请选择跟进方式', trigger: 'change' }]
}

// 监听客户ID变化以获取该客户的交易
const fetchCustomerDeals = async (newVal) => {
  if (newVal) {
    try {
      const res = await axios.get('/api/deals')
      currentCustomerDeals.value = res.data.filter(d => d.customer_id === newVal)
    } catch (e) {
      console.error('获取交易列表失败', e)
    }
  } else {
    currentCustomerDeals.value = []
  }
}

watch(() => newFollowUp.value.customer_id, fetchCustomerDeals)
watch(() => editFollowUpForm.value.customer_id, fetchCustomerDeals)

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

const saveFollowUp = async () => {
  if (!addFormRef.value) return
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await axios.post('/api/follow-ups', newFollowUp.value)
        ElMessage.success('跟进记录添加成功')
        emit('refresh')
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

const updateFollowUp = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await axios.put(`/api/follow-ups/${editFollowUpForm.value.id}`, editFollowUpForm.value)
        ElMessage.success('跟进记录更新成功')
        emit('refresh')
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

// Exposed methods
const openAdd = () => {
  resetAddForm()
  showAddDialog.value = true
}

const openEdit = async (followUp) => {
  editFollowUpForm.value = {
    id: followUp.id,
    customer_id: followUp.customer_id,
    content: followUp.content,
    follow_type: followUp.follow_type,
    next_follow_date: followUp.next_follow_date,
    deal_id: followUp.deal_id,
    is_conversion: followUp.is_conversion
  }
  
  customerLoading.value = true
  try {
    const response = await axios.get('/api/customers')
    customerOptions.value = response.data
  } catch (error) {
    console.error('加载客户列表失败:', error)
    if (followUp.customer_id && followUp.customer_name) {
      customerOptions.value = [{ id: followUp.customer_id, name: followUp.customer_name }]
    }
  } finally {
    customerLoading.value = false
  }
  
  showEditDialog.value = true
}

const resetAddForm = () => {
  newFollowUp.value = {
    customer_id: '',
    content: '',
    follow_type: '',
    next_follow_date: '',
    deal_id: null,
    is_conversion: false
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
    next_follow_date: '',
    deal_id: null,
    is_conversion: false
  }
  customerOptions.value = []
  editFormRef.value?.resetFields()
}

defineExpose({
  openAdd,
  openEdit
})
</script>
