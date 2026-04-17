<template>
  <div class="stats-container" v-loading="loading">
    <!-- 页面头部：负责全局筛选控制 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><DataAnalysis /></el-icon>
        <h2>统计分析</h2>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button 
            v-for="opt in timeOptions" 
            :key="opt.value"
            :type="timeRange === opt.value ? 'primary' : 'default'" 
            @click="handleTimeChange(opt.value)"
          >
            {{ opt.label }}
          </el-button>
        </el-button-group>
        
        <el-date-picker
          v-if="timeRange === 'custom'"
          v-model="dateRange"
          type="daterange"
          value-format="YYYY-MM-DD"
          @change="fetchData"
          style="margin-left: 12px; width: 240px"
        />
        
        <el-button @click="fetchData" :icon="Refresh" circle style="margin-left: 12px" />
      </div>
    </div>

    <!-- 1. 核心指标卡片 -->
    <KpiCards :data="kpiData" />

    <!-- 2. 增长趋势图 -->
    <TrendCharts :data="trendData" />

    <!-- 3. 构成分布图 -->
    <DistributionCharts 
      :industryData="industryData" 
      :statusData="statusData" 
    />

    <!-- 4. 数据明细表格 (月度汇总) -->
    <el-card class="detail-card" shadow="hover">
      <template #header><span>数据月度汇总</span></template>
      <el-table :data="monthlySummary" border stripe>
        <el-table-column prop="month" label="月份" align="center" />
        <el-table-column prop="newCustomers" label="新增客户" align="center" />
        <el-table-column prop="newDeals" label="新增交易" align="center" />
        <el-table-column prop="closedAmount" label="成交金额" align="center">
          <template #default="scope">¥{{ scope.row.closedAmount.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="conversionRate" label="成交转化率" align="center">
          <template #default="scope">{{ scope.row.conversionRate }}%</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { DataAnalysis, Refresh } from '@element-plus/icons-vue'
import KpiCards from './stats/KpiCards.vue'
import TrendCharts from './stats/TrendCharts.vue'
import DistributionCharts from './stats/DistributionCharts.vue'

const loading = ref(false)
const timeRange = ref('month')
const dateRange = ref([])
const kpiData = ref({})
const trendData = ref([])
const industryData = ref([])
const statusData = ref([])
const monthlySummary = ref([])

const timeOptions = [
  { label: '全部', value: 'all' },
  { label: '本月', value: 'month' },
  { label: '本季', value: 'quarter' },
  { label: '本年', value: 'year' },
  { label: '自定义', value: 'custom' }
]

const handleTimeChange = (val) => {
  timeRange.value = val
  if (val !== 'custom') fetchData()
}

const fetchData = async () => {
  loading.value = true
  try {
    let params = { range: timeRange.value }
    if (timeRange.value === 'custom' && dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const [kpiRes, trendRes, statusRes, industryRes, summaryRes] = await Promise.all([
      axios.get('/api/stats/kpi', { params }),
      axios.get('/api/stats/trend', { params }),
      axios.get('/api/stats/status'),
      axios.get('/api/stats/industry'),
      axios.get('/api/stats/monthly-summary')
    ])

    kpiData.value = kpiRes.data
    trendData.value = trendRes.data
    
    // 转换客户状态数据为数组格式供图表使用
    const statusObj = statusRes.data.customers || {}
    const statusMap = { 'potential': '潜在客户', 'active': '活跃客户', 'lost': '已流失客户' }
    statusData.value = Object.keys(statusObj).map(key => ({
      status: statusMap[key] || key,
      count: statusObj[key]
    }))
    
    // 转换行业数据为数组格式供图表使用
    const industryObj = industryRes.data || {}
    industryData.value = Object.keys(industryObj).map(key => ({
      industry: key,
      count: industryObj[key]
    }))
    
    monthlySummary.value = summaryRes.data
  } catch (error) {
    console.error('Fetch stats failed:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchData())
</script>

<style scoped>
.stats-container { padding: 20px; background: #f5f7fa; min-height: 100vh; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-icon { font-size: 28px; color: #409eff; }
.detail-card { border-radius: 12px; }
</style>
