<template>
  <div class="kpi-section">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6" v-for="item in kpiConfigs" :key="item.key">
        <el-card class="kpi-card" shadow="hover">
          <div class="kpi-content">
            <div class="kpi-icon" :class="item.iconClass">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <div class="kpi-info">
              <div class="kpi-value">{{ item.prefix }}{{ formatValue(data[item.dataKey]) }}{{ item.suffix }}</div>
              <div class="kpi-label">{{ item.label }}</div>
              <div class="kpi-trend" :class="data[item.trendKey] >= 0 ? 'up' : 'down'">
                <el-icon><ArrowUp v-if="data[item.trendKey] >= 0" /><ArrowDown v-else /></el-icon>
                <span>{{ Math.abs(data[item.trendKey]) }}%</span>
                <span class="trend-text">环比</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { User, Money, Message, DataAnalysis, ArrowUp, ArrowDown } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      customers: 0, deals: 0, amount: 0, follow_ups: 0,
      customerTrend: 0, dealTrend: 0, amountTrend: 0, followUpTrend: 0
    })
  }
})

const kpiConfigs = [
  { label: '新增客户', dataKey: 'customers', trendKey: 'customerTrend', icon: User, iconClass: 'customer-icon' },
  { label: '新增交易', dataKey: 'deals', trendKey: 'dealTrend', icon: DataAnalysis, iconClass: 'deal-icon' },
  { label: '成交金额', dataKey: 'amount', trendKey: 'amountTrend', icon: Money, iconClass: 'amount-icon', prefix: '¥' },
  { label: '跟进记录', dataKey: 'follow_ups', trendKey: 'followUpTrend', icon: Message, iconClass: 'follow-icon' }
]

const formatValue = (val) => {
  if (typeof val !== 'number') return 0
  if (val >= 10000) return (val / 10000).toFixed(1) + 'w'
  return val.toLocaleString()
}
</script>

<style scoped>
.kpi-section { margin-bottom: 20px; }
.kpi-card { border-radius: 12px; transition: all 0.3s; }
.kpi-card:hover { transform: translateY(-5px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.kpi-content { display: flex; align-items: center; }
.kpi-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-right: 16px; }
.customer-icon { background: rgba(64, 158, 255, 0.1); color: #409eff; }
.deal-icon { background: rgba(103, 194, 58, 0.1); color: #67c23a; }
.amount-icon { background: rgba(230, 162, 60, 0.1); color: #e6a23c; }
.follow-icon { background: rgba(144, 147, 153, 0.1); color: #909399; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 24px; font-weight: bold; color: #303133; margin-bottom: 4px; }
.kpi-label { font-size: 14px; color: #909399; margin-bottom: 8px; }
.kpi-trend { display: flex; align-items: center; gap: 4px; font-size: 12px; }
.kpi-trend.up { color: #f56c6c; }
.kpi-trend.down { color: #67c23a; }
.trend-text { margin-left: 4px; color: #909399; }
</style>
