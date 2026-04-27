<template>
  <div class="import-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Upload /></el-icon>
        <h2>数据导入</h2>
      </div>
    </div>

    <!-- 导入类型选择 -->
    <el-row :gutter="20" class="import-section">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="import-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>客户数据导入</span>
            </div>
          </template>
          
          <div class="import-content">
            <p class="import-desc">支持导入客户信息，包括姓名、电话、邮箱、公司、行业等</p>
            
            <div class="template-download">
              <el-button type="text" @click="downloadTemplate('customers')">
                <el-icon><Download /></el-icon>
                下载客户导入模板
              </el-button>
            </div>
            
            <el-upload
              class="upload-area"
              drag
              action="/api/import/preview"
              :headers="uploadHeaders"
              :data="uploadData"
              :on-success="(res) => handlePreviewSuccess(res, 'customers')"
              :on-error="handleError"
              :before-upload="beforeUpload"
              accept=".xlsx,.csv"
              :show-file-list="false"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 Excel (.xlsx) 或 CSV 格式文件
                </div>
              </template>
            </el-upload>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="import-card">
          <template #header>
            <div class="card-header">
              <el-icon><Money /></el-icon>
              <span>交易数据导入</span>
            </div>
          </template>
          
          <div class="import-content">
            <p class="import-desc">支持导入交易记录，需要关联已存在的客户ID</p>
            
            <div class="template-download">
              <el-button type="text" @click="downloadTemplate('deals')">
                <el-icon><Download /></el-icon>
                下载交易导入模板
              </el-button>
            </div>
            
            <el-upload
              class="upload-area"
              drag
              action="/api/import/preview"
              :headers="uploadHeaders"
              :data="uploadData"
              :on-success="(res) => handlePreviewSuccess(res, 'deals')"
              :on-error="handleError"
              :before-upload="beforeUpload"
              accept=".xlsx,.csv"
              :show-file-list="false"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 Excel (.xlsx) 或 CSV 格式文件
                </div>
              </template>
            </el-upload>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 导入说明 -->
    <el-card shadow="hover" class="instructions-card">
      <template #header>
        <div class="card-header">
          <el-icon><InfoFilled /></el-icon>
          <span>导入说明</span>
        </div>
      </template>
      
      <div class="instructions-content">
        <h4>客户数据导入字段说明：</h4>
        <el-table :data="customerFields" border style="width: 100%" class="field-table">
          <el-table-column prop="field" label="字段名" width="150" />
          <el-table-column prop="required" label="是否必填" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.required ? 'danger' : 'info'" size="small">
                {{ scope.row.required ? '必填' : '可选' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="说明" />
        </el-table>

        <h4 style="margin-top: 20px;">交易数据导入字段说明：</h4>
        <el-table :data="dealFields" border style="width: 100%" class="field-table">
          <el-table-column prop="field" label="字段名" width="150" />
          <el-table-column prop="required" label="是否必填" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.required ? 'danger' : 'info'" size="small">
                {{ scope.row.required ? '必填' : '可选' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="说明" />
        </el-table>

        <el-alert
          title="注意事项"
          type="warning"
          :closable="false"
          style="margin-top: 20px;"
        >
          <template #default>
            <ul>
              <li>导入文件大小不能超过 10MB</li>
              <li>客户数据导入时，如果姓名和电话都相同，则视为重复数据，不会导入</li>
              <li>交易数据导入时，customer_id 必须是系统中已存在的客户ID</li>
              <li>日期格式建议使用：YYYY-MM-DD（如：2024-01-01）</li>
              <li>状态字段可选值：potential（潜在客户）、active（活跃客户）、lost（已流失客户）</li>
              <li>交易状态可选值：negotiating（谈判中）、closed（已完成）、cancelled（已取消）</li>
            </ul>
          </template>
        </el-alert>
      </div>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewType === 'customers' ? '客户数据预览' : '交易数据预览'"
      width="80%"
      destroy-on-close
    >
      <div class="preview-container">
        <p class="preview-info">共解析到 {{ previewTotal }} 条数据，以下为前5条预览：</p>
        <el-table :data="previewData" border style="width: 100%">
          <el-table-column
            v-for="col in previewColumns"
            :key="col"
            :prop="col"
            :label="col"
          />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport" :loading="importing">
          确认导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入结果对话框 -->
    <el-dialog
      v-model="resultDialogVisible"
      title="导入结果"
      width="600px"
    >
      <div class="result-content">
        <el-result
          :icon="importResult.success ? 'success' : 'warning'"
          :title="importResult.message"
        >
          <template #sub-title>
            <div v-if="importResult.errors && importResult.errors.length > 0">
              <p style="color: #f56c6c; margin-bottom: 10px;">错误详情（显示前10条）：</p>
              <ul class="error-list">
                <li v-for="(error, index) in importResult.errors" :key="index">
                  {{ error }}
                </li>
              </ul>
            </div>
          </template>
        </el-result>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, User, Money, Download, InfoFilled, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ id: 1, role: 'user' })
  }
})

// 判断是否为管理员
const isAdmin = computed(() => {
  return props.currentUser?.role === 'admin'
})

const resultDialogVisible = ref(false)
const importResult = ref({
  success: false,
  message: '',
  errors: []
})

// 预览状态
const previewDialogVisible = ref(false)
const previewType = ref('')
const previewData = ref([])
const previewColumns = ref([])
const previewTotal = ref(0)
const currentFile = ref(null)
const importing = ref(false)

// 上传请求头 - 使用token验证，无需手动设置角色
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return {
    'Authorization': token ? `Bearer ${token}` : ''
  }
})

// 上传附加数据
const uploadData = computed(() => {
  return {
    user_id: props.currentUser.id
  }
})

// 客户字段说明
const customerFields = [
  { field: 'name', required: true, description: '客户姓名' },
  { field: 'phone', required: false, description: '联系电话' },
  { field: 'email', required: false, description: '电子邮箱' },
  { field: 'company', required: false, description: '公司名称' },
  { field: 'industry', required: false, description: '所属行业' },
  { field: 'status', required: false, description: '客户状态（potential/active/lost）' }
]

// 交易字段说明
const dealFields = [
  { field: 'customer_id', required: true, description: '客户ID（系统中已存在的客户）' },
  { field: 'amount', required: true, description: '交易金额（数字）' },
  { field: 'product_name', required: false, description: '产品名称' },
  { field: 'deal_status', required: false, description: '交易状态（negotiating/closed/cancelled）' },
  { field: 'expected_close_date', required: false, description: '预期完成日期（YYYY-MM-DD）' }
]

// 上传前检查并拦截
const beforeUpload = (file) => {
  const isExcel = file.name.endsWith('.xlsx')
  const isCSV = file.name.endsWith('.csv')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isExcel && !isCSV) {
    ElMessage.error('只支持 .xlsx 或 .csv 格式文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  currentFile.value = file
  return true
}

const handlePreviewSuccess = (response, type) => {
  if (response.success) {
    previewType.value = type
    previewColumns.value = response.columns
    previewData.value = response.preview_data
    previewTotal.value = response.total_rows
    previewDialogVisible.value = true
  } else {
    ElMessage.error(response.message || '解析预览数据失败')
  }
}

const confirmImport = async () => {
  if (!currentFile.value) return
  
  importing.value = true
  const formData = new FormData()
  formData.append('file', currentFile.value)
  formData.append('user_id', props.currentUser.id)

  try {
    const url = previewType.value === 'customers' ? '/api/import/customers' : '/api/import/deals'
    const response = await axios.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    previewDialogVisible.value = false
    handleSuccess(response.data)
  } catch (error) {
    handleError(error)
  } finally {
    importing.value = false
  }
}

// 上传成功处理
const handleSuccess = (response) => {
  importResult.value = response
  resultDialogVisible.value = true
  
  if (response.success) {
    ElMessage.success(response.message)
  } else {
    ElMessage.warning(response.message)
  }
}

// 上传失败处理
const handleError = (error) => {
  let message = '导入失败'
  let errors = []
  
  if (error.response && error.response.data) {
    message = error.response.data.error || error.response.data.message || message
    errors = error.response.data.errors || []
  } else if (error.message) {
    try {
      const response = JSON.parse(error.message)
      message = response.error || message
      errors = response.errors || []
    } catch (e) {
      message = error.message
    }
  }
  
  importResult.value = {
    success: false,
    message: message,
    errors: errors
  }
  resultDialogVisible.value = true
  ElMessage.error(message)
}

// 下载模板
const downloadTemplate = async (type) => {
  try {
    const response = await axios.get(`/api/import/template/${type}`, {
      responseType: 'blob'
    })

    const blob = response.data
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = type === 'customers' ? '客户导入模板.xlsx' : '交易导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('下载模板失败: ' + error.message)
  }
}
</script>

<style scoped>
.import-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-icon {
  font-size: 32px;
  color: #409eff;
  margin-right: 12px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.import-section {
  margin-bottom: 24px;
}

.import-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.import-content {
  padding: 10px 0;
}

.import-desc {
  color: #606266;
  margin-bottom: 16px;
  line-height: 1.6;
}

.template-download {
  margin-bottom: 16px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 20px;
}

.instructions-card {
  margin-top: 24px;
}

.instructions-content h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-weight: 600;
}

.field-table {
  margin-bottom: 16px;
}

.result-content {
  padding: 20px;
}

.error-list {
  max-height: 200px;
  overflow-y: auto;
  padding-left: 20px;
  margin: 0;
}

.error-list li {
  color: #f56c6c;
  margin-bottom: 4px;
  font-size: 13px;
}

:deep(.el-alert__content ul) {
  margin: 0;
  padding-left: 20px;
}

:deep(.el-alert__content li) {
  margin-bottom: 4px;
}
</style>
