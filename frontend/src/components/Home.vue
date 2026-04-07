<template>
  <div class="home-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎回来，{{ currentUser.username }}</h1>
        <p class="welcome-subtitle">今天是 {{ currentDate }}，祝您工作愉快！</p>
      </div>
      <div class="quick-actions">
        <el-button type="primary" @click="navigateTo('customers')">
          <el-icon><Plus /></el-icon>
          新增客户
        </el-button>
        <el-button type="success" @click="navigateTo('follow-ups')">
          <el-icon><Edit /></el-icon>
          添加跟进
        </el-button>
        <el-button type="warning" @click="navigateTo('deals')">
          <el-icon><Money /></el-icon>
          新增交易
        </el-button>
      </div>
    </div>

    <!-- 统计卡片区域 -->
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

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 最近活动 -->
        <el-col :xs="24" :lg="12">
          <el-card class="content-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-left">
                  <el-icon><Clock /></el-icon>
                  <span>最近活动</span>
                  <el-tag type="info" size="small">近30天</el-tag>
                </div>
                <el-button type="text" @click="refreshRecentActivities">刷新</el-button>
              </div>
            </template>
            
            <!-- 搜索框 -->
            <div class="activity-search">
              <el-input
                v-model="activitySearchKeyword"
                placeholder="搜索活动..."
                clearable
                :prefix-icon="Search"
                size="small"
              />
            </div>
            
            <div class="activity-list" v-loading="loadingActivities">
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
          </el-card>
        </el-col>

        <!-- 待办事项 -->
        <el-col :xs="24" :lg="12">
          <el-card class="content-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-left">
                  <el-icon><List /></el-icon>
                  <span>待办事项</span>
                  <el-tag v-if="unfinishedTodoCount > 0" type="danger" size="small">{{ unfinishedTodoCount }}个待办</el-tag>
                </div>
                <el-button type="primary" size="small" @click="showAddTodoDialog">
                  <el-icon><Plus /></el-icon>
                  新增
                </el-button>
              </div>
            </template>
            <div class="todo-list" v-loading="loadingTodos">
              <div v-for="(todo, index) in todoList" :key="todo.id" class="todo-item">
                <div class="todo-left">
                  <el-checkbox v-model="todo.completed" @change="handleTodoChange(todo)">
                    <span :class="{ 'completed': todo.completed }">{{ todo.content }}</span>
                  </el-checkbox>
                </div>
                <div class="todo-right">
                  <el-tag :type="getPriorityType(todo.priority)" size="small">
                    {{ getPriorityLabel(todo.priority) }}
                  </el-tag>
                  <el-dropdown trigger="click" @command="(cmd) => handleTodoCommand(cmd, todo)">
                    <el-button type="text" size="small">
                      <el-icon><More /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="edit">编辑</el-dropdown-item>
                        <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
              <el-empty v-if="todoList.length === 0" description="暂无待办事项，点击上方按钮添加" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-access">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Grid /></el-icon>
            <span>快捷入口</span>
          </div>
        </template>
        <div class="quick-grid">
          <div class="quick-item" @click="navigateTo('customers')">
            <div class="quick-icon customer">
              <el-icon><User /></el-icon>
            </div>
            <div class="quick-label">客户管理</div>
          </div>
          <div class="quick-item" @click="navigateTo('follow-ups')">
            <div class="quick-icon follow">
              <el-icon><Message /></el-icon>
            </div>
            <div class="quick-label">跟进记录</div>
          </div>
          <div class="quick-item" @click="navigateTo('deals')">
            <div class="quick-icon deal">
              <el-icon><Money /></el-icon>
            </div>
            <div class="quick-label">交易管理</div>
          </div>
          <div class="quick-item" @click="navigateTo('stats')">
            <div class="quick-icon stats">
              <el-icon><DataBoard /></el-icon>
            </div>
            <div class="quick-label">统计分析</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 活动详情对话框 -->
    <el-dialog
      v-model="activityDetailVisible"
      title="活动详情"
      width="500px"
      destroy-on-close
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

    <!-- 待办事项对话框 -->
    <el-dialog
      v-model="todoDialogVisible"
      :title="isEditingTodo ? '编辑待办事项' : '新增待办事项'"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="todoFormRef"
        :model="todoForm"
        :rules="todoRules"
        label-width="80px"
      >
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="todoForm.content"
            type="textarea"
            :rows="3"
            placeholder="请输入待办事项内容"
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="todoForm.priority">
            <el-radio-button label="high">高</el-radio-button>
            <el-radio-button label="medium">中</el-radio-button>
            <el-radio-button label="low">低</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="todoDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTodo" :loading="savingTodo">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { 
  User, Message, Money, DataBoard, Plus, Edit, Search, More, ArrowRight,
  ArrowUp, ArrowDown, Clock, List, Grid, Document 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ username: '', id: null })
  }
})

