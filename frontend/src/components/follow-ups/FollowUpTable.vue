<template>
  <el-card shadow="hover" class="table-card">
    <el-table
      :data="paginatedFollowUps"
      border
      stripe
      style="width: 100%"
      v-loading="loading"
      :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
    >
      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="customer_name" label="客户姓名" min-width="120">
        <template #default="scope">
          <div class="customer-name">
            <el-avatar :size="28" :style="{ backgroundColor: getAvatarColor(scope.row.customer_name) }">
              {{ scope.row.customer_name ? scope.row.customer_name.charAt(0) : '?' }}
            </el-avatar>
            <span>{{ scope.row.customer_name || '未知客户' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="content" label="跟进内容" min-width="200" show-overflow-tooltip />
      <el-table-column prop="follow_type" label="跟进方式" width="100" align="center">
        <template #default="scope">
          <el-tag :type="getFollowTypeType(scope.row.follow_type)" effect="light" size="small">
            {{ scope.row.follow_type || '其他' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_conversion" label="促成交易" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.is_conversion ? 'success' : 'info'" effect="light" size="small">
            {{ scope.row.is_conversion ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="next_follow_date" label="下次跟进时间" width="140">
        <template #default="scope">
          <span v-if="scope.row.next_follow_date" class="next-date">
            <el-icon><Calendar /></el-icon>
            {{ formatDateOnly(scope.row.next_follow_date) }}
          </span>
          <span v-else class="no-date">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="记录时间" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button type="primary" link :icon="Edit" @click="emit('edit', scope.row)">
            编辑
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
import { Edit, Delete, Calendar } from '@element-plus/icons-vue'
import { getAvatarColor, formatDate, formatDateOnly } from '../../utils/helpers'

const props = defineProps({
  paginatedFollowUps: Array,
  loading: Boolean,
  currentPage: Number,
  pageSize: Number,
  filteredTotal: Number
})

const emit = defineEmits(['edit', 'delete', 'update:currentPage', 'update:pageSize'])

const getFollowTypeType = (type) => {
  const typeMap = {
    '电话': 'primary',
    '邮件': 'success',
    '面谈': 'warning',
    '微信': 'info'
  }
  return typeMap[type] || 'info'
}
</script>

<style scoped>
.table-card {
  margin-bottom: 20px;
}
.customer-name {
  display: flex;
  align-items: center;
  gap: 8px;
}
.next-date {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #67C23A;
}
.no-date {
  color: #909399;
}
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
