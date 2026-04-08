<template>
  <div class="products-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Box /></el-icon>
        <h2>产品库管理</h2>
        <el-tag type="info" class="count-tag">共 {{ total }} 个产品</el-tag>
      </div>
      <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
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
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160" align="center">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link :icon="Edit" @click="editProduct(scope.row)">
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

    <el-dialog
      v-model="showAddDialog"
      title="添加产品"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="addFormRef"
        :model="newProduct"
        :rules="productRules"
        label-width="80px"
        status-icon
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="newProduct.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单价" prop="price">
              <el-input-number
                v-model="newProduct.price"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-select v-model="newProduct.unit" placeholder="请选择单位" style="width: 100%">
                <el-option label="件" value="件" />
                <el-option label="个" value="个" />
                <el-option label="套" value="套" />
                <el-option label="台" value="台" />
                <el-option label="箱" value="箱" />
                <el-option label="kg" value="kg" />
                <el-option label="吨" value="吨" />
                <el-option label="米" value="米" />
                <el-option label="次" value="次" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="description">
          <el-input v-model="newProduct.description" type="textarea" :rows="3" placeholder="请输入产品描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProduct" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showEditDialog"
      title="编辑产品"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editProductForm"
        :rules="productRules"
        label-width="80px"
        status-icon
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="editProductForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单价" prop="price">
              <el-input-number
                v-model="editProductForm.price"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-select v-model="editProductForm.unit" placeholder="请选择单位" style="width: 100%">
                <el-option label="件" value="件" />
                <el-option label="个" value="个" />
                <el-option label="套" value="套" />
                <el-option label="台" value="台" />
                <el-option label="箱" value="箱" />
                <el-option label="kg" value="kg" />
                <el-option label="吨" value="吨" />
                <el-option label="米" value="米" />
                <el-option label="次" value="次" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editProductForm.description" type="textarea" :rows="3" placeholder="请输入产品描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateProduct" :loading="updating">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Box, Plus, Search, RefreshRight, Edit, Delete } from '@element-plus/icons-vue'

const products = ref([])
const loading = ref(false)
const saving = ref(false)
const updating = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const newProduct = ref({
  name: '',
  price: 0,
  unit: '件',
  description: ''
})

const editProductForm = ref({
  id: null,
  name: '',
  price: 0,
  unit: '件',
  description: ''
})

const productRules = {
  name: [
    { required: true, message: '请输入产品名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在2到100个字符', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入单价', trigger: 'blur' },
    { type: 'number', min: 0, message: '单价不能为负数', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请选择单位', trigger: 'change' }
  ]
}

const formatNumber = (num) => {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

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

const saveProduct = async () => {
  if (!addFormRef.value) return

  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await axios.post('/api/products', newProduct.value)
        ElMessage.success('产品添加成功')
        fetchProducts()
        showAddDialog.value = false
        resetForm()
      } catch (error) {
        console.error('保存产品失败:', error)
        ElMessage.error(error.response?.data?.message || '保存产品失败')
      } finally {
        saving.value = false
      }
    }
  })
}

const editProduct = (product) => {
  editProductForm.value = {
    id: product.id,
    name: product.name,
    price: product.price,
    unit: product.unit,
    description: product.description || ''
  }
  showEditDialog.value = true
}

const updateProduct = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await axios.put(`/api/products/${editProductForm.value.id}`, editProductForm.value)
        ElMessage.success('产品更新成功')
        fetchProducts()
        showEditDialog.value = false
      } catch (error) {
        console.error('更新产品失败:', error)
        ElMessage.error(error.response?.data?.message || '更新产品失败')
      } finally {
        updating.value = false
      }
    }
  })
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

const resetForm = () => {
  newProduct.value = {
    name: '',
    price: 0,
    unit: '件',
    description: ''
  }
  addFormRef.value?.resetFields()
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.products-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 28px;
  color: #409eff;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.count-tag {
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

.table-card {
  margin-bottom: 20px;
}

.product-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-icon {
  color: #409eff;
  font-size: 18px;
}

.price-text {
  font-weight: 600;
  color: #f56c6c;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
