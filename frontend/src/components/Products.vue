<template>
  <div class="products-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Box /></el-icon>
        <h2>产品库管理</h2>
        <el-tag type="info" class="count-tag">共 {{ total }} 个产品</el-tag>
      </div>
      <el-button v-if="isAdmin" type="primary" @click="openAddDialog" :icon="Plus">
        添加产品
      </el-button>
    </div>

    <el-card class="search-card" shadow="never">
      <el-row :gutter="20" align="middle">
        <el-col :span="12">
          <el-input
            v-model="searchQuery"
            placeholder="搜索产品名称、描述"
            clearable
            :prefix-icon="Search"
            @input="handleSearch"
            class="search-input"
          />
        </el-col>
        <el-col :span="12" style="text-align: right;">
          <el-button @click="resetFilters" :icon="RefreshRight">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <el-table
        :data="paginatedProducts"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="产品名称" min-width="150">
          <template #default="scope">
            <div class="product-name">
              <el-icon class="product-icon"><Box /></el-icon>
              <span>{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="单价" width="120" align="right">
          <template #default="scope">
            <span class="price-text">¥{{ formatNumber(scope.row.price) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" align="center" />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="scope">
            <el-switch
              v-if="isAdmin"
              v-model="scope.row.is_active"
              @change="toggleStatus(scope.row)"
              active-text="在售"
              inactive-text="停售"
              inline-prompt
            />
            <el-tag v-else :type="scope.row.is_active ? 'success' : 'info'" size="small">
              {{ scope.row.is_active ? '在售' : '停售' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160" align="center">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column v-if="isAdmin" label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link :icon="Edit" @click="openEditDialog(scope.row)">
              编辑
            </el-button>
            <el-button type="danger" link :icon="Delete" @click="deleteProduct(scope.row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredTotal"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <ProductDialogs ref="dialogsRef" @refresh="fetchProducts" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Box, Plus, Search, RefreshRight, Edit, Delete } from '@element-plus/icons-vue'
import { formatDate, formatNumber } from '../utils/helpers'
import ProductDialogs from './products/ProductDialogs.vue'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ role: 'user' })
  }
})

const isAdmin = computed(() => props.currentUser?.role === 'admin')

const products = ref([])
const loading = ref(false)
const dialogsRef = ref(null)

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const filteredProducts = computed(() => {
  let result = products.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(product =>
      product.name?.toLowerCase().includes(query) ||
      product.description?.toLowerCase().includes(query)
    )
  }
  return result
})

const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredProducts.value.slice(start, end)
})

const filteredTotal = computed(() => filteredProducts.value.length)
const total = computed(() => products.value.length)

const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/products')
    products.value = response.data
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (product) => {
  try {
    await axios.put(`/api/products/${product.id}`, {
      is_active: product.is_active
    })
    ElMessage.success(product.is_active ? '产品已恢复销售' : '产品已停售隐藏')
  } catch (error) {
    console.error('切换状态失败:', error)
    product.is_active = !product.is_active
    ElMessage.error('切换状态失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  searchQuery.value = ''
  currentPage.value = 1
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const openAddDialog = () => {
  dialogsRef.value?.openAdd()
}

const openEditDialog = (product) => {
  dialogsRef.value?.openEdit(product)
}

const deleteProduct = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个产品吗？此操作不可恢复！', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/products/${id}`)
    ElMessage.success('产品删除成功')
    fetchProducts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除产品失败:', error)
      ElMessage.error(error.response?.data?.message || '删除产品失败')
    }
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.products-container { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-icon { font-size: 28px; color: #409eff; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 600; }
.count-tag { font-size: 14px; }
.search-card { margin-bottom: 20px; }
.search-input { width: 300px; }
.table-card { margin-bottom: 20px; }
.product-name { display: flex; align-items: center; gap: 8px; }
.product-icon { color: #409eff; font-size: 18px; }
.price-text { font-weight: 600; color: #f56c6c; }
.pagination-container { display: flex; justify-content: flex-end; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ebeef5; }
</style>
