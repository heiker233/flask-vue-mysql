<template>
  <div>
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
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="newProduct.is_active" active-text="在售" inactive-text="停售" />
        </el-form-item>
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
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="editProductForm.is_active" active-text="在售" inactive-text="停售" />
        </el-form-item>
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
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['refresh'])

const saving = ref(false)
const updating = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)

const newProduct = ref({
  name: '',
  price: 0,
  unit: '件',
  description: '',
  is_active: true
})

const editProductForm = ref({
  id: null,
  name: '',
  price: 0,
  unit: '件',
  description: '',
  is_active: true
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

const saveProduct = async () => {
  if (!addFormRef.value) return

  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await axios.post('/api/products', newProduct.value)
        ElMessage.success('产品添加成功')
        emit('refresh')
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

const updateProduct = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await axios.put(`/api/products/${editProductForm.value.id}`, editProductForm.value)
        ElMessage.success('产品更新成功')
        emit('refresh')
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

const resetForm = () => {
  newProduct.value = {
    name: '',
    price: 0,
    unit: '件',
    description: '',
    is_active: true
  }
  addFormRef.value?.resetFields()
}

const openAdd = () => {
  resetForm()
  showAddDialog.value = true
}

const openEdit = (product) => {
  editProductForm.value = {
    id: product.id,
    name: product.name,
    price: product.price,
    unit: product.unit,
    description: product.description || '',
    is_active: product.is_active
  }
  showEditDialog.value = true
}

defineExpose({
  openAdd,
  openEdit
})
</script>
