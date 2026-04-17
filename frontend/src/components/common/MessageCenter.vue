<template>
  <el-popover placement="bottom" :width="300" trigger="click" @show="fetchMessages">
    <template #reference>
      <el-badge :value="unreadCount" :max="99" class="msg-badge" :hidden="unreadCount === 0">
        <el-icon class="msg-icon"><Bell /></el-icon>
      </el-badge>
    </template>
    <div class="msg-container">
      <div class="msg-header">
        <span>消息通知</span>
        <el-button type="text" size="small" @click="readAllMessages" v-if="unreadCount > 0">全部已读</el-button>
      </div>
      <div class="msg-list" v-loading="loadingMessages">
        <div v-for="msg in messages" :key="msg.id" class="msg-item" :class="{ 'unread': !msg.is_read }" @click="readMessage(msg)">
          <div class="msg-title">
            <el-tag size="small" :type="getMsgTypeTag(msg.msg_type)">{{ msg.title }}</el-tag>
            <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
          </div>
          <div class="msg-content">{{ msg.content }}</div>
        </div>
        <el-empty v-if="messages.length === 0" description="暂无消息" :image-size="60" />
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'
import { Bell } from '@element-plus/icons-vue'
import axios from 'axios'
import { formatDate } from '../../utils/helpers'

const props = defineProps({
  userId: {
    type: Number,
    required: false
  }
})

const messages = ref([])
const loadingMessages = ref(false)
const unreadCount = computed(() => messages.value.filter(m => !m.is_read).length)
let messageTimer = null

const fetchMessages = async () => {
  if (!props.userId) return
  loadingMessages.value = true
  try {
    const res = await axios.get('/api/messages', { params: { user_id: props.userId } })
    messages.value = res.data
  } catch (error) {
    console.error('获取消息失败', error)
  } finally {
    loadingMessages.value = false
  }
}

const readMessage = async (msg) => {
  if (msg.is_read) return
  try {
    await axios.put(`/api/messages/${msg.id}/read`)
    msg.is_read = true
  } catch (error) {
    console.error('标记已读失败', error)
  }
}

const readAllMessages = async () => {
  if (!props.userId) return
  try {
    await axios.put('/api/messages/read_all', { user_id: props.userId })
    messages.value.forEach(m => m.is_read = true)
  } catch (error) {
    console.error('标记全部已读失败', error)
  }
}

const getMsgTypeTag = (type) => {
  const map = { 'deal': 'success', 'todo': 'danger', 'system': 'info' }
  return map[type] || 'info'
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const startPolling = () => {
  if (messageTimer) clearInterval(messageTimer)
  fetchMessages()
  messageTimer = setInterval(fetchMessages, 60000)
}

const stopPolling = () => {
  if (messageTimer) clearInterval(messageTimer)
}

watch(() => props.userId, (newVal) => {
  if (newVal) {
    startPolling()
  } else {
    stopPolling()
    messages.value = []
  }
}, { immediate: true })

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.msg-badge {
  margin-right: 15px;
  cursor: pointer;
}

.msg-icon {
  font-size: 20px;
  color: white;
}

.msg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
  margin-bottom: 10px;
  font-weight: bold;
}

.msg-list {
  max-height: 300px;
  overflow-y: auto;
}

.msg-item {
  padding: 10px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.msg-item:hover {
  background-color: #f5f7fa;
}

.msg-item.unread {
  background-color: #fdf6ec;
}

.msg-item.unread:hover {
  background-color: #faecd8;
}

.msg-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.msg-time {
  font-size: 12px;
  color: #909399;
}

.msg-content {
  font-size: 13px;
  color: #606266;
}
</style>
