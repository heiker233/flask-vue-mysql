<template>
  <div class="stats-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><DataAnalysis /></el-icon>
        <div class="header-title-section">
          <h2>统计分析</h2>
          <div class="time-display">
            <el-tag type="info" size="small">
              <el-icon><Calendar /></el-icon>
              {{ currentTimeDisplay }}
            </el-tag>
          </div>
        </div>
      </div>
      <div class="header-right">
        <!-- 快捷查询按钮组 -->
        <div class="quick-query-wrapper">
          <div class="quick-query-buttons-row">
            <el-button-group class="quick-query-buttons">
              <el-button 
                :type="timeRange === 'all' ? 'primary' : 'default'" 
                @click="setQuickQuery('all')"
                size="default"
              >
                <el-icon><Grid /></el-icon>
                全部
              </el-button>
              <el-button 
                :type="timeRange === 'month' ? 'primary' : 'default'" 
                @click="setQuickQuery('month')"
                size="default"
              >
                <el-icon><Calendar /></el-icon>
                本月
              </el-button>
              <el-button 
                :type="timeRange === 'year' ? 'primary' : 'default'" 
                @click="setQuickQuery('year')"
                size="default"
              >
                <el-icon><Calendar /></el-icon>
                本年
              </el-button>
              <el-button 
                :type="timeRange === 'custom' ? 'primary' : 'default'" 
                @click="setQuickQuery('custom')"
                size="default"
              >
                <el-icon><Setting /></el-icon>
                自定义
              </el-button>
            </el-button-group>
            
            <el-button type="primary" @click="refreshAllData" :loading="loading" class="refresh-btn">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
          
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
            :shortcuts="dateShortcuts"
            :editable="false"
            :unlink-panels="true"
          />
        </div>
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <div class="kpi-section">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="kpi-card" shadow="hover">
            <div class="kpi-content">
              <div class="kpi-icon customer-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="kpi-info">
                <div class="kpi-value">{{ formatInteger(kpiData.customers) }}</div>
                <div class="kpi-label">新增客户</div>
                <div class="kpi-trend" :class="kpiData.customerTrend >= 0 ? 'up' : 'down'">
                  <el-icon><ArrowUp v-if="kpiData.customerTrend >= 0" /><ArrowDown v-else /></el-icon>
                  <span>{{ Math.abs(kpiData.customerTrend) }}%</span>
                  <span class="trend-text">环比</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="kpi-card" shadow="hover">
            <div class="kpi-content">
              <div class="kpi-icon deal-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="kpi-info">
                <div class="kpi-value">{{ formatInteger(kpiData.deals) }}</div>
                <div class="kpi-label">新增交易</div>
                <div class="kpi-trend" :class="kpiData.dealTrend >= 0 ? 'up' : 'down'">
                  <el-icon><ArrowUp v-if="kpiData.dealTrend >= 0" /><ArrowDown v-else /></el-icon>
                  <span>{{ Math.abs(kpiData.dealTrend) }}%</span>
                  <span class="trend-text">环比</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="kpi-card" shadow="hover">
            <div class="kpi-content">
              <div class="kpi-icon amount-icon">
                <el-icon><Money /></el-icon>
              </div>
              <div class="kpi-info">
                <div class="kpi-value">¥{{ formatAmount(kpiData.amount) }}</div>
                <div class="kpi-label">成交金额</div>
                <div class="kpi-trend" :class="kpiData.amountTrend >= 0 ? 'up' : 'down'">
                  <el-icon><ArrowUp v-if="kpiData.amountTrend >= 0" /><ArrowDown v-else /></el-icon>
                  <span>{{ Math.abs(kpiData.amountTrend) }}%</span>
                  <span class="trend-text">环比</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="kpi-card" shadow="hover">
            <div class="kpi-content">
              <div class="kpi-icon conversion-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="kpi-info">
                <div class="kpi-value">{{ kpiData.conversionRate }}%</div>
                <div class="kpi-label">成交转化率</div>
                <div class="kpi-trend" :class="kpiData.conversionTrend >= 0 ? 'up' : 'down'">
                  <el-icon><ArrowUp v-if="kpiData.conversionTrend >= 0" /><ArrowDown v-else /></el-icon>
                  <span>{{ Math.abs(kpiData.conversionTrend) }}%</span>
                  <span class="trend-text">环比</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <el-row :gutter="20">
        <!-- 客户增长趋势 -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><User /></el-icon>
                <span>客户增长趋势</span>
                <el-tooltip content="显示选定时间范围内的客户增长情况">
                  <el-icon><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
            </template>
            <div class="chart-container" v-loading="loading">
              <div ref="customerChart" class="chart"></div>
            </div>
          </el-card>
        </el-col>

        <!-- 交易金额趋势 -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Money /></el-icon>
                <span>交易金额趋势</span>
                <el-tooltip content="显示选定时间范围内的交易金额变化">
                  <el-icon><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
            </template>
            <div class="chart-container" v-loading="loading">
              <div ref="amountChart" class="chart"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="chart-row">
        <!-- 客户状态分布 -->
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><PieChart /></el-icon>
                <span>客户状态分布</span>
              </div>
            </template>
            <div class="chart-container" v-loading="loading">
              <div ref="customerStatusChart" class="chart"></div>
            </div>
          </el-card>
        </el-col>

        <!-- 交易状态分布 -->
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><PieChart /></el-icon>
                <span>交易状态分布</span>
              </div>
            </template>
            <div class="chart-container" v-loading="loading">
              <div ref="dealStatusChart" class="chart"></div>
            </div>
          </el-card>
        </el-col>

        <!-- 行业分布 -->
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><OfficeBuilding /></el-icon>
                <span>客户行业分布</span>
              </div>
            </template>
            <div class="chart-container" v-loading="loading">
              <div ref="industryChart" class="chart"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 详细数据表格（月统计） -->
    <div class="tables-section">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><List /></el-icon>
            <span>月度数据报表</span>
            <el-button type="primary" size="small" @click="exportData">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
          </div>
        </template>
        <el-table :data="detailData" border stripe style="width: 100%" v-loading="loading">
          <el-table-column prop="month" label="月份" width="120" align="center">
            <template #default="scope">
              <el-tag type="primary" size="small">{{ scope.row.month }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="newCustomers" label="新增客户" align="center" sortable>
            <template #default="scope">
              <span class="number-highlight">{{ formatInteger(scope.row.newCustomers) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="newDeals" label="新增交易" align="center" sortable>
            <template #default="scope">
              <span class="number-highlight">{{ formatInteger(scope.row.newDeals) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="closedAmount" label="成交金额" align="right" sortable>
            <template #default="scope">
              <span class="amount-text">¥{{ formatNumber(scope.row.closedAmount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="followUps" label="跟进次数" align="center" sortable>
            <template #default="scope">
              <span class="number-highlight">{{ formatInteger(scope.row.followUps) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="conversionRate" label="转化率" align="center" sortable width="150">
            <template #default="scope">
              <el-progress 
                :percentage="scope.row.conversionRate" 
                :color="getProgressColor(scope.row.conversionRate)"
                :stroke-width="8"
              />
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { 
  DataAnalysis, User, Money, Document, TrendCharts, 
  ArrowUp, ArrowDown, Refresh, InfoFilled, PieChart, 
  OfficeBuilding, List, Download, Calendar, Grid
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const timeRange = ref('month')
const dateRange = ref([])

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    }
  },
  {
    text: '最近半年',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 180)
      return [start, end]
    }
  },
  {
    text: '最近一年',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 365)
      return [start, end]
    }
  }
]

// KPI数据
const kpiData = ref({
  customers: 0,
  deals: 0,
  amount: 0,
  conversionRate: 0,
  customerTrend: 0,
  dealTrend: 0,
  amountTrend: 0,
  conversionTrend: 0
})

// 详细数据（月统计）
const detailData = ref([])

// 图表数据（根据时间范围）
const trendData = ref([])

// 当前时间显示
const currentTimeDisplay = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  
  if (timeRange.value === 'custom' && dateRange.value && dateRange.value.length === 2) {
    return `${dateRange.value[0]} 至 ${dateRange.value[1]}`
  } else if (timeRange.value === 'month') {
    // 本月第一天
    return `${year}-${month}-01`
  } else if (timeRange.value === 'quarter') {
    // 本季度第一个月
    const currentMonth = now.getMonth() + 1
    const quarterStartMonth = Math.floor((currentMonth - 1) / 3) * 3 + 1
    return `${year}-${String(quarterStartMonth).padStart(2, '0')}`
  } else if (timeRange.value === 'year') {
    // 本年第一个月
    return `${year}-01`
  }
  return ''
})

// 图表实例
const customerChart = ref(null)
const amountChart = ref(null)
const customerStatusChart = ref(null)
const dealStatusChart = ref(null)
const industryChart = ref(null)

let charts = {}

// 格式化金额
const formatAmount = (amount) => {
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toLocaleString()
}

// 格式化数字（金额用，保留2位小数）
const formatNumber = (num) => {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 格式化整数（客户数、交易数等用）
const formatInteger = (num) => {
  return Math.round(num).toLocaleString('zh-CN')
}

// 获取进度条颜色
const getProgressColor = (percentage) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#e6a23c'
  if (percentage >= 40) return '#409eff'
  return '#f56c6c'
}

// 初始化客户增长趋势图
const initCustomerChart = (data) => {
  if (!customerChart.value) return
  
  const chart = echarts.init(customerChart.value)
  charts.customer = chart
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(param => {
          result += param.marker + ' ' + param.seriesName + ': ' + Math.round(param.value) + '<br/>'
        })
        return result
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.period),
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: '客户数',
      minInterval: 1,
      axisLabel: {
        formatter: function(value) {
          return Math.round(value)
        }
      }
    },
    series: [{
      name: '新增客户',
      type: 'bar',
      data: data.map(item => item.newCustomers),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#188df0' }
        ])
      },
      emphasis: {
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#2378f7' },
            { offset: 0.7, color: '#2378f7' },
            { offset: 1, color: '#83bff6' }
          ])
        }
      }
    }]
  }
  
  chart.setOption(option)
}

