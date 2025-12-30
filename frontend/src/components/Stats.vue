<template>
  <div class="stats-container">
    <div class="page-header">
      <h2>统计分析</h2>
    </div>
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="card-content">
          <div class="card-icon customer-icon">
            <User />
          </div>
          <div class="card-info">
            <div class="card-value">{{ customerStats.total }}</div>
            <div class="card-label">总客户数</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="card-content">
          <div class="card-icon deal-icon">
            <Money />
          </div>
          <div class="card-info">
            <div class="card-value">{{ dealStats.total_deals }}</div>
            <div class="card-label">总交易数</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="card-content">
          <div class="card-icon amount-icon">
            <DataAnalysis />
          </div>
          <div class="card-info">
            <div class="card-value">¥{{ dealStats.closed_amount }}</div>
            <div class="card-label">完成交易金额</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="stats-tables">
      <el-card class="table-card" title="客户状态分布">
        <el-table :data="customerStatusData" border stripe style="width: 100%">
          <el-table-column prop="status" label="状态" />
          <el-table-column prop="count" label="数量" />
        </el-table>
      </el-card>

      <el-card class="table-card" title="交易状态分布">
        <el-table :data="dealStatusData" border stripe style="width: 100%">
          <el-table-column prop="status" label="状态" />
          <el-table-column prop="count" label="数量" />
          <el-table-column prop="amount" label="金额" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { User, Money, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const customerStats = ref({ total: 0, potential: 0, active: 0, lost: 0 })
const dealStats = ref({ total_deals: 0, total_amount: 0, closed_deals: 0, closed_amount: 0 })

const customerStatusData = computed(() => [
  { status: '潜在客户', count: customerStats.value.potential },
  { status: '活跃客户', count: customerStats.value.active },
  { status: '已流失客户', count: customerStats.value.lost }
])

const dealStatusData = computed(() => [
  { status: '总交易', count: dealStats.value.total_deals, amount: `¥${dealStats.value.total_amount}` },
  { status: '已完成', count: dealStats.value.closed_deals, amount: `¥${dealStats.value.closed_amount}` }
])

const fetchCustomerStats = async () => {
  try {
    const response = await axios.get('/api/stats/customers')
    customerStats.value = response.data
  } catch (error) {
    console.error('获取客户统计失败:', error)
    const errorMessage = error.response?.data?.message || '获取客户统计数据失败'
    ElMessage.error(errorMessage)
  }
}

const fetchDealStats = async () => {
  try {
    const response = await axios.get('/api/stats/deals')
    dealStats.value = response.data
  } catch (error) {
    console.error('获取交易统计失败:', error)
    const errorMessage = error.response?.data?.message || '获取交易统计数据失败'
    ElMessage.error(errorMessage)
  }
}

onMounted(() => {
  fetchCustomerStats()
  fetchDealStats()
})
</script>

<style scoped>
.stats-container {
  height: 100%;
}

.page-header {
  margin-bottom: 20px;
}

.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 250px;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.customer-icon {
  background-color: #e3f2fd;
  color: #2196f3;
}

.deal-icon {
  background-color: #f3e5f5;
  color: #9c27b0;
}

.amount-icon {
  background-color: #e8f5e8;
  color: #4caf50;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
}

.card-label {
  color: #666;
}

.stats-tables {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.table-card {
  height: 400px;
}
</style>