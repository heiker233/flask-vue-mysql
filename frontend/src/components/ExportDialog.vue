<template>
  <el-dialog
    v-model="visible"
    title="数据导出"
    width="600px"
    destroy-on-close
  >
    <el-form :model="exportForm" label-width="100px">
      <!-- 导出格式选择 -->
      <el-form-item label="导出格式">
        <el-radio-group v-model="exportForm.format">
          <el-radio-button label="csv">
            <el-icon><Document /></el-icon> CSV
          </el-radio-button>
          <el-radio-button label="excel">
            <el-icon><DocumentChecked /></el-icon> Excel
          </el-radio-button>
          <el-radio-button label="json">
            <el-icon><DocumentCopy /></el-icon> JSON
          </el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- 数据范围选择 -->
      <el-form-item label="数据范围">
        <el-radio-group v-model="exportForm.range">
          <el-radio label="all">全部数据</el-radio>
          <el-radio label="filtered">当前筛选结果</el-radio>
          <el-radio label="selected">选中数据</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 字段选择 -->
      <el-form-item label="导出字段">
        <div class="field-selection">
          <div class="field-actions">
            <el-button type="primary" link size="small" @click="selectAllFields">
              全选
            </el-button>
            <el-button type="primary" link size="small" @click="clearAllFields">
              清空
            </el-button>
            <el-button type="primary" link size="small" @click="selectDefaultFields">
              默认字段
            </el-button>
          </div>
          <el-checkbox-group v-model="exportForm.fields" class="field-checkbox-group">
            <el-row :gutter="10">
              <el-col :span="8" v-for="field in availableFields" :key="field.key">
                <el-checkbox :label="field.key">
                  {{ field.label }}
                  <el-tooltip v-if="field.description" :content="field.description">
                    <el-icon><InfoFilled /></el-icon>
                  </el-tooltip>
                </el-checkbox>
              </el-col>
            </el-row>
          </el-checkbox-group>
        </div>
      </el-form-item>

      <!-- 高级选项 -->
      <el-form-item>
        <template #label>
          <span>高级选项</span>
          <el-tooltip content="展开更多导出选项">
            <el-icon style="margin-left: 4px;"><InfoFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-collapse v-model="activeCollapse">
          <el-collapse-item name="advanced">
            <el-form-item label="文件名">
              <el-input 
                v-model="exportForm.filename" 
                placeholder="请输入文件名（不含扩展名）"
                :suffix-icon="Document"
              />
            </el-form-item>
            <el-form-item label="编码格式" v-if="exportForm.format === 'csv'">
              <el-select v-model="exportForm.encoding" style="width: 100%">
                <el-option label="UTF-8 (推荐)" value="utf-8" />
                <el-option label="GBK (兼容Excel中文)" value="gbk" />
              </el-select>
            </el-form-item>
            <el-form-item label="包含表头">
              <el-switch v-model="exportForm.includeHeader" active-text="是" inactive-text="否" />
            </el-form-item>
            <el-form-item label="日期格式">
              <el-select v-model="exportForm.dateFormat" style="width: 100%">
                <el-option label="YYYY-MM-DD HH:mm:ss" value="YYYY-MM-DD HH:mm:ss" />
                <el-option label="YYYY-MM-DD" value="YYYY-MM-DD" />
                <el-option label="YYYY/MM/DD" value="YYYY/MM/DD" />
                <el-option label="DD/MM/YYYY" value="DD/MM/YYYY" />
              </el-select>
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
      </el-form-item>

      <!-- 导出预览 -->
      <el-form-item label="导出预览">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="数据条数">{{ previewData.count }} 条</el-descriptions-item>
          <el-descriptions-item label="字段数量">{{ exportForm.fields.length }} 个</el-descriptions-item>
          <el-descriptions-item label="文件格式">{{ formatLabel }}</el-descriptions-item>
          <el-descriptions-item label="预计大小">{{ previewData.size }}</el-descriptions-item>
        </el-descriptions>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleExport" :loading="exporting">
        <el-icon><Download /></el-icon>
        确认导出
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, DocumentChecked, DocumentCopy, Download, InfoFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '数据导出'
  },
  // 可用的字段列表
  fields: {
    type: Array,
    default: () => []
  },
  // 默认选中的字段
  defaultFields: {
    type: Array,
    default: () => []
  },
  // 数据类型（用于后端API）
  dataType: {
    type: String,
    required: true
  },
  // 当前筛选条件
  filters: {
    type: Object,
    default: () => ({})
  },
  // 选中的数据ID列表
  selectedIds: {
    type: Array,
    default: () => []
  },
  // 数据总数
  totalCount: {
    type: Number,
    default: 0
  },
  // 筛选后的数据数
  filteredCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue', 'export-success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const exporting = ref(false)
