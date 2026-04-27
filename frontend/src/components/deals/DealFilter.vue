<template>
  <el-card class="search-card" shadow="never">
    <el-row :gutter="20" align="middle">
      <el-col :xs="24" :sm="24" :md="24" :lg="24">
        <div class="filter-container">
          <!-- 时间查询按钮组 -->
          <div class="time-filter-section">
            <el-button-group class="time-filter-buttons">
              <el-button 
                :type="timeRange === 'all' ? 'primary' : 'default'" 
                @click="onSetTimeRange('all')"
              >
                <el-icon><Grid /></el-icon>
                全部
              </el-button>
              <el-button 
                :type="timeRange === 'month' ? 'primary' : 'default'" 
                @click="onSetTimeRange('month')"
              >
                <el-icon><Calendar /></el-icon>
                本月
              </el-button>
              <el-button 
                :type="timeRange === 'year' ? 'primary' : 'default'" 
                @click="onSetTimeRange('year')"
              >
                <el-icon><Calendar /></el-icon>
                本年
              </el-button>
              <el-button 
                :type="timeRange === 'custom' ? 'primary' : 'default'" 
                @click="onSetTimeRange('custom')"
              >
                <el-icon><Setting /></el-icon>
                自定义
              </el-button>
            </el-button-group>
            
            <!-- 自定义日期选择器 -->
            <el-date-picker
              v-if="timeRange === 'custom'"
              :model-value="dateRange"
              @update:model-value="val => emit('update:dateRange', val)"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              @change="onSearch"
              class="date-range-picker"
              :unlink-panels="true"
            />
          </div>
          
          <!-- 其他筛选条件 -->
          <div class="other-filters">
            <el-input
              :model-value="searchQuery"
              @update:model-value="val => emit('update:searchQuery', val)"
              placeholder="搜索客户姓名、产品"
              clearable
              :prefix-icon="Search"
              @input="onSearch"
              class="search-input"
            />
            <el-select
              :model-value="filterStatus"
              @update:model-value="val => emit('update:filterStatus', val)"
              placeholder="筛选状态"
              clearable
              @change="onSearch"
              class="filter-select"
            >
              <el-option label="谈判中" value="negotiating" />
              <el-option label="已完成" value="closed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-button @click="onReset" :icon="RefreshRight">重置</el-button>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { Search, RefreshRight, Calendar, Setting, Grid } from '@element-plus/icons-vue'
import { formatLocalDateInput } from '../../utils/helpers'

const props = defineProps({
  searchQuery: String,
  filterStatus: String,
  timeRange: String,
  dateRange: Array
})

const emit = defineEmits([
  'update:searchQuery',
  'update:filterStatus',
  'update:timeRange',
  'update:dateRange',
  'search'
])

const onSearch = () => {
  emit('search')
}

const onSetTimeRange = (range) => {
  emit('update:timeRange', range)
  
  if (range === 'all') {
    emit('update:dateRange', [])
    onSearch()
  } else if (range !== 'custom') {
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth()
    
    if (range === 'month') {
      const start = new Date(year, month, 1)
      emit('update:dateRange', [
        formatLocalDateInput(start),
        formatLocalDateInput(now)
      ])
    } else if (range === 'year') {
      const start = new Date(year, 0, 1)
      emit('update:dateRange', [
        formatLocalDateInput(start),
        formatLocalDateInput(now)
      ])
    }
    onSearch()
  }
}

const onReset = () => {
  emit('update:searchQuery', '')
  emit('update:filterStatus', '')
  onSetTimeRange('month')
}
</script>

<style scoped>
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
</style>
