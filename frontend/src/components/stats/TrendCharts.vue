<template>
  <el-card class="chart-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <el-icon><TrendChartsIcon /></el-icon>
          <span>业务增长趋势</span>
        </div>
        <el-radio-group v-model="activeTab" size="small">
          <el-radio-button label="customer">客户</el-radio-button>
          <el-radio-button label="amount">金额</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    <div ref="chartRef" class="chart-container"></div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { TrendCharts as TrendChartsIcon } from '@element-plus/icons-vue'

const props = defineProps({
  data: { type: Array, default: () => [] }
})

const chartRef = ref(null)
const activeTab = ref('customer')
let chartInstance = null

const initChart = () => {
  if (!chartRef.value || props.data.length === 0) return
  if (!chartInstance) chartInstance = echarts.init(chartRef.value)

  const isCustomer = activeTab.value === 'customer'
  const option = {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255, 255, 255, 0.9)', boxShadow: '0 2px 12px 0 rgba(0,0,0,0.1)' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      boundaryGap: false, 
      data: props.data.map(d => d.period),
      axisLine: { lineStyle: { color: '#E4E7ED' } },
      axisLabel: { color: '#909399' }
    },
    yAxis: { 
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { type: 'dashed', color: '#EBEEF5' } }
    },
    series: [{
      name: isCustomer ? '新增客户' : '成交金额',
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: props.data.map(d => isCustomer ? d.newCustomers : d.closedAmount),
      itemStyle: { color: isCustomer ? '#409EFF' : '#E6A23C' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: isCustomer ? 'rgba(64, 158, 255, 0.3)' : 'rgba(230, 162, 60, 0.3)' },
          { offset: 1, color: isCustomer ? 'rgba(64, 158, 255, 0)' : 'rgba(230, 162, 60, 0)' }
        ])
      }
    }]
  }
  chartInstance.setOption(option)
}

watch([() => props.data, activeTab], () => initChart(), { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chartInstance?.resize())
})

onUnmounted(() => {
  window.removeEventListener('resize', () => chartInstance?.resize())
  chartInstance?.dispose()
})
</script>

<style scoped>
.chart-card { border-radius: 12px; margin-bottom: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 8px; font-weight: 600; }
.chart-container { height: 350px; width: 100%; }
</style>
