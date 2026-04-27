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
              placeholder="搜索客户姓名、跟进内容"
              clearable
              :prefix-icon="Search"
              @input="handleSearch"
              class="search-input"
            />
            <el-select
              v-model="filterType"
              placeholder="筛选跟进方式"
              clearable
              @change="handleSearch"
              class="filter-select"
            >
              <el-option label="电话" value="电话" />
              <el-option label="邮件" value="邮件" />
              <el-option label="面谈" value="面谈" />
              <el-option label="微信" value="微信" />
              <el-option label="其他" value="其他" />
            </el-select>
            <el-button @click="resetFilters" :icon="RefreshRight">重置</el-button>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Calendar, Grid, Setting, Search, RefreshRight } from '@element-plus/icons-vue'
import { formatLocalDateInput } from '../../utils/helpers'

const props = defineProps({
  searchQuery: String,
  filterType: String,
  timeRange: String,
  dateRange: Array
})

const emit = defineEmits([
  'update:searchQuery', 
  'update:filterType', 
  'update:timeRange',
  'update:dateRange',
  'search',
  'reset'
])

const searchQuery = computed({
  get: () => props.searchQuery,
  set: (val) => emit('update:searchQuery', val)
})

const filterType = computed({
  get: () => props.filterType,
  set: (val) => emit('update:filterType', val)
})

const timeRange = computed({
  get: () => props.timeRange,
  set: (val) => emit('update:timeRange', val)
})

const dateRange = computed({
  get: () => props.dateRange,
  set: (val) => emit('update:dateRange', val)
})

const handleSearch = () => {
  emit('search')
}

const resetFilters = () => {
  searchQuery.value = ''
  filterType.value = ''
  setTimeRange('month')
  emit('reset')
}

const handleDateRangeChange = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    emit('search')
  }
}

const setTimeRange = (range) => {
  timeRange.value = range
  if (range === 'all') {
    dateRange.value = []
    emit('search')
  } else if (range !== 'custom') {
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth()
    
    if (range === 'month') {
      const start = new Date(year, month, 1)
      const end = new Date(year, month + 1, 0)
      dateRange.value = [
        formatLocalDateInput(start),
        formatLocalDateInput(end)
      ]
    } else if (range === 'year') {
      const start = new Date(year, 0, 1)
      const end = new Date(year, 11, 31)
      dateRange.value = [
        formatLocalDateInput(start),
        formatLocalDateInput(end)
      ]
    }
    emit('search')
  }
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
