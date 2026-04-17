import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

export function useFollowUps() {
  const followUps = ref([])
  const loading = ref(false)

  // 搜索和筛选状态
  const searchQuery = ref('')
  const filterType = ref('')
  const timeRange = ref('month')
  const dateRange = ref([])

  // 分页状态
  const currentPage = ref(1)
  const pageSize = ref(10)

  // 获取数据
  const fetchFollowUps = async () => {
    loading.value = true
    try {
      const response = await axios.get('/api/follow-ups')
      followUps.value = response.data
    } catch (error) {
      console.error('获取跟进记录失败:', error)
      ElMessage.error('获取跟进记录列表失败')
    } finally {
      loading.value = false
    }
  }

  // 经过筛选的基础数据
  const filteredData = computed(() => {
    let result = followUps.value

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(followUp =>
        (followUp.customer_name && followUp.customer_name.toLowerCase().includes(query)) ||
        (followUp.content && followUp.content.toLowerCase().includes(query))
      )
    }

    if (filterType.value) {
      result = result.filter(followUp => followUp.follow_type === filterType.value)
    }

    if (dateRange.value && dateRange.value.length === 2) {
      const startDateStr = dateRange.value[0]
      const endDateStr = dateRange.value[1]
      result = result.filter(followUp => {
        const dateStr = followUp.next_follow_date
          ? followUp.next_follow_date.substring(0, 10)
          : followUp.created_at.substring(0, 10)
        return dateStr >= startDateStr && dateStr <= endDateStr
      })
    }

    return result
  })

  // 分页后的数据
  const paginatedFollowUps = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return filteredData.value.slice(start, end)
  })

  // 筛选后的总数
  const filteredTotal = computed(() => filteredData.value.length)

  // 获取当前筛选条件（用于导出）
  const currentFilters = computed(() => {
    return {
      keyword: searchQuery.value,
      follow_type: filterType.value,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1]
    }
  })

  return {
    followUps,
    loading,
    searchQuery,
    filterType,
    timeRange,
    dateRange,
    currentPage,
    pageSize,
    fetchFollowUps,
    paginatedFollowUps,
    filteredTotal,
    currentFilters
  }
}
