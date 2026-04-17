<template>
  <div class="quick-access">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Grid /></el-icon>
          <span>快捷入口</span>
        </div>
      </template>
      <div class="quick-grid">
        <div class="quick-item" @click="handleNavigate('customers')">
          <div class="quick-icon customer">
            <el-icon><User /></el-icon>
          </div>
          <div class="quick-label">客户管理</div>
        </div>
        <div class="quick-item" @click="handleNavigate('follow-ups')">
          <div class="quick-icon follow">
            <el-icon><Message /></el-icon>
          </div>
          <div class="quick-label">跟进记录</div>
        </div>
        <div class="quick-item" @click="handleNavigate('deals')">
          <div class="quick-icon deal">
            <el-icon><Money /></el-icon>
          </div>
          <div class="quick-label">交易管理</div>
        </div>
        <div class="quick-item" @click="handleNavigate('stats')">
          <div class="quick-icon stats">
            <el-icon><DataBoard /></el-icon>
          </div>
          <div class="quick-label">统计分析</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { Grid, User, Message, Money, DataBoard } from '@element-plus/icons-vue'

const emit = defineEmits(['navigate'])

const handleNavigate = (route) => {
  emit('navigate', route)
}
</script>

<style scoped>
.quick-access { margin-bottom: 20px; }
.card-header { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; }
.quick-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 20px; }
.quick-item { display: flex; flex-direction: column; align-items: center; padding: 20px; border-radius: 12px; cursor: pointer; transition: all 0.3s ease; }
.quick-item:hover { background: #f5f7fa; transform: translateY(-4px); }
.quick-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; font-size: 28px; transition: all 0.3s ease; }
.quick-icon.customer { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.quick-icon.follow { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; }
.quick-icon.deal { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.quick-icon.stats { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
.quick-label { font-size: 14px; color: #606266; font-weight: 500; }

@media (max-width: 768px) {
  .quick-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