// 初始化交易金额趋势图
const initAmountChart = (data) => {
  if (!amountChart.value) return
  
  const chart = echarts.init(amountChart.value)
  charts.amount = chart
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        return params[0].name + '<br/>' +
               params[0].marker + ' 成交金额: ¥' + formatNumber(params[0].value)
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.period),
      boundaryGap: false,
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: '金额(万元)',
      axisLabel: {
        formatter: function(value) {
          return (value / 10000).toFixed(0)
        }
      }
    },
    series: [{
      name: '成交金额',
      type: 'line',
      data: data.map(item => item.closedAmount),
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        color: '#f5576c',
        width: 3
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(245, 87, 108, 0.3)' },
          { offset: 1, color: 'rgba(245, 87, 108, 0.05)' }
        ])
      },
      itemStyle: {
        color: '#f5576c'
      }
    }]
  }
  
  chart.setOption(option)
}

// 初始化客户状态分布饼图
const initCustomerStatusChart = (data) => {
  if (!customerStatusChart.value) return
  
  const chart = echarts.init(customerStatusChart.value)
  charts.customerStatus = chart
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      name: '客户状态',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: data.potential, name: '潜在客户', itemStyle: { color: '#409eff' } },
        { value: data.active, name: '活跃客户', itemStyle: { color: '#67c23a' } },
        { value: data.lost, name: '流失客户', itemStyle: { color: '#f56c6c' } }
      ]
    }]
  }
  
  chart.setOption(option)
}

