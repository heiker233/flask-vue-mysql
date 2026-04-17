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
              v-model="localDateRange"
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
          
          <!-- 基础筛选条件 -->
          <div class="other-filters">
            <el-input
              v-model="localSearchQuery"
              placeholder="搜索客户姓名、电话、公司"
              clearable
              :prefix-icon="Search"
              @input="handleSearch"
              class="search-input"
            />
            <el-select
              v-model="localFilterStatus"
              placeholder="筛选状态"
              clearable
              @change="handleSearch"
              class="filter-select"
            >
              <el-option label="潜在客户" value="potential" />
              <el-option label="活跃客户" value="active" />
              <el-option label="已流失客户" value="lost" />
            </el-select>
            <el-select
              v-model="localFilterIndustry"
              placeholder="筛选行业"
              clearable
              @change="handleSearch"
              class="filter-select"
            >
              <el-option
                v-for="industry in industryOptions"
                :key="industry"
                :label="industry"
                :value="industry"
              />
            </el-select>
            <el-button type="primary" @click="localShowAdvancedSearch = !localShowAdvancedSearch" :icon="localShowAdvancedSearch ? ArrowUp : ArrowDown">
              {{ localShowAdvancedSearch ? '收起' : '高级搜索' }}
            </el-button>
            <el-button @click="resetFilters" :icon="RefreshRight">重置</el-button>
          </div>
          
          <!-- 高级搜索区域 -->
          <div v-if="localShowAdvancedSearch" class="advanced-search">
            <el-divider content-position="left">高级筛选</el-divider>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="合作阶段">
                  <el-select v-model="localAdvancedFilters.cooperation_stage" placeholder="选择合作阶段" clearable @change="handleSearch" style="width: 100%">
                    <el-option label="初步接触" value="initial" />
                    <el-option label="需求沟通" value="communication" />
                    <el-option label="方案制定" value="proposal" />
                    <el-option label="商务谈判" value="negotiation" />
                    <el-option label="已签约" value="signed" />
                    <el-option label="合作中" value="cooperating" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="负责人">
                  <el-select v-model="localAdvancedFilters.assigned_to" placeholder="选择负责人" clearable @change="handleSearch" style="width: 100%">
                    <el-option
                      v-for="user in userList"
                      :key="user.id"
                      :label="user.username"
                      :value="user.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="评分范围">
                  <div class="score-range">
                    <el-rate v-model="localAdvancedFilters.value_score_min" :max="5" />
                    <span class="range-separator">至</span>
                    <el-rate v-model="localAdvancedFilters.value_score_max" :max="5" />
                  </div>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="电话前缀">
                  <el-input v-model="localAdvancedFilters.phone_prefix" placeholder="如: 138" clearable @input="handleSearch" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="排序字段">
                  <el-select v-model="localSortBy" placeholder="选择排序字段" @change="handleSearch" style="width: 100%">
                    <el-option label="创建时间" value="created_at" />
                    <el-option label="价值评分" value="value_score" />
                    <el-option label="客户姓名" value="name" />
                    <el-option label="公司名称" value="company" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="排序方式">
                  <el-radio-group v-model="localSortOrder" @change="handleSearch">
                    <el-radio-button label="desc">降序</el-radio-button>
                    <el-radio-button label="asc">升序</el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Search, RefreshRight, Calendar, Setting, Grid, ArrowUp, ArrowDown } from '@element-plus/icons-vue'

const props = defineProps({
  searchQuery: String,
  filterStatus: String,
  filterIndustry: String,
  timeRange: String,
  dateRange: Array,
  showAdvancedSearch: Boolean,
  advancedFilters: Object,
  sortBy: String,
  sortOrder: String,
  industryOptions: Array,
  userList: Array
})

const emit = defineEmits([
  'update:searchQuery',
  'update:filterStatus',
  'update:filterIndustry',
  'update:timeRange',
  'update:dateRange',
  'update:showAdvancedSearch',
  'update:advancedFilters',
  'update:sortBy',
  'update:sortOrder',
  'search',
  'reset',
  'timeRangeChange',
  'dateRangeChange'
])

const localSearchQuery = computed({ get: () => props.searchQuery, set: (val) => emit('update:searchQuery', val) })
const localFilterStatus = computed({ get: () => props.filterStatus, set: (val) => emit('update:filterStatus', val) })
const localFilterIndustry = computed({ get: () => props.filterIndustry, set: (val) => emit('update:filterIndustry', val) })
const localDateRange = computed({ get: () => props.dateRange, set: (val) => emit('update:dateRange', val) })
const localShowAdvancedSearch = computed({ get: () => props.showAdvancedSearch, set: (val) => emit('update:showAdvancedSearch', val) })
const localAdvancedFilters = computed({ get: () => props.advancedFilters, set: (val) => emit('update:advancedFilters', val) })
const localSortBy = computed({ get: () => props.sortBy, set: (val) => emit('update:sortBy', val) })
const localSortOrder = computed({ get: () => props.sortOrder, set: (val) => emit('update:sortOrder', val) })

const setTimeRange = (range) => {
  emit('timeRangeChange', range)
}

const handleDateRangeChange = () => {
  emit('dateRangeChange')
}

const handleSearch = () => {
  emit('search')
}

const resetFilters = () => {
  emit('reset')
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
.advanced-search {
  margin-top: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
.advanced-search .el-divider {
  margin: 0 0 16px 0;
}
.score-range {
  display: flex;
  align-items: center;
  gap: 8px;
}
.range-separator {
  color: #909399;
  font-size: 14px;
}
.search-input {
  width: 240px;
}
.filter-select {
  width: 140px;
}
</style>