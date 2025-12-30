<template>
  <div class="customers-container">
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="showAddDialog = true">添加客户</el-button>
    </div>
    <el-table :data="customers" border stripe style="width: 100%" max-height="600">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="phone" label="电话" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="company" label="公司" />
      <el-table-column prop="industry" label="行业" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button type="link" @click="editCustomer(scope.row)">编辑</el-button>
          <el-button type="link" danger @click="deleteCustomer(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="showAddDialog"
      title="添加客户"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="newCustomer" label-width="120px">
        <el-form-item label="姓名" prop="name" required>
          <el-input v-model="newCustomer.name" placeholder="请输入客户姓名" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="newCustomer.phone" placeholder="请输入客户电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="newCustomer.email" placeholder="请输入客户邮箱" />
        </el-form-item>
        <el-form-item label="公司" prop="company">
          <el-input v-model="newCustomer.company" placeholder="请输入客户公司" />
        </el-form-item>
        <el-form-item label="行业" prop="industry">
          <el-input v-model="newCustomer.industry" placeholder="请输入客户行业" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="newCustomer.status" placeholder="请选择客户状态">
            <el-option label="潜在客户" value="potential" />
            <el-option label="活跃客户" value="active" />
            <el-option label="已流失客户" value="lost" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCustomer">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showEditDialog"
      title="编辑客户"
      width="600px"
      @close="resetEditForm"
    >
      <el-form :model="editCustomerForm" label-width="120px">
        <el-form-item label="姓名" prop="name" required>
          <el-input v-model="editCustomerForm.name" placeholder="请输入客户姓名" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="editCustomerForm.phone" placeholder="请输入客户电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editCustomerForm.email" placeholder="请输入客户邮箱" />
        </el-form-item>
        <el-form-item label="公司" prop="company">
          <el-input v-model="editCustomerForm.company" placeholder="请输入客户公司" />
        </el-form-item>
        <el-form-item label="行业" prop="industry">
          <el-input v-model="editCustomerForm.industry" placeholder="请输入客户行业" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="editCustomerForm.status" placeholder="请选择客户状态">
            <el-option label="潜在客户" value="potential" />
            <el-option label="活跃客户" value="active" />
            <el-option label="已流失客户" value="lost" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateCustomer">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const customers = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const newCustomer = ref({
  name: '',
  phone: '',
  email: '',
  company: '',
  industry: '',
  status: 'potential'
})
const editCustomerForm = ref({
  id: null,
  name: '',
  phone: '',
  email: '',
  company: '',
  industry: '',
  status: 'potential'
})

const fetchCustomers = async () => {
  try {
    const response = await axios.get('/api/customers')
    customers.value = response.data
  } catch (error) {
    console.error('获取客户失败:', error)
    const errorMessage = error.response?.data?.message || '获取客户列表失败'
    ElMessage.error(errorMessage)
  }
}

const saveCustomer = async () => {
  try {
    await axios.post('/api/customers', newCustomer.value)
    ElMessage.success('客户添加成功')
    fetchCustomers()
    showAddDialog.value = false
    resetForm()
  } catch (error) {
    console.error('保存客户失败:', error)
    const errorMessage = error.response?.data?.message || '保存客户失败'
    ElMessage.error(errorMessage)
  }
}

const deleteCustomer = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个客户吗？', '确认删除', {
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
      const errorMessage = error.response?.data?.message || '删除客户失败'
      ElMessage.error(errorMessage)
    }
  }
}

const editCustomer = (customer) => {
  editCustomerForm.value = {
    id: customer.id,
    name: customer.name,
    phone: customer.phone,
    email: customer.email,
    company: customer.company,
    industry: customer.industry,
    status: customer.status
  }
  showEditDialog.value = true
}

const updateCustomer = async () => {
  try {
    await axios.put(`/api/customers/${editCustomerForm.value.id}`, editCustomerForm.value)
    ElMessage.success('客户更新成功')
    fetchCustomers()
    showEditDialog.value = false
    resetEditForm()
  } catch (error) {
    console.error('更新客户失败:', error)
    const errorMessage = error.response?.data?.message || '更新客户失败'
    ElMessage.error(errorMessage)
  }
}

const resetForm = () => {
  newCustomer.value = {
    name: '',
    phone: '',
    email: '',
    company: '',
    industry: '',
    status: 'potential'
  }
}

const resetEditForm = () => {
  editCustomerForm.value = {
    id: null,
    name: '',
    phone: '',
    email: '',
    company: '',
    industry: '',
    status: 'potential'
  }
}

onMounted(() => {
  fetchCustomers()
})
</script>

<style scoped>
.customers-container {
  height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>