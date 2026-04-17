<template>
  <el-row :gutter="20" class="dist-section">
    <el-col :xs="24" :lg="12">
      <el-card class="dist-card" shadow="hover">
        <template #header><div class="card-header"><span>客户行业分布</span></div></template>
        <div ref="industryChartRef" class="chart-container"></div>
      </el-card>
    </el-col>
    <el-col :xs="24" :lg="12">
      <el-card class="dist-card" shadow="hover">
        <template #header><div class="card-header"><span>客户状态构成</span></div></template>
        <div ref="statusChartRef" class="chart-container"></div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  industryData: { type: Array, default: () => [] },
  statusData: { type: Array, default: () => [] }
})

const industryChartRef = ref(null)
const statusChartRef = ref(null)
let industryChart = null
let statusChart = null

const initIndustryChart = () => {
  if (!industryChartRef.value || props.industryData.length === 0) return
  if (!industryChart) industryChart = echarts.init(industryChartRef.value)
  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center', itemWidth: 8, textStyle: { fontSize: 12 } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data: props.industryData.map(d => ({ name: d.industry || '未知', value: d.count }))
    }]
  }
  industryChart.setOption(option)
}

const initStatusChart = () => {
  if (!statusChartRef.value || props.statusData.length === 0) return
  if (!statusChart) statusChart = echarts.init(statusChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: '70%',
      roseType: 'radius',
      data: props.statusData.map(d => ({ name: d.status, value: d.count })),
      itemStyle: { borderRadius: 5 }
    }]
  }
  statusChart.setOption(option)
}

watch(() => props.industryData, () => initIndustryChart(), { deep: true })
watch(() => props.statusData, () => initStatusChart(), { deep: true })

onMounted(() => {
  initIndustryChart()
  initStatusChart()
  window.addEventListener('resize', () => {
    industryChart?.resize()
    statusChart?.resize()
  })
})

onUnmounted(() => {
  industryChart?.dispose()
  statusChart?.dispose()
})
</script>

<style scoped>
.dist-section { margin-bottom: 20px; }
.dist-card { border-radius: 12px; }
.chart-container { height: 300px; width: 100%; }
</style>
