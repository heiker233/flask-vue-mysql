<template>
  <el-card class="content-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <el-icon><Clock /></el-icon>
          <span>最近活动</span>
          <el-tag type="info" size="small">近30天</el-tag>
        </div>
        <el-button type="text" @click="$emit('refresh')">刷新</el-button>
      </div>
    </template>
    
    <div class="activity-search">
      <el-input
        v-model="activitySearchKeyword"
        placeholder="搜索活动..."
        clearable
        :prefix-icon="Search"
        size="small"
      />
    </div>
    
    <div class="activity-list" v-loading="loading">
      <div 
        v-for="(activity, index) in filteredActivities" 
        :key="index" 
        class="activity-item"
        @click="showActivityDetail(activity)"
      >
        <div class="activity-icon" :class="activity.type">
          <el-icon>
            <User v-if="activity.type === 'customer'" />
            <Document v-if="activity.type === 'deal'" />
            <Message v-if="activity.type === 'follow'" />
          </el-icon>
        </div>
        <div class="activity-content">
          <div class="activity-title">{{ activity.title }}</div>
          <div class="activity-time">{{ activity.time }}</div>
        </div>
        <el-icon class="activity-arrow"><ArrowRight /></el-icon>
      </div>
      <el-empty v-if="filteredActivities.length === 0" description="暂无活动记录" />
    </div>

    <!-- 活动详情对话框 -->
    <el-dialog
      v-model="activityDetailVisible"
      title="活动详情"
      width="500px"
      destroy-on-close
      append-to-body
    >
      <el-descriptions :column="1" border v-if="selectedActivity">
        <el-descriptions-item label="活动类型">
          <el-tag :type="getActivityTypeTag(selectedActivity.type)">
            {{ getActivityTypeLabel(selectedActivity.type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="活动标题">{{ selectedActivity.title }}</el-descriptions-item>
        <el-descriptions-item label="发生时间">{{ selectedActivity.time }}</el-descriptions-item>
        <el-descriptions-item label="详细信息" v-if="selectedActivity.detail">
          {{ selectedActivity.detail }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="activityDetailVisible = false">关闭</el-button>
        <el-button type="primary" @click="navigateToDetail(selectedActivity)">
          查看详情
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Clock, Search, User, Document, Message, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  activities: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'navigate'])

const activitySearchKeyword = ref('')
const activityDetailVisible = ref(false)
const selectedActivity = ref(null)

const filteredActivities = computed(() => {
  if (!activitySearchKeyword.value) return props.activities
  const keyword = activitySearchKeyword.value.toLowerCase()
  return props.activities.filter(activity => 
    activity.title.toLowerCase().includes(keyword)
  )
})

const showActivityDetail = (activity) => {
  selectedActivity.value = activity
  activityDetailVisible.value = true
}

const navigateToDetail = (activity) => {
  if (!activity) return
  activityDetailVisible.value = false
  if (activity.type === 'customer') {
    emit('navigate', 'customers')
  } else if (activity.type === 'deal') {
    emit('navigate', 'deals')
  } else if (activity.type === 'follow') {
    emit('navigate', 'follow-ups')
  }
}

const getActivityTypeTag = (type) => {
  const tags = { customer: 'primary', deal: 'success', follow: 'warning' }
  return tags[type] || ''
}

const getActivityTypeLabel = (type) => {
  const labels = { customer: '新增客户', deal: '新增交易', follow: '跟进记录' }
  return labels[type] || '其他'
}
</script>

<style scoped>
.content-card { border-radius: 12px; height: 100%; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; }
.activity-search { margin-bottom: 12px; }
.activity-list { max-height: 300px; overflow-y: auto; }
.activity-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #ebeef5; cursor: pointer; }
.activity-item:hover { background-color: #f5f7fa; }
.activity-icon { width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-size: 18px; flex-shrink: 0; }
.activity-icon.customer { background: rgba(102, 126, 234, 0.1); color: #667eea; }
.activity-icon.deal { background: rgba(240, 147, 251, 0.1); color: #f093fb; }
.activity-icon.follow { background: rgba(67, 233, 123, 0.1); color: #43e97b; }
.activity-content { flex: 1; }
.activity-title { font-size: 14px; color: #303133; margin-bottom: 4px; }
.activity-time { font-size: 12px; color: #909399; }
.activity-arrow { margin-left: 8px; color: #c0c4cc; }
</style>