const activeCollapse = ref([])

// 导出表单
const exportForm = ref({
  format: 'excel',
  range: 'filtered',
  fields: [],
  filename: '',
  encoding: 'utf-8',
  includeHeader: true,
  dateFormat: 'YYYY-MM-DD HH:mm:ss'
})

// 可用字段（包含默认选中状态）
const availableFields = computed(() => {
  return props.fields.map(field => ({
    ...field,
    selected: props.defaultFields.includes(field.key)
  }))
})

// 格式标签
const formatLabel = computed(() => {
  const labels = {
    'csv': 'CSV 文本文件',
    'excel': 'Excel 工作表',
    'json': 'JSON 数据文件'
  }
  return labels[exportForm.value.format] || exportForm.value.format
})

// 预览数据
const previewData = computed(() => {
  let count = 0
  switch (exportForm.value.range) {
    case 'all':
      count = props.totalCount
      break
    case 'filtered':
      count = props.filteredCount
      break
    case 'selected':
      count = props.selectedIds.length
      break
  }
  
  // 估算文件大小（粗略计算）
  const avgRowSize = exportForm.value.fields.length * 50 // 假设每个字段50字节
  const totalSize = count * avgRowSize
  let sizeStr = ''
  if (totalSize < 1024) {
    sizeStr = totalSize + ' B'
  } else if (totalSize < 1024 * 1024) {
    sizeStr = (totalSize / 1024).toFixed(2) + ' KB'
  } else {
    sizeStr = (totalSize / 1024 / 1024).toFixed(2) + ' MB'
  }
  
  return { count, size: sizeStr }
})

// 监听对话框打开，初始化默认值
watch(() => props.modelValue, (val) => {
  if (val) {
    // 设置默认文件名
    const date = new Date().toISOString().split('T')[0]
    exportForm.value.filename = `${props.dataType}_导出_${date}`
    // 设置默认字段
    exportForm.value.fields = [...props.defaultFields]
  }
})

// 全选字段
const selectAllFields = () => {
  exportForm.value.fields = props.fields.map(f => f.key)
}

// 清空字段
const clearAllFields = () => {
  exportForm.value.fields = []
}

// 选择默认字段
const selectDefaultFields = () => {
  exportForm.value.fields = [...props.defaultFields]
}

// 处理导出
const handleExport = async () => {
  if (exportForm.value.fields.length === 0) {
    ElMessage.warning('请至少选择一个导出字段')
    return
  }
  
  if (previewData.value.count === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  exporting.value = true
  
  try {
    // 构建请求参数
    const params = {
      data_type: props.dataType,
      format: exportForm.value.format,
      range: exportForm.value.range,
      fields: exportForm.value.fields,
      filename: exportForm.value.filename,
      encoding: exportForm.value.encoding,
      include_header: exportForm.value.includeHeader,
      date_format: exportForm.value.dateFormat
    }
    
    // 添加筛选条件或选中ID
    if (exportForm.value.range === 'filtered') {
      params.filters = props.filters
    } else if (exportForm.value.range === 'selected') {
      params.selected_ids = props.selectedIds
    }
    
    // 发送导出请求
    const response = await axios.post('/api/export', params, {
      responseType: 'blob'
    })
    
    // 获取文件扩展名
    const extMap = { 'csv': 'csv', 'excel': 'xlsx', 'json': 'json' }
    const ext = extMap[exportForm.value.format]
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: exportForm.value.format === 'csv' ? 'text/csv;charset=utf-8;' : 
            exportForm.value.format === 'excel' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' :
            'application/json'
    })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${exportForm.value.filename}.${ext}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('数据导出成功')
    emit('export-success')
    visible.value = false
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('数据导出失败，请重试')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.field-selection {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
}

.field-actions {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.field-checkbox-group {
  max-height: 200px;
  overflow-y: auto;
}

.field-checkbox-group :deep(.el-checkbox) {
  margin-right: 0;
  margin-bottom: 8px;
  width: 100%;
}

:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item__header) {
  border: none;
  font-weight: normal;
  color: #606266;
}

:deep(.el-collapse-item__wrap) {
  border: none;
}

:deep(.el-collapse-item__content) {
  padding-bottom: 0;
}
</style>