const emit = defineEmits(['navigate'])

// 加载状态
const loadingActivities = ref(false)
const loadingTodos = ref(false)
const savingTodo = ref(false)

// 统计数据
const stats = ref({
  total_customers: 0,
  total_deals: 0,
  total_amount: 0,
  total_follow_ups: 0,
  customer_trend: 0,
  deal_trend: 0,
  amount_trend: 0,
  follow_up_trend: 0
})

// 最近活动
const recentActivities = ref([])
const activitySearchKeyword = ref('')
const activityDetailVisible = ref(false)
const selectedActivity = ref(null)

// 待办事项
const todoList = ref([])
const todoDialogVisible = ref(false)
const isEditingTodo = ref(false)
const todoFormRef = ref(null)
const todoForm = ref({
  id: null,
  content: '',
  priority: 'medium',
  completed: false
})

// 待办事项验证规则
const todoRules = {
  content: [
    { required: true, message: '请输入待办事项内容', trigger: 'blur' },
    { min: 1, max: 200, message: '内容长度在1-200个字符之间', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

// 计算属性
const currentDate = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const weekDay = weekDays[now.getDay()]
  return `${year}年${month}月${day}日 星期${weekDay}`
})

const filteredActivities = computed(() => {
  if (!activitySearchKeyword.value) return recentActivities.value
  const keyword = activitySearchKeyword.value.toLowerCase()
  return recentActivities.value.filter(activity => 
    activity.title.toLowerCase().includes(keyword)
  )
})

const unfinishedTodoCount = computed(() => {
  return todoList.value.filter(todo => !todo.completed).length
})

// 格式化方法
const formatAmount = (amount) => {
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toLocaleString()
}

const formatInteger = (num) => {
  return Math.round(num).toLocaleString('zh-CN')
}

const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString('zh-CN')
}