// 初始化交易状态分布饼图
const initDealStatusChart = (data) => {
  if (!dealStatusChart.value) return
  
  const chart = echarts.init(dealStatusChart.value)
  charts.dealStatus = chart
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      name: '交易状态',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: data.negotiating, name: '洽谈中', itemStyle: { color: '#e6a23c' } },
        { value: data.closed, name: '已完成', itemStyle: { color: '#67c23a' } },
        { value: data.failed, name: '已失败', itemStyle: { color: '#909399' } }
      ]
    }]
  }
  
  chart.setOption(option)
}

// 初始化行业分布图
const initIndustryChart = (data) => {
  if (!industryChart.value) return
  
  const chart = echarts.init(industryChart.value)
  charts.industry = chart
  
  const industries = Object.keys(data)
  const values = Object.values(data)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: industries
    },
    series: [{
      name: '客户数',
      type: 'bar',
      data: values,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#188df0' }
        ])
      }
    }]
  }
  
  chart.setOption(option)
}

// 获取统计数据
const fetchStatsData = async () => {
  loading.value = true
  try {
    let params = `range=${timeRange.value}`
    
    // 如果是自定义时间范围，添加日期参数
    if (timeRange.value === 'custom' && dateRange.value && dateRange.value.length === 2) {
      params += `&start_date=${dateRange.value[0]}&end_date=${dateRange.value[1]}`
    }
    
    const [kpiRes, trendRes, monthlyRes, statusRes, industryRes] = await Promise.all([
      axios.get(`/api/stats/kpi?${params}`),
      axios.get(`/api/stats/trend?${params}`),
      axios.get('/api/stats/monthly-summary'),
      axios.get('/api/stats/status'),
      axios.get('/api/stats/industry')
    ])
    
    // 更新KPI数据
    kpiData.value = kpiRes.data
    
    // 更新图表数据
    trendData.value = trendRes.data
    
    // 更新详细数据（月统计）
    detailData.value = monthlyRes.data
    
    // 初始化图表
    await nextTick()
    initCustomerChart(trendRes.data)
    initAmountChart(trendRes.data)
    initCustomerStatusChart(statusRes.data.customers)
    initDealStatusChart(statusRes.data.deals)
    initIndustryChart(industryRes.data)
    
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 处理日期范围变化
const handleDateRangeChange = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    fetchStatsData()
  }
}

