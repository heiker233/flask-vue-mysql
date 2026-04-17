import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export function useDeals() {
  const deals = ref([])
  const customers = ref([])
  const customerOptions = ref([])
  const productList = ref([])
  const loading = ref(false)

  // Filters
  const searchQuery = ref('')
  const filterStatus = ref('')
  const timeRange = ref('month')
  const dateRange = ref([])
  
  // Pagination
  const currentPage = ref(1)
  const pageSize = ref(10)

  // API Calls
  const fetchDeals = async () => {
    loading.value = true
    try {
      const params = new URLSearchParams()
      if (searchQuery.value) params.append('keyword', searchQuery.value)
      if (filterStatus.value) params.append('status', filterStatus.value)
      if (dateRange.value && dateRange.value.length === 2) {
        params.append('start_date', dateRange.value[0])
        params.append('end_date', dateRange.value[1])
      }
      params.append('page', currentPage.value)
      params.append('pageSize', pageSize.value)

      const response = await axios.get(`/api/deals?${params.toString()}`)
      deals.value = response.data.items || response.data
      totalServer.value = response.data.total || response.data.length
      if (response.data.stats) {
        serverStats.value = response.data.stats
      }
    } catch (error) {
      console.error('获取交易记录失败:', error)
      ElMessage.error('获取交易记录列表失败')
    } finally {
      loading.value = false
    }
  }

  const fetchCustomers = async () => {
    try {
      const response = await axios.get('/api/customers')
      customers.value = response.data
      customerOptions.value = response.data
    } catch (error) {
      console.error('获取客户列表失败:', error)
    }
  }

  const fetchProducts = async () => {
    try {
      const response = await axios.get('/api/products')
      productList.value = response.data
    } catch (error) {
      console.error('获取产品列表失败:', error)
    }
  }

  const deleteDeal = async (id) => {
    try {
      await ElMessageBox.confirm('确定要删除这条交易记录吗？此操作不可恢复！', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      await axios.delete(`/api/deals/${id}`)
      ElMessage.success('交易记录删除成功')
      await fetchDeals()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除交易记录失败:', error)
        ElMessage.error(error?.response?.data?.message || '删除交易记录失败')
      }
    }
  }

  const submitApproval = async (approvalDeal, approvalForm, currentUser) => {
    if (!approvalDeal) return false
    
    try {
      const response = await axios.post(`/api/deals/${approvalDeal.id}/approve`, {
        action: approvalForm.action,
        comment: approvalForm.comment,
        approver_id: currentUser?.id || 1
      })
      
      if (response.data.success) {
        ElMessage.success(response.data.message)
        await fetchDeals()
        return true
      } else {
        ElMessage.error(response.data.message || '审批失败')
        return false
      }
    } catch (error) {
      console.error('审批失败:', error)
      ElMessage.error(error.response?.data?.message || '审批失败')
      return false
    }
  }

  // Filter Logic
  const filteredDeals = computed(() => deals.value)
  const paginatedDeals = computed(() => deals.value)
  const filteredTotal = computed(() => totalServer.value)
  const total = computed(() => totalServer.value)
  const serverStats = ref({})
  const totalServer = ref(0)

  const currentFilters = computed(() => {
    return {
      keyword: searchQuery.value,
      status: filterStatus.value,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1]
    }
  })

  const totalAmount = computed(() => serverStats.value.totalAmount || 0)
  const closedAmount = computed(() => serverStats.value.closedAmount || 0)
  const negotiatingAmount = computed(() => serverStats.value.negotiatingAmount || 0)
  const pendingApprovalCount = computed(() => serverStats.value.pendingApprovalCount || 0)
  const unpaidAmount = computed(() => serverStats.value.unpaidAmount || 0)

  return {
    deals,
    customers,
    customerOptions,
    productList,
    loading,
    
    searchQuery,
    filterStatus,
    timeRange,
    dateRange,
    currentPage,
    pageSize,
    
    filteredDeals,
    paginatedDeals,
    filteredTotal,
    total,
    currentFilters,
    
    totalAmount,
    closedAmount,
    negotiatingAmount,
    pendingApprovalCount,
    unpaidAmount,
    
    fetchDeals,
    fetchCustomers,
    fetchProducts,
    deleteDeal,
    submitApproval
  }
}
