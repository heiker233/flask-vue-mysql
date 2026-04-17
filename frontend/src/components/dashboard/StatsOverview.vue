<template>
  <div class="stats-section">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon customer-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatInteger(stats.total_customers) }}</div>
            <div class="stat-label">总客户数</div>
            <div class="stat-trend" :class="stats.customer_trend >= 0 ? 'up' : 'down'">
              <el-icon><ArrowUp v-if="stats.customer_trend >= 0" /><ArrowDown v-else /></el-icon>
              {{ Math.abs(stats.customer_trend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon deal-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatInteger(stats.total_deals) }}</div>
            <div class="stat-label">总交易数</div>
            <div class="stat-trend" :class="stats.deal_trend >= 0 ? 'up' : 'down'">
              <el-icon><ArrowUp v-if="stats.deal_trend >= 0" /><ArrowDown v-else /></el-icon>
              {{ Math.abs(stats.deal_trend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon amount-icon">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ formatAmount(stats.total_amount) }}</div>
            <div class="stat-label">完成交易金额</div>
            <div class="stat-trend" :class="stats.amount_trend >= 0 ? 'up' : 'down'">
              <el-icon><ArrowUp v-if="stats.amount_trend >= 0" /><ArrowDown v-else /></el-icon>
              {{ Math.abs(stats.amount_trend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon follow-icon">
            <el-icon><Message /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatInteger(stats.total_follow_ups) }}</div>
            <div class="stat-label">跟进记录</div>
            <div class="stat-trend" :class="stats.follow_up_trend >= 0 ? 'up' : 'down'">
              <el-icon><ArrowUp v-if="stats.follow_up_trend >= 0" /><ArrowDown v-else /></el-icon>
              {{ Math.abs(stats.follow_up_trend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { User, Document, Money, Message, ArrowUp, ArrowDown } from '@element-plus/icons-vue'

defineProps({
  stats: {
    type: Object,
    required: true
  }
})

const formatAmount = (amount) => {
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return (amount || 0).toLocaleString()
}

const formatInteger = (num) => {
  return Math.round(num || 0).toLocaleString('zh-CN')
}
</script>

<style scoped>
.stats-section { margin-bottom: 20px; }
.stat-card { border-radius: 12px; transition: all 0.3s ease; }
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }
.stat-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 16px; font-size: 28px; }
.customer-icon { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.deal-icon { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.amount-icon { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
.follow-icon { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; }
.stat-info { display: flex; flex-direction: column; }
.stat-card :deep(.el-card__body) { display: flex; align-items: center; padding: 20px; }
.stat-value { font-size: 24px; font-weight: 700; color: #303133; margin-bottom: 4px; }
.stat-label { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-trend { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 600; padding: 4px 8px; border-radius: 4px; }
.stat-trend.up { background: rgba(103, 194, 58, 0.1); color: #67c23a; }
.stat-trend.down { background: rgba(245, 108, 108, 0.1); color: #f56c6c; }
</style>
