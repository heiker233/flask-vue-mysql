<template>
  <div class="home-container">
    <!-- 欢迎区域 -->
    <WelcomeBanner 
      :current-user="currentUser" 
      @navigate="navigateTo" 
    />

    <!-- 快捷入口 -->
    <QuickAccess @navigate="navigateTo" />

    <!-- 统计卡片区域 -->
    <StatsOverview :stats="stats" />

    <!-- 图表展示区域 -->
    <ChartsSection 
      :trend-data="trendData" 
      :industry-data="industryData" 
    />

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 最近活动 -->
        <el-col :xs="24" :lg="12">
          <ActivityTimeline 
            :activities="recentActivities" 
            :loading="loadingActivities"
            @refresh="fetchRecentActivities"
            @navigate="navigateTo"
          />
        </el-col>

        <!-- 待办事项 -->
        <el-col :xs="24" :lg="12">
          <TodoWidget 
            :todos="todoList"
            :loading="loadingTodos"
            @save="handleSaveTodo"
            @change="handleTodoChange"
            @command="handleTodoCommand"
          />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useDashboard } from '../composables/useDashboard'

// 导入子组件
import WelcomeBanner from './dashboard/WelcomeBanner.vue'
import StatsOverview from './dashboard/StatsOverview.vue'
import ChartsSection from './dashboard/ChartsSection.vue'
import ActivityTimeline from './dashboard/ActivityTimeline.vue'
import TodoWidget from './dashboard/TodoWidget.vue'
import QuickAccess from './dashboard/QuickAccess.vue'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ username: '', id: null })
  }
})

const emit = defineEmits(['navigate'])

// 导航方法
const navigateTo = (route) => {
  emit('navigate', route)
}

// 使用 Composable 提取逻辑
const {
  loadingActivities,
  loadingTodos,
  stats,
  trendData,
  industryData,
  recentActivities,
  todoList,
  fetchStats,
  fetchChartsData,
  fetchRecentActivities,
  fetchTodoList,
  saveTodo,
  handleTodoChange,
  handleTodoCommand
} = useDashboard(props.currentUser)

const handleSaveTodo = async (todoForm, isEditing, callback) => {
  const success = await saveTodo(todoForm, isEditing)
  if (callback) callback(success)
}

onMounted(() => {
  fetchStats()
  fetchChartsData()
  fetchRecentActivities()
  if (props.currentUser && props.currentUser.id) {
    fetchTodoList()
  }
})

watch(() => props.currentUser?.id, (newId) => {
  if (newId) {
    fetchTodoList()
  }
})
</script>

<style scoped>
.home-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

.main-content {
  margin-bottom: 20px;
}
</style>