// 设置快捷查询
const setQuickQuery = (range) => {
  timeRange.value = range
  if (range === 'all') {
    dateRange.value = []
    fetchStatsData()
  } else if (range !== 'custom') {
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth()
    
    if (range === 'month') {
      const start = new Date(year, month, 1)
      dateRange.value = [
        start.toISOString().split('T')[0],
        now.toISOString().split('T')[0]
      ]
    } else if (range === 'year') {
      const start = new Date(year, 0, 1)
      dateRange.value = [
        start.toISOString().split('T')[0],
        now.toISOString().split('T')[0]
      ]
    }
    fetchStatsData()
  }
}

// 刷新所有数据
const refreshAllData = () => {
  fetchStatsData()
  ElMessage.success('数据刷新成功')
}

// 导出数据
const exportData = () => {
  // 创建CSV内容
  const headers = ['月份', '新增客户', '新增交易', '成交金额', '跟进次数', '转化率']
  const rows = detailData.value.map(item => [
    item.month,
    item.newCustomers,
    item.newDeals,
    item.closedAmount,
    item.followUps,
    item.conversionRate + '%'
  ])
  
  const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
  
  // 下载CSV文件
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `月度统计数据_${new Date().toLocaleDateString()}.csv`
  link.click()
  
  ElMessage.success('数据导出成功')
}

// 窗口大小改变时重新渲染图表
const handleResize = () => {
  Object.values(charts).forEach(chart => {
    if (chart) chart.resize()
  })
}

onMounted(() => {
  // 默认选择本月
  setQuickQuery('month')
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  Object.values(charts).forEach(chart => {
    if (chart) chart.dispose()
  })
})
</script>

<style scoped>
.stats-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 28px;
  color: #409eff;
}

.header-title-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-title-section h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.time-display {
  display: flex;
  align-items: center;
}

.time-display .el-icon {
  margin-right: 4px;
}

.header-right {
  display: flex;
  align-items: flex-start;
}

.quick-query-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-end;
}

.quick-query-buttons-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quick-query-buttons {
  display: flex;
}

.quick-query-buttons .el-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

.refresh-btn {
  margin-left: 0;
}

/* KPI卡片 */
.kpi-section {
  margin-bottom: 20px;
}

.kpi-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.kpi-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.kpi-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 28px;
}

.customer-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.deal-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.amount-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.conversion-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.kpi-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.kpi-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.kpi-trend.up {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.kpi-trend.down {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.trend-text {
  font-size: 12px;
  font-weight: normal;
  margin-left: 4px;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 20px;
}

.chart-row {
  margin-top: 20px;
}

.chart-card {
  border-radius: 12px;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.card-header span {
  flex: 1;
}

.chart-container {
  height: 300px;
  padding: 10px;
}

.chart {
  width: 100%;
  height: 100%;
}

/* 表格区域 */
.tables-section {
  margin-bottom: 20px;
}

.amount-text {
  color: #67c23a;
  font-weight: 600;
}

.number-highlight {
  font-weight: 600;
  color: #409eff;
}

/* 日期选择器样式 */
.date-range-picker {
  margin-left: 10px;
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .header-right {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .kpi-card {
    margin-bottom: 12px;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>
