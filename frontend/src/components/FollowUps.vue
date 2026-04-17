<template>
  <div class="follow-ups-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Message /></el-icon>
        <h2>跟进记录</h2>
        <el-tag type="info" class="count-tag">共 {{ followUps.length }} 条记录</el-tag>
      </div>
      <div class="header-right">
        <el-button type="success" @click="showExportDialog = true" :icon="Download">
          导出数据
        </el-button>
        <el-button type="primary" @click="openAddDialog" :icon="Plus">
          添加记录
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <FollowUpFilter
      v-model:searchQuery="searchQuery"
      v-model:filterType="filterType"
      v-model:timeRange="timeRange"
      v-model:dateRange="dateRange"
      @search="fetchFollowUps"
      @reset="fetchFollowUps"
    />

    <!-- 跟进记录表格 -->
    <FollowUpTable
      :paginatedFollowUps="paginatedFollowUps"
      :loading="loading"
      v-model:currentPage="currentPage"
      v-model:pageSize="pageSize"
      :filteredTotal="filteredTotal"
      @edit="openEditDialog"
      @delete="deleteFollowUp"
    />

    <!-- 表单对话框 -->
    <FollowUpDialogs
      ref="dialogsRef"
      @refresh="fetchFollowUps"
    />

    <!-- 导出对话框 -->
    <ExportDialog
      v-model="showExportDialog"
      title="导出跟进记录"
      data-type="follow-ups"
      :fields="followUpExportFields"
      :default-fields="defaultExportFields"
      :filters="currentFilters"
      :total-count="followUps.length"
      :filtered-count="filteredTotal"
      @export-success="() => ElMessage.success('跟进记录导出成功')"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Message, Plus, Download } from '@element-plus/icons-vue'
import ExportDialog from './ExportDialog.vue'

import FollowUpFilter from './follow-ups/FollowUpFilter.vue'
import FollowUpTable from './follow-ups/FollowUpTable.vue'
import FollowUpDialogs from './follow-ups/FollowUpDialogs.vue'
import { useFollowUps } from '../composables/useFollowUps'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ role: 'user' })
  }
})

const {
  followUps,
  loading,
  searchQuery,
  filterType,
  timeRange,
  dateRange,
  currentPage,
  pageSize,
  fetchFollowUps,
  paginatedFollowUps,
  filteredTotal,
  currentFilters
} = useFollowUps()

const dialogsRef = ref(null)
const showExportDialog = ref(false)

const openAddDialog = () => {
  dialogsRef.value?.openAdd()
}

const openEditDialog = (row) => {
  dialogsRef.value?.openEdit(row)
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
      ElMessage.error(error.response?.data?.message || '删除跟进记录失败')
    }
  }
}

// 导出字段配置保留在主组件中或根据需要抽出
const followUpExportFields = [
  { key: 'id', label: '记录ID', description: '系统唯一标识' },
  { key: 'customer_id', label: '客户ID', description: '关联客户ID' },
  { key: 'customer_name', label: '客户姓名', description: '客户名称' },
  { key: 'deal_id', label: '交易ID', description: '关联交易ID' },
  { key: 'content', label: '跟进内容', description: '跟进详细内容' },
  { key: 'follow_type', label: '跟进方式', description: '电话/邮件/面谈等' },
  { key: 'next_follow_date', label: '下次跟进日期', description: '计划下次跟进时间' },
  { key: 'is_conversion', label: '是否促成交易', description: '是否成功转化' },
  { key: 'created_by', label: '创建人ID', description: '记录创建人ID' },
  { key: 'creator_name', label: '创建人姓名', description: '记录创建人姓名' },
  { key: 'created_at', label: '创建时间', description: '记录创建时间' }
]

const defaultExportFields = ['id', 'customer_name', 'content', 'follow_type', 'next_follow_date', 'is_conversion', 'created_at']

onMounted(() => {
  fetchFollowUps()
  // 默认选择本月由 useFollowUps 中初始化的 data 设置了 timeRange="month"，此时由 Filter组件自己触发可能更好或就在初始化时设置
  // 这里已在 Filter 初始化时如果有设置会处理，不过稳妥起见不重写组件的话就是这样
})
</script>

<style scoped>
.follow-ups-container {
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
  color: #909399;
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
