<template>
  <el-row :gutter="20" class="stats-row">
    <el-col :xs="24" :sm="8" :md="6">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-item">
          <div class="stat-label">总交易金额</div>
          <div class="stat-value amount">¥{{ formatAmount(totalAmount) }}</div>
        </div>
      </el-card>
    </el-col>
    <el-col :xs="24" :sm="8" :md="6">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-item">
          <div class="stat-label">已完成金额</div>
          <div class="stat-value success">¥{{ formatAmount(closedAmount) }}</div>
        </div>
      </el-card>
    </el-col>
    <el-col :xs="24" :sm="8" :md="6">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-item">
          <div class="stat-label">待审批交易</div>
          <div class="stat-value warning">{{ pendingApprovalCount }} 笔</div>
        </div>
      </el-card>
    </el-col>
    <el-col :xs="24" :sm="8" :md="6">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-item">
          <div class="stat-label">未收款金额</div>
          <div class="stat-value danger">¥{{ formatAmount(unpaidAmount) }}</div>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
defineProps({
  totalAmount: { type: Number, default: 0 },
  closedAmount: { type: Number, default: 0 },
  pendingApprovalCount: { type: Number, default: 0 },
  unpaidAmount: { type: Number, default: 0 }
})

const formatAmount = (amount) => {
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}
</script>

<style scoped>
.stats-row {
  margin-bottom: 20px;
}
.stat-card {
  text-align: center;
}
.stat-item {
  padding: 10px 0;
}
.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 24px;
  font-weight: 600;
}
.stat-value.amount {
  color: #409eff;
}
.stat-value.success {
  color: #67c23a;
}
.stat-value.warning {
  color: #e6a23c;
}
.stat-value.danger {
  color: #f56c6c;
}
</style>