<template>
  <div class="charts-section">
    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>业务增长趋势</span>
              <el-radio-group v-model="trendType" size="small" @change="initTrendChart">
                <el-radio-button label="customer">客户</el-radio-button>
                <el-radio-button label="amount">金额</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>客户行业分布</span>
            </div>
          </template>
          <div ref="industryChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  trendData: {
    type: Array,
    default: () => []
  },
  industryData: {
    type: Array,
    default: () => []
  }
})

const trendChartRef = ref(null)
const industryChartRef = ref(null)
const trendType = ref('customer')
let trendChart = null
let industryChart = null

const initTrendChart = () => {
  if (!trendChartRef.value || props.trendData.length === 0) return
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)
  
  const isCustomer = trendType.value === 'customer'
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: props.trendData.map(d => d.period) },
    yAxis: { type: 'value' },
    series: [{
      name: isCustomer ? '新增客户' : '成交金额',
      type: 'line',
      smooth: true,
      data: props.trendData.map(d => isCustomer ? d.newCustomers : d.closedAmount),
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: isCustomer ? 'rgba(102, 126, 234, 0.3)' : 'rgba(240, 147, 251, 0.3)' },
          { offset: 1, color: isCustomer ? 'rgba(102, 126, 234, 0)' : 'rgba(240, 147, 251, 0)' }
        ])
      },
      itemStyle: { color: isCustomer ? '#667eea' : '#f093fb' }
    }]
  }
  trendChart.setOption(option)
}

const initIndustryChart = () => {
  if (!industryChartRef.value || props.industryData.length === 0) return
  if (!industryChart) industryChart = echarts.init(industryChartRef.value)
  
  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: '0', left: 'center', icon: 'circle', itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 12 } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: '14', fontWeight: 'bold' } },
      data: props.industryData.map(d => ({ name: d.industry, value: d.count }))
    }]
  }
  industryChart.setOption(option)
}

watch(() => props.trendData, () => {
  initTrendChart()
}, { deep: true })

watch(() => props.industryData, () => {
  initIndustryChart()
}, { deep: true })

const handleResize = () => {
  trendChart?.resize()
  industryChart?.resize()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  // Ensure charts are initialized if data is already present
  if (props.trendData.length > 0) initTrendChart()
  if (props.industryData.length > 0) initIndustryChart()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  industryChart?.dispose()
})
</script>

<style scoped>
.charts-section { margin-bottom: 20px; }
.chart-card { border-radius: 12px; height: 400px; }
.chart-container { height: 300px; width: 100%; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
</style>
