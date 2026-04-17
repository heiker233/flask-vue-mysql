<template>
  <div>
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
        <el-form-item label="价值评分" prop="value_score">
          <el-rate v-model="newCustomer.value_score" :max="5" show-score />
        </el-form-item>
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
        <el-form-item label="价值评分" prop="value_score">
          <el-rate v-model="editCustomerForm.value_score" :max="5" show-score />
        </el-form-item>
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
          <el-button type="primary" @click="showViewDialog = false; openEdit(currentCustomer)">
            编辑客户
          </el-button>
          <el-button @click="showViewDialog = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 分配客户对话框 -->
    <el-dialog
      v-model="showAssignDialog"
      title="分配客户"
      width="400px"
      destroy-on-close
    >
      <el-form label-width="100px">
        <el-form-item label="分配给">
          <el-select v-model="assignForm.assigned_to" placeholder="请选择负责人" style="width: 100%">
            <el-option label="未分配" :value="null" />
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAssignDialog = false">取消</el-button>
        <el-button type="primary" @click="submitAssign" :loading="assigning">确定</el-button>
      </template>
    </el-dialog>

    <!-- 评分编辑对话框 -->
    <el-dialog
      v-model="showScoreEditDialog"
      title="修改客户评分"
      width="400px"
      destroy-on-close
    >
      <el-form label-width="80px">
        <el-form-item label="客户">
          <span>{{ scoreEditForm.name }}</span>
        </el-form-item>
        <el-form-item label="评分">
          <el-rate 
            v-model="scoreEditForm.value_score" 
            :max="5"
            show-score
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showScoreEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveScore">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getAvatarColor, formatDate } from '../../utils/helpers'

const props = defineProps({
  industryOptions: Array
})

const emit = defineEmits([
  'customer-added',
  'customer-updated',
  'customer-assigned',
  'score-updated'
])

// Dialog states
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const showAssignDialog = ref(false)
const showScoreEditDialog = ref(false)

// Form refs
const addFormRef = ref(null)
const editFormRef = ref(null)

// Action states
const saving = ref(false)
const updating = ref(false)
const assigning = ref(false)

// Forms & Data
const newCustomer = ref({
  name: '', phone: '', email: '', company: '', industry: '', status: 'potential', value_score: 3, notes: ''
})

const editCustomerForm = ref({
  id: null, name: '', phone: '', email: '', company: '', industry: '', status: 'potential', value_score: 3, notes: ''
})

const currentCustomer = ref(null)

const assignForm = ref({
  id: null, assigned_to: null
})

const scoreEditForm = ref({
  id: null, name: '', value_score: 0
})

const userOptions = ref([])

// Validation rules
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

const getCustomerStatusText = (status) => {
  const statusMap = { 'potential': '潜在客户', 'active': '活跃客户', 'lost': '已流失客户' }
  return statusMap[status] || status
}

const getCustomerStatusType = (status) => {
  const typeMap = { 'potential': 'warning', 'active': 'success', 'lost': 'info' }
  return typeMap[status] || 'info'
}

const resetForm = () => {
  newCustomer.value = {
    name: '', phone: '', email: '', company: '', industry: '', status: 'potential', value_score: 3, notes: ''
  }
  addFormRef.value?.resetFields()
}

const resetEditForm = () => {
  editCustomerForm.value = {
    id: null, name: '', phone: '', email: '', company: '', industry: '', status: 'potential', value_score: 3, notes: ''
  }
  editFormRef.value?.resetFields()
}

// API Actions
const saveCustomer = async () => {
  if (!addFormRef.value) return
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const response = await axios.post('/api/customers', newCustomer.value)
        const newCustomerData = response.data.customer || {
          ...newCustomer.value,
          id: response.data.id,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        emit('customer-added', newCustomerData)
        ElMessage.success('客户添加成功')
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

const updateCustomer = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await axios.put(`/api/customers/${editCustomerForm.value.id}`, editCustomerForm.value)
        emit('customer-updated', editCustomerForm.value)
        ElMessage.success('客户更新成功')
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

const submitAssign = async () => {
  assigning.value = true
  try {
    await axios.put(`/api/customers/${assignForm.value.id}/assign`, {
      assigned_to: assignForm.value.assigned_to
    })
    const user = userOptions.value.find(u => u.id === assignForm.value.assigned_to)
    emit('customer-assigned', {
      id: assignForm.value.id,
      assigned_to: assignForm.value.assigned_to,
      assignee: user
    })
    ElMessage.success('客户分配成功')
    showAssignDialog.value = false
  } catch (error) {
    console.error('分配客户失败:', error)
    ElMessage.error(error.response?.data?.message || '分配客户失败')
  } finally {
    assigning.value = false
  }
}

const saveScore = async () => {
  try {
    await axios.put(`/api/customers/${scoreEditForm.value.id}`, { 
      value_score: scoreEditForm.value.value_score 
    })
    emit('score-updated', {
      id: scoreEditForm.value.id,
      value_score: scoreEditForm.value.value_score
    })
    ElMessage.success('评分更新成功')
    showScoreEditDialog.value = false
  } catch (error) {
    console.error('更新评分失败:', error)
    ElMessage.error(error.response?.data?.message || '更新评分失败')
  }
}

// Exposed Methods
const openAdd = () => {
  resetForm()
  showAddDialog.value = true
}

const openEdit = (customer) => {
  editCustomerForm.value = {
    id: customer.id, name: customer.name, phone: customer.phone,
    email: customer.email, company: customer.company, industry: customer.industry,
    status: customer.status, value_score: customer.value_score || 3, notes: customer.notes || ''
  }
  showEditDialog.value = true
}

const openView = (customer) => {
  currentCustomer.value = customer
  showViewDialog.value = true
}

const openAssign = async (customer) => {
  assignForm.value = {
    id: customer.id,
    assigned_to: customer.assigned_to
  }
  if (userOptions.value.length === 0) {
    try {
      const response = await axios.get('/api/users')
      userOptions.value = response.data
    } catch (error) {
      console.error('获取用户列表失败', error)
    }
  }
  showAssignDialog.value = true
}

const openScoreEdit = (customer) => {
  scoreEditForm.value = {
    id: customer.id,
    name: customer.name,
    value_score: customer.value_score || 0
  }
  showScoreEditDialog.value = true
}

defineExpose({
  openAdd,
  openEdit,
  openView,
  openAssign,
  openScoreEdit
})
</script>

<style scoped>
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

.text-gray {
  color: #909399;
}
</style>