const getPriorityType = (priority) => {
  const types = { high: 'danger', medium: 'warning', low: 'info' }
  return types[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const labels = { high: '高', medium: '中', low: '低' }
  return labels[priority] || '低'
}

const getActivityTypeTag = (type) => {
  const tags = { customer: 'primary', deal: 'success', follow: 'warning' }
  return tags[type] || ''
}

const getActivityTypeLabel = (type) => {
  const labels = { customer: '新增客户', deal: '新增交易', follow: '跟进记录' }
  return labels[type] || '其他'
}

// 数据获取方法
const fetchStats = async () => {
  try {
    const response = await axios.get('/api/stats')
    stats.value = response.data
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

const fetchRecentActivities = async () => {
  loadingActivities.value = true
  try {
    // 获取近30天的数据
    const thirtyDaysAgo = new Date()
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
    
    const [customersRes, followUpsRes, dealsRes] = await Promise.all([
      axios.get('/api/stats/recent-customers'),
      axios.get('/api/stats/recent-follow-ups'),
      axios.get('/api/deals')
    ])
    
    const activities = []
    
    customersRes.data.forEach(customer => {
      const createdAt = new Date(customer.created_at)
      if (createdAt >= thirtyDaysAgo) {
        activities.push({
          type: 'customer',
          title: `新增客户：${customer.name}`,
          time: formatTime(customer.created_at),
          rawTime: customer.created_at,
          detail: `客户名称：${customer.name}${customer.company ? ' | 公司：' + customer.company : ''}${customer.phone ? ' | 电话：' + customer.phone : ''}`,
          data: customer
        })
      }
    })
    
    followUpsRes.data.forEach(follow => {
      const createdAt = new Date(follow.created_at)
      if (createdAt >= thirtyDaysAgo) {
        activities.push({
          type: 'follow',
          title: `跟进记录：${follow.customer_name}`,
          time: formatTime(follow.created_at),
          rawTime: follow.created_at,
          detail: `跟进内容：${follow.content}`,
          data: follow
        })
      }
    })
    
    dealsRes.data.forEach(deal => {
      const createdAt = new Date(deal.created_at)
      if (createdAt >= thirtyDaysAgo) {
        activities.push({
          type: 'deal',
          title: `新增交易：¥${deal.amount}`,
          time: formatTime(deal.created_at),
          rawTime: deal.created_at,
          detail: `交易金额：¥${deal.amount} | 客户：${deal.customer_name}${deal.product ? ' | 产品：' + deal.product : ''}`,
          data: deal
        })
      }
    })
    
    // 按时间排序
    recentActivities.value = activities.sort((a, b) => {
      return new Date(b.rawTime) - new Date(a.rawTime)
    }).slice(0, 20)
  } catch (error) {
    console.error('获取最近活动失败:', error)
    ElMessage.error('获取最近活动失败')
  } finally {
    loadingActivities.value = false
  }
}

const fetchTodoList = async () => {
  loadingTodos.value = true
  try {
    const response = await axios.get('/api/todos', {
      params: { user_id: props.currentUser.id }
    })
    todoList.value = response.data
  } catch (error) {
    console.error('获取待办事项失败:', error)
    ElMessage.error('获取待办事项失败')
  } finally {
    loadingTodos.value = false
  }
}

// 活动详情方法
const showActivityDetail = (activity) => {
  selectedActivity.value = activity
  activityDetailVisible.value = true
}

const navigateToDetail = (activity) => {
  if (!activity) return
  activityDetailVisible.value = false
  if (activity.type === 'customer') {
    navigateTo('customers')
  } else if (activity.type === 'deal') {
    navigateTo('deals')
  } else if (activity.type === 'follow') {
    navigateTo('follow-ups')
  }
}

// 待办事项方法
const showAddTodoDialog = () => {
  isEditingTodo.value = false
  todoForm.value = {
    id: null,
    content: '',
    priority: 'medium',
    completed: false
  }
  todoDialogVisible.value = true
}

const editTodo = (todo) => {
  isEditingTodo.value = true
  todoForm.value = { ...todo }
  todoDialogVisible.value = true
}

const saveTodo = async () => {
  if (!todoFormRef.value) return
  
  await todoFormRef.value.validate(async (valid) => {
    if (valid) {
      savingTodo.value = true
      try {
        const data = {
          ...todoForm.value,
          user_id: props.currentUser.id
        }
        
        if (isEditingTodo.value) {
          await axios.put(`/api/todos/${todoForm.value.id}`, data)
          ElMessage.success('待办事项更新成功')
        } else {
          await axios.post('/api/todos', data)
          ElMessage.success('待办事项添加成功')
        }
        
        todoDialogVisible.value = false
        fetchTodoList()
      } catch (error) {
        console.error('保存待办事项失败:', error)
        ElMessage.error(error.response?.data?.message || '保存失败')
      } finally {
        savingTodo.value = false
      }
    }
  })
}

const handleTodoChange = async (todo) => {
  try {
    await axios.put(`/api/todos/${todo.id}`, {
      ...todo,
      user_id: props.currentUser.id
    })
    if (todo.completed) {
      ElMessage.success('已完成')
    }
  } catch (error) {
    console.error('更新待办事项失败:', error)
    ElMessage.error('更新失败')
    todo.completed = !todo.completed
  }
}

const handleTodoCommand = async (command, todo) => {
  if (command === 'edit') {
    editTodo(todo)
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除这个待办事项吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await axios.delete(`/api/todos/${todo.id}`)
      ElMessage.success('删除成功')
      fetchTodoList()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除待办事项失败:', error)
        ElMessage.error('删除失败')
      }
    }
  }
}

// 通用方法
const navigateTo = (route) => {
  emit('navigate', route)
}

const refreshRecentActivities = () => {
  fetchRecentActivities()
  ElMessage.success('刷新成功')
}

onMounted(() => {
  fetchStats()
  fetchRecentActivities()
  fetchTodoList()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

/* 欢迎区域 */
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

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.welcome-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.quick-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 28px;
}

.customer-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.deal-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.amount-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.follow-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.stat-trend.up {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.stat-trend.down {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

/* 主要内容区域 */
.main-content {
  margin-bottom: 20px;
}

.content-card {
  border-radius: 12px;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

/* 活动搜索 */
.activity-search {
  margin-bottom: 12px;
}

/* 活动列表 */
.activity-list {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.activity-item:hover {
  background-color: #f5f7fa;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 18px;
  flex-shrink: 0;
}

.activity-icon.customer {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.activity-icon.deal {
  background: rgba(240, 147, 251, 0.1);
  color: #f093fb;
}

.activity-icon.follow {
  background: rgba(67, 233, 123, 0.1);
  color: #43e97b;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

.activity-arrow {
  color: #c0c4cc;
  margin-left: 8px;
}

/* 待办事项 */
.todo-list {
  max-height: 300px;
  overflow-y: auto;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.todo-item:last-child {
  border-bottom: none;
}

.todo-left {
  flex: 1;
  min-width: 0;
}

.todo-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.todo-item .completed {
  text-decoration: line-through;
  color: #909399;
}

/* 快捷入口 */
.quick-access {
  margin-bottom: 20px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-item:hover {
  background: #f5f7fa;
  transform: translateY(-4px);
}

.quick-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 28px;
  transition: all 0.3s ease;
}

.quick-icon.customer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.quick-icon.follow {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.quick-icon.deal {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.quick-icon.stats {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.quick-item:hover .quick-icon {
  transform: scale(1.1);
}

.quick-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .quick-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .stat-card {
    margin-bottom: 12px;
  }
  
  .quick-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
