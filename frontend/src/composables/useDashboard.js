import { ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export function useDashboard(currentUser) {
  // 加载状态
  const loadingActivities = ref(false)
  const loadingTodos = ref(false)

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

  // 图表数据
  const trendData = ref([])
  const industryData = ref([])

  // 最近活动
  const recentActivities = ref([])

  // 待办事项
  const todoList = ref([])

  // 格式化时间方法(用于最近活动)
  const formatTime = (timeStr) => {
    const date = new Date(timeStr)
    const localDate = new Date(date.getTime() + 8 * 60 * 60 * 1000)
    const now = new Date()
    const diff = now - localDate
    
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
    
    return localDate.toLocaleDateString('zh-CN')
  }

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats')
      stats.value = response.data
    } catch (error) {
      console.error('获取统计数据失败:', error)
    }
  }

  const fetchChartsData = async () => {
    try {
      const [trendRes, industryRes] = await Promise.all([
        axios.get('/api/stats/trend?range=month'),
        axios.get('/api/stats/industry')
      ])
      trendData.value = trendRes.data
      
      const industryObj = industryRes.data || {}
      industryData.value = Object.keys(industryObj).map(key => ({
        industry: key,
        count: industryObj[key]
      }))
    } catch (error) {
      console.error('获取图表数据失败:', error)
    }
  }

  const fetchRecentActivities = async () => {
    loadingActivities.value = true
    try {
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
            detail: `客户名称：${customer.name}${customer.company ? ' | 公司：' + customer.company : ''}`,
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
            detail: `客户：${deal.customer_name} | 金额：¥${deal.amount}`,
            data: deal
          })
        }
      })
      
      recentActivities.value = activities.sort((a, b) => {
        return new Date(b.rawTime) - new Date(a.rawTime)
      }).slice(0, 20)
    } catch (error) {
      console.error('获取最近活动失败:', error)
    } finally {
      loadingActivities.value = false
    }
  }

  const fetchTodoList = async () => {
    if (!currentUser || !currentUser.id) return
    loadingTodos.value = true
    try {
      const response = await axios.get('/api/todos', {
        params: { user_id: currentUser.id }
      })
      todoList.value = response.data
    } catch (error) {
      console.error('获取待办事项失败:', error)
    } finally {
      loadingTodos.value = false
    }
  }

  const saveTodo = async (todoForm, isEditing) => {
    if (!currentUser || !currentUser.id) return false
    try {
      const data = {
        ...todoForm,
        user_id: currentUser.id
      }
      
      if (isEditing) {
        await axios.put(`/api/todos/${todoForm.id}`, data)
        ElMessage.success('待办事项更新成功')
      } else {
        await axios.post('/api/todos', data)
        ElMessage.success('待办事项添加成功')
      }
      
      await fetchTodoList()
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '保存失败')
      return false
    }
  }

  const handleTodoChange = async (todo) => {
    if (!currentUser || !currentUser.id) return
    try {
      await axios.put(`/api/todos/${todo.id}`, {
        ...todo,
        user_id: currentUser.id
      })
      if (todo.completed) ElMessage.success('已完成')
    } catch (error) {
      ElMessage.error('更新失败')
      todo.completed = !todo.completed
    }
  }

  const handleTodoCommand = async (command, todo, editCallback) => {
    if (command === 'edit') {
      if (editCallback) editCallback(todo)
    } else if (command === 'delete') {
      try {
        await ElMessageBox.confirm('确定要删除这个待办事项吗？', '提示', { type: 'warning' })
        await axios.delete(`/api/todos/${todo.id}`)
        ElMessage.success('删除成功')
        fetchTodoList()
      } catch (error) {
        if (error !== 'cancel') ElMessage.error('删除失败')
      }
    }
  }

  return {
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
  }
}
