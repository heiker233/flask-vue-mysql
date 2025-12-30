<template>
  <div class="follow-ups-container">
    <div class="page-header">
      <h2>跟进记录</h2>
      <el-button type="primary" @click="showAddDialog = true">添加记录</el-button>
    </div>
    <el-table :data="followUps" border stripe style="width: 100%" max-height="600">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="customer_id" label="客户ID" />
      <el-table-column prop="content" label="内容" />
      <el-table-column prop="follow_type" label="跟进方式" />
      <el-table-column prop="next_follow_date" label="下次跟进时间" />
      <el-table-column prop="created_at" label="记录时间" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button type="link" @click="editFollowUp(scope.row)">编辑</el-button>
          <el-button type="link" danger @click="deleteFollowUp(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="showAddDialog"
      title="添加跟进记录"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="newFollowUp" label-width="120px">
        <el-form-item label="客户ID" prop="customer_id" required>
          <el-input v-model.number="newFollowUp.customer_id" placeholder="请输入客户ID" />
        </el-form-item>
        <el-form-item label="跟进内容" prop="content" required>
          <el-input type="textarea" v-model="newFollowUp.content" rows="3" placeholder="请输入跟进内容" />
        </el-form-item>
        <el-form-item label="跟进方式" prop="follow_type">
          <el-input v-model="newFollowUp.follow_type" placeholder="请输入跟进方式" />
        </el-form-item>
        <el-form-item label="下次跟进时间" prop="next_follow_date">
          <el-date-picker
            v-model="newFollowUp.next_follow_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveFollowUp">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showEditDialog"
      title="编辑跟进记录"
      width="600px"
      @close="resetEditForm"
    >
      <el-form :model="editFollowUpForm" label-width="120px">
        <el-form-item label="客户ID" prop="customer_id" required>
          <el-input v-model.number="editFollowUpForm.customer_id" placeholder="请输入客户ID" />
        </el-form-item>
        <el-form-item label="跟进内容" prop="content" required>
          <el-input type="textarea" v-model="editFollowUpForm.content" rows="3" placeholder="请输入跟进内容" />
        </el-form-item>
        <el-form-item label="跟进方式" prop="follow_type">
          <el-input v-model="editFollowUpForm.follow_type" placeholder="请输入跟进方式" />
        </el-form-item>
        <el-form-item label="下次跟进时间" prop="next_follow_date">
          <el-date-picker
            v-model="editFollowUpForm.next_follow_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateFollowUp">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const followUps = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const newFollowUp = ref({
  customer_id: '',
  content: '',
  follow_type: '',
  next_follow_date: ''
})
const editFollowUpForm = ref({
  id: null,
  customer_id: '',
  content: '',
  follow_type: '',
  next_follow_date: ''
})

const fetchFollowUps = async () => {
  try {
    const response = await axios.get('/api/follow-ups')
    followUps.value = response.data
  } catch (error) {
    console.error('获取跟进记录失败:', error)
    const errorMessage = error.response?.data?.message || '获取跟进记录列表失败'
    ElMessage.error(errorMessage)
  }
}

const saveFollowUp = async () => {
  try {
    await axios.post('/api/follow-ups', newFollowUp.value)
    ElMessage.success('跟进记录添加成功')
    fetchFollowUps()
    showAddDialog.value = false
    resetForm()
  } catch (error) {
    console.error('保存跟进记录失败:', error)
    const errorMessage = error.response?.data?.message || '保存跟进记录失败'
    ElMessage.error(errorMessage)
  }
}

const deleteFollowUp = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条跟进记录吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`/api/follow-ups/${id}`)
    ElMessage.success('跟进记录删除成功')
    fetchFollowUps()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除跟进记录失败:', error)
      const errorMessage = error.response?.data?.message || '删除跟进记录失败'
      ElMessage.error(errorMessage)
    }
  }
}

const editFollowUp = (followUp) => {
  editFollowUpForm.value = {
    id: followUp.id,
    customer_id: followUp.customer_id,
    content: followUp.content,
    follow_type: followUp.follow_type,
    next_follow_date: followUp.next_follow_date
  }
  showEditDialog.value = true
}

const updateFollowUp = async () => {
  try {
    await axios.put(`/api/follow-ups/${editFollowUpForm.value.id}`, editFollowUpForm.value)
    ElMessage.success('跟进记录更新成功')
    fetchFollowUps()
    showEditDialog.value = false
    resetEditForm()
  } catch (error) {
    console.error('更新跟进记录失败:', error)
    const errorMessage = error.response?.data?.message || '更新跟进记录失败'
    ElMessage.error(errorMessage)
  }
}

const resetForm = () => {
  newFollowUp.value = {
    customer_id: '',
    content: '',
    follow_type: '',
    next_follow_date: ''
  }
}

const resetEditForm = () => {
  editFollowUpForm.value = {
    id: null,
    customer_id: '',
    content: '',
    follow_type: '',
    next_follow_date: ''
  }
}

onMounted(() => {
  fetchFollowUps()
})
</script>

<style scoped>
.follow-ups-container {
  height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>