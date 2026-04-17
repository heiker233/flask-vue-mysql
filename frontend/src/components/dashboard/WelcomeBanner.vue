<template>
  <div class="welcome-section">
    <div class="welcome-content">
      <h1 class="welcome-title">欢迎回来，{{ currentUser.username }}</h1>
      <p class="welcome-subtitle">今天是 {{ currentDate }}，祝您工作愉快！</p>
    </div>
    <div class="quick-actions">
      <el-button type="primary" @click="$emit('navigate', 'customers')">
        <el-icon><Plus /></el-icon>
        新增客户
      </el-button>
      <el-button type="success" @click="$emit('navigate', 'follow-ups')">
        <el-icon><Edit /></el-icon>
        添加跟进
      </el-button>
      <el-button type="warning" @click="$emit('navigate', 'deals')">
        <el-icon><Money /></el-icon>
        新增交易
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, Edit, Money } from '@element-plus/icons-vue'

const props = defineProps({
  currentUser: {
    type: Object,
    required: true
  }
})

defineEmits(['navigate'])

const currentDate = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const weekDay = weekDays[now.getDay()]
  return `${year}年${month}月${day}日 星期${weekDay}`
})
</script>

<style scoped>
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.welcome-title { font-size: 28px; font-weight: 600; margin: 0 0 10px 0; }
.welcome-subtitle { font-size: 16px; opacity: 0.9; margin: 0; }
.quick-actions { display: flex; gap: 12px; }

@media (max-width: 768px) {
  .welcome-section { flex-direction: column; text-align: center; gap: 20px; }
  .quick-actions { flex-wrap: wrap; justify-content: center; }
}
</style>
