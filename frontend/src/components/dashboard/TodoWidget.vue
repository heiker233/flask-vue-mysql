<template>
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
    
    <div class="todo-list" v-loading="loading">
      <div v-for="todo in todos" :key="todo.id" class="todo-item">
        <div class="todo-left">
          <el-checkbox v-model="todo.completed" @change="$emit('change', todo)">
            <span :class="{ 'completed': todo.completed }">{{ todo.content }}</span>
          </el-checkbox>
          <div class="todo-due" v-if="todo.due_date && !todo.completed">
            <el-tag size="small" :type="getDueDateType(todo.due_date)">
              截止: {{ formatDueDate(todo.due_date) }}
            </el-tag>
          </div>
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
      <el-empty v-if="todos.length === 0" description="暂无待办事项，点击上方按钮添加" />
    </div>

    <!-- 待办事项对话框 -->
    <el-dialog
      v-model="todoDialogVisible"
      :title="isEditingTodo ? '编辑待办事项' : '新增待办事项'"
      width="500px"
      destroy-on-close
      append-to-body
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
        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker
            v-model="todoForm.due_date"
            type="datetime"
            placeholder="选择截止日期时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="todoDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTodo" :loading="savingTodo">
          确定
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { List, Plus, More } from '@element-plus/icons-vue'

const props = defineProps({
  todos: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save', 'change', 'command'])

const todoDialogVisible = ref(false)
const isEditingTodo = ref(false)
const savingTodo = ref(false)
const todoFormRef = ref(null)
const todoForm = ref({
  id: null,
  content: '',
  priority: 'medium',
  completed: false,
  due_date: ''
})

const todoRules = {
  content: [
    { required: true, message: '请输入待办事项内容', trigger: 'blur' },
    { min: 1, max: 200, message: '内容长度在1-200个字符之间', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

const unfinishedTodoCount = computed(() => {
  return props.todos.filter(todo => !todo.completed).length
})

const formatDueDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}-${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const getDueDateType = (dateStr) => {
  if (!dateStr) return 'info'
  const diff = new Date(dateStr).getTime() - new Date().getTime()
  if (diff < 0) return 'danger' // 已过期
  if (diff < 86400000) return 'warning' // 24小时内到期
  return 'success'
}

const getPriorityType = (priority) => {
  const types = { high: 'danger', medium: 'warning', low: 'info' }
  return types[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const labels = { high: '高', medium: '中', low: '低' }
  return labels[priority] || '低'
}

const showAddTodoDialog = () => {
  isEditingTodo.value = false
  todoForm.value = {
    id: null,
    content: '',
    priority: 'medium',
    completed: false,
    due_date: ''
  }
  todoDialogVisible.value = true
}

const handleTodoCommand = (cmd, todo) => {
  emit('command', cmd, todo, (t) => {
    isEditingTodo.value = true
    todoForm.value = { ...t }
    todoDialogVisible.value = true
  })
}

const saveTodo = async () => {
  if (!todoFormRef.value) return
  await todoFormRef.value.validate(async (valid) => {
    if (valid) {
      savingTodo.value = true
      emit('save', todoForm.value, isEditingTodo.value, (success) => {
        savingTodo.value = false
        if (success) todoDialogVisible.value = false
      })
    }
  })
}
</script>

<style scoped>
.content-card { border-radius: 12px; height: 100%; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; }
.todo-list { max-height: 300px; overflow-y: auto; }
.todo-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #ebeef5; }
.todo-item .completed { text-decoration: line-through; color: #909399; }
.todo-left { display: flex; flex-direction: column; gap: 4px; }
.todo-due { margin-left: 24px; }
.todo-right { display: flex; align-items: center; gap: 8px; }
</style>
