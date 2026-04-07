<template>
  <div class="customers-container">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><User /></el-icon>
        <h2>客户管理</h2>
        <el-tag type="info" class="count-tag">共 {{ total }} 位客户</el-tag>
      </div>
      <div class="header-right">
        <el-button type="warning" @click="showReminderDialog = true" :icon="Bell">
          跟进提醒
          <el-badge v-if="overdueCount > 0" :value="overdueCount" class="reminder-badge" />
        </el-button>
        <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
          添加客户
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <el-card class="search-card" shadow="never">
      <el-row :gutter="20" align="middle">
        <el-col :xs="24" :sm="24" :md="24" :lg="24">
          <div class="filter-container">
            <!-- 时间查询按钮组 -->
            <div class="time-filter-section">
              <el-button-group class="time-filter-buttons">
                <el-button 
                  :type="timeRange === 'all' ? 'primary' : 'default'" 
                  @click="setTimeRange('all')"
                >
                  <el-icon><Grid /></el-icon>
                  全部
                </el-button>
                <el-button 
                  :type="timeRange === 'month' ? 'primary' : 'default'" 
                  @click="setTimeRange('month')"
                >
                  <el-icon><Calendar /></el-icon>
                  本月
                </el-button>
                <el-button 
                  :type="timeRange === 'year' ? 'primary' : 'default'" 
                  @click="setTimeRange('year')"
                >
                  <el-icon><Calendar /></el-icon>
                  本年
                </el-button>
                <el-button 
                  :type="timeRange === 'custom' ? 'primary' : 'default'" 
                  @click="setTimeRange('custom')"
                >
                  <el-icon><Setting /></el-icon>
                  自定义
                </el-button>
              </el-button-group>
              
              <!-- 自定义日期选择器 -->
              <el-date-picker
                v-if="timeRange === 'custom'"
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                @change="handleDateRangeChange"
                class="date-range-picker"
                :unlink-panels="true"
              />
            </div>
            
            <!-- 其他筛选条件 -->
            <div class="other-filters">
              <el-input
                v-model="searchQuery"
                placeholder="搜索客户姓名、电话、公司"
                clearable
                :prefix-icon="Search"
                @input="handleSearch"
                class="search-input"
              />
              <el-select
                v-model="filterStatus"
                placeholder="筛选状态"
                clearable
                @change="handleSearch"
                class="filter-select"
              >
                <el-option label="潜在客户" value="potential" />
                <el-option label="活跃客户" value="active" />
                <el-option label="已流失客户" value="lost" />
              </el-select>
              <el-select
                v-model="filterIndustry"
                placeholder="筛选行业"
                clearable
                @change="handleSearch"
                class="filter-select"
              >
                <el-option
                  v-for="industry in industryOptions"
                  :key="industry"
                  :label="industry"
                  :value="industry"
                />
              </el-select>
              <el-select
                v-model="filterValueScore"
                placeholder="客户价值"
                clearable
                @change="handleSearch"
                class="filter-select"
              >
                <el-option label="⭐⭐⭐⭐⭐ 高价值" :value="5" />
                <el-option label="⭐⭐⭐⭐ 较高价值" :value="4" />
                <el-option label="⭐⭐⭐ 中等价值" :value="3" />
                <el-option label="⭐⭐ 较低价值" :value="2" />
                <el-option label="⭐ 低价值" :value="1" />
              </el-select>
              <el-button @click="resetFilters" :icon="RefreshRight">重置</el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 客户表格 -->
    <el-card shadow="hover" class="table-card">
      <el-table
        :data="filteredCustomers"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="姓名" min-width="100" sortable>
          <template #default="scope">
            <div class="customer-name">
              <el-avatar :size="32" :style="{ backgroundColor: getAvatarColor(scope.row.name) }">
                {{ scope.row.name.charAt(0) }}
              </el-avatar>
              <span>{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="company" label="公司" min-width="120" show-overflow-tooltip />
        <el-table-column prop="industry" label="行业" min-width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.industry" size="small" effect="plain">
              {{ scope.row.industry }}
            </el-tag>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="value_score" label="价值" width="100" align="center">
          <template #default="scope">
            <el-rate v-model="scope.row.value_score" disabled show-score text-color="#ff9900" />
          </template>
        </el-table-column>
        <el-table-column prop="cooperation_stage" label="合作阶段" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStageType(scope.row.cooperation_stage)" size="small">
              {{ getStageText(scope.row.cooperation_stage) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" min-width="120">
          <template #default="scope">
            <div class="tag-list">
              <el-tag
                v-for="tag in scope.row.tags.slice(0, 3)"
                :key="tag.id"
                :type="getTagType(tag.type)"
                size="small"
                class="customer-tag"
              >
                {{ tag.name }}
              </el-tag>
              <el-tag v-if="scope.row.tags.length > 3" size="small" type="info">+{{ scope.row.tags.length - 3 }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="next_follow_date" label="下次跟进" width="120" align="center">
          <template #default="scope">
            <el-tag v-if="isOverdue(scope.row.next_follow_date)" type="danger" size="small">
              已逾期
            </el-tag>
            <el-tag v-else-if="isToday(scope.row.next_follow_date)" type="warning" size="small">
              今天
            </el-tag>
            <span v-else-if="scope.row.next_follow_date" class="text-gray">
              {{ formatDateShort(scope.row.next_follow_date) }}
            </span>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="scope">
            <el-tag :type="getCustomerStatusType(scope.row.status)" effect="light" size="small">
              {{ getCustomerStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link :icon="View" @click="viewCustomer(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link :icon="Edit" @click="editCustomer(scope.row)">
              编辑
            </el-button>
            <el-button type="danger" link :icon="Delete" @click="deleteCustomer(scope.row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 添加客户对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加客户"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="addFormRef"
        :model="newCustomer"
        :rules="customerRules"
        label-width="100px"
        status-icon
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="newCustomer.name" placeholder="请输入客户姓名" maxlength="50" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话" prop="phone">
              <el-input 
                v-model="newCustomer.phone" 
                placeholder="请输入客户电话"
                @blur="checkDuplicate('phone', newCustomer.phone)"
              />
              <el-alert v-if="duplicateWarning.phone" :title="duplicateWarning.phone" type="warning" :closable="false" show-icon />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="newCustomer.email" 
            placeholder="请输入客户邮箱"
            @blur="checkDuplicate('email', newCustomer.email)"
          />
          <el-alert v-if="duplicateWarning.email" :title="duplicateWarning.email" type="warning" :closable="false" show-icon />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="公司" prop="company">
              <el-input v-model="newCustomer.company" placeholder="请输入客户公司" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="行业" prop="industry">
              <el-select v-model="newCustomer.industry" placeholder="请选择行业" style="width: 100%" allow-create filterable>
                <el-option
                  v-for="industry in industryOptions"
                  :key="industry"
                  :label="industry"
                  :value="industry"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户价值" prop="value_score">
              <el-rate v-model="newCustomer.value_score" show-score />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合作阶段" prop="cooperation_stage">
              <el-select v-model="newCustomer.cooperation_stage" placeholder="请选择合作阶段" style="width: 100%">
                <el-option label="初步接触" value="initial" />
                <el-option label="需求沟通" value="communication" />
                <el-option label="方案制定" value="proposal" />
                <el-option label="商务谈判" value="negotiation" />
                <el-option label="已签约" value="signed" />
                <el-option label="合作中" value="cooperating" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="客户标签" prop="tags">
          <el-select
            v-model="newCustomer.tags"
            multiple
            filterable
            allow-create
            placeholder="请选择或输入标签"
            style="width: 100%"
          >
            <el-option-group label="价值标签">
              <el-option label="高价值客户" value="高价值客户" />
              <el-option label="VIP客户" value="VIP客户" />
              <el-option label="长期合作" value="长期合作" />
            </el-option-group>
            <el-option-group label="阶段标签">
              <el-option label="新客户" value="新客户" />
              <el-option label="待跟进" value="待跟进" />
              <el-option label="重点客户" value="重点客户" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="newCustomer.status">
            <el-radio-button label="potential">潜在客户</el-radio-button>
            <el-radio-button label="active">活跃客户</el-radio-button>
            <el-radio-button label="lost">已流失</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCustomer" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑客户对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑客户"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editCustomerForm"
        :rules="customerRules"
        label-width="100px"
        status-icon
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="editCustomerForm.name" placeholder="请输入客户姓名" maxlength="50" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话" prop="phone">
              <el-input 
                v-model="editCustomerForm.phone" 
                placeholder="请输入客户电话"
                @blur="checkDuplicate('phone', editCustomerForm.phone, editCustomerForm.id)"
              />
              <el-alert v-if="duplicateWarning.phone" :title="duplicateWarning.phone" type="warning" :closable="false" show-icon />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="editCustomerForm.email" 
            placeholder="请输入客户邮箱"
            @blur="checkDuplicate('email', editCustomerForm.email, editCustomerForm.id)"
          />
          <el-alert v-if="duplicateWarning.email" :title="duplicateWarning.email" type="warning" :closable="false" show-icon />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="公司" prop="company">
              <el-input v-model="editCustomerForm.company" placeholder="请输入客户公司" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="行业" prop="industry">
              <el-select v-model="editCustomerForm.industry" placeholder="请选择行业" style="width: 100%" allow-create filterable>
                <el-option
                  v-for="industry in industryOptions"
                  :key="industry"
                  :label="industry"
                  :value="industry"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户价值" prop="value_score">
              <el-rate v-model="editCustomerForm.value_score" show-score />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合作阶段" prop="cooperation_stage">
              <el-select v-model="editCustomerForm.cooperation_stage" placeholder="请选择合作阶段" style="width: 100%">
                <el-option label="初步接触" value="initial" />
                <el-option label="需求沟通" value="communication" />
                <el-option label="方案制定" value="proposal" />
                <el-option label="商务谈判" value="negotiation" />
                <el-option label="已签约" value="signed" />
                <el-option label="合作中" value="cooperating" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="客户标签" prop="tags">
          <el-select
            v-model="editCustomerForm.tags"
            multiple
            filterable
            allow-create
            placeholder="请选择或输入标签"
            style="width: 100%"
          >
            <el-option-group label="价值标签">
              <el-option label="高价值客户" value="高价值客户" />
              <el-option label="VIP客户" value="VIP客户" />
              <el-option label="长期合作" value="长期合作" />
            </el-option-group>
            <el-option-group label="阶段标签">
              <el-option label="新客户" value="新客户" />
              <el-option label="待跟进" value="待跟进" />
              <el-option label="重点客户" value="重点客户" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="editCustomerForm.status">
            <el-radio-button label="potential">潜在客户</el-radio-button>
            <el-radio-button label="active">活跃客户</el-radio-button>
            <el-radio-button label="lost">已流失</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateCustomer" :loading="updating">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看客户详情对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="客户详情"
      width="700px"
    >
      <div v-if="currentCustomer" class="customer-detail">
        <div class="detail-header">
          <el-avatar :size="64" :style="{ backgroundColor: getAvatarColor(currentCustomer.name), fontSize: '24px' }">
            {{ currentCustomer.name.charAt(0) }}
          </el-avatar>
          <div class="detail-title">
            <h3>{{ currentCustomer.name }}</h3>
            <div class="detail-tags">
              <el-tag :type="getCustomerStatusType(currentCustomer.status)" effect="light">
                {{ getCustomerStatusText(currentCustomer.status) }}
              </el-tag>
              <el-tag :type="getStageType(currentCustomer.cooperation_stage)" effect="plain">
                {{ getStageText(currentCustomer.cooperation_stage) }}
              </el-tag>
            </div>
          </div>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="电话">{{ currentCustomer.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentCustomer.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="公司">{{ currentCustomer.company || '-' }}</el-descriptions-item>
          <el-descriptions-item label="行业">{{ currentCustomer.industry || '-' }}</el-descriptions-item>
          <el-descriptions-item label="客户价值">
            <el-rate v-model="currentCustomer.value_score" disabled show-score />
          </el-descriptions-item>
          <el-descriptions-item label="下次跟进">
            <el-tag v-if="isOverdue(currentCustomer.next_follow_date)" type="danger">已逾期</el-tag>
            <span v-else>{{ formatDate(currentCustomer.next_follow_date) || '未设置' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="标签" :span="2">
            <div class="tag-list">
              <el-tag
                v-for="tag in currentCustomer.tags"
                :key="tag.id"
                :type="getTagType(tag.type)"
                class="customer-tag"
              >
                {{ tag.name }}
              </el-tag>
              <span v-if="!currentCustomer.tags || currentCustomer.tags.length === 0" class="text-gray">暂无标签</span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentCustomer.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(currentCustomer.updated_at) }}</el-descriptions-item>
        </el-descriptions>
        <div class="detail-actions">
          <el-button type="primary" @click="showViewDialog = false; editCustomer(currentCustomer)">
            编辑客户
          </el-button>
          <el-button @click="showViewDialog = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 跟进提醒对话框 -->
    <el-dialog
      v-model="showReminderDialog"
      title="客户跟进提醒"
      width="800px"
    >
      <el-tabs v-model="reminderTab">
        <el-tab-pane label="全部提醒" name="all">
          <el-alert
            v-if="reminderStats.overdue_count > 0"
            :title="`有 ${reminderStats.overdue_count} 个客户跟进已逾期，请尽快处理！`"
            type="error"
            :closable="false"
            show-icon
            style="margin-bottom: 15px;"
          />
          <el-table :data="followUpReminders" border stripe>
            <el-table-column prop="customer_name" label="客户姓名" min-width="100" />
            <el-table-column prop="customer_company" label="公司" min-width="120" show-overflow-tooltip />
            <el-table-column prop="next_follow_date" label="下次跟进时间" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.is_overdue" type="danger" size="small">已逾期</el-tag>
                <el-tag v-else-if="scope.row.days_remaining === 0" type="warning" size="small">今天</el-tag>
                <span v-else>{{ formatDate(scope.row.next_follow_date) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="last_follow_content" label="上次跟进内容" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="goToFollowUp(scope.row.customer_id)">
                  去跟进
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="已逾期" name="overdue">
          <el-table :data="overdueReminders" border stripe>
            <el-table-column prop="customer_name" label="客户姓名" min-width="100" />
            <el-table-column prop="customer_company" label="公司" min-width="120" show-overflow-tooltip />
            <el-table-column prop="next_follow_date" label="应跟进时间" width="120">
              <template #default="scope">
                <span style="color: #f56c6c;">{{ formatDate(scope.row.next_follow_date) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="last_follow_content" label="上次跟进内容" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="goToFollowUp(scope.row.customer_id)">
                  去跟进
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="今天" name="today">
          <el-table :data="todayReminders" border stripe>
            <el-table-column prop="customer_name" label="客户姓名" min-width="100" />
            <el-table-column prop="customer_company" label="公司" min-width="120" show-overflow-tooltip />
            <el-table-column prop="customer_phone" label="电话" min-width="120" />
            <el-table-column prop="last_follow_content" label="上次跟进内容" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="goToFollowUp(scope.row.customer_id)">
                  去跟进
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Plus, Search, RefreshRight, View, Edit, Delete, Calendar, Setting, Grid, Bell } from '@element-plus/icons-vue'

const emit = defineEmits(['navigate'])

// 数据
const customers = ref([])
const loading = ref(false)
const saving = ref(false)
const updating = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const showReminderDialog = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)

// 搜索和筛选
const searchQuery = ref('')
const filterStatus = ref('')
const filterIndustry = ref('')
const filterValueScore = ref(null)

// 时间筛选
const timeRange = ref('month')
const dateRange = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 跟进提醒
const followUpReminders = ref([])
const reminderStats = ref({ total: 0, overdue_count: 0, today_count: 0 })
const reminderTab = ref('all')

// 查重警告
const duplicateWarning = ref({ phone: '', email: '' })

// 行业选项
const industryOptions = [
  'IT/互联网',
  '金融',
  '制造业',
  '教育',
  '医疗',
  '房地产',
  '零售',
  '餐饮',
  '物流',
  '其他'
]

// 表单数据
const newCustomer = ref({
  name: '',
  phone: '',
  email: '',
  company: '',
  industry: '',
  status: 'potential',
  value_score: 3,
  cooperation_stage: 'initial',
  tags: []
})

const editCustomerForm = ref({
  id: null,
  name: '',
  phone: '',
  email: '',
  company: '',
  industry: '',
  status: 'potential',
  value_score: 3,
  cooperation_stage: 'initial',
  tags: []
})

const currentCustomer = ref(null)

// 表单验证规则
const customerRules = {
  name: [
    { required: true, message: '请输入客户姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$|^\d{3,4}-\d{7,8}$|^\d{7,8}$/, message: '请输入正确的电话号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择客户状态', trigger: 'change' }
  ]
}

// 头像颜色
const avatarColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8E44AD', '#16A085']
const getAvatarColor = (name) => {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return avatarColors[Math.abs(hash) % avatarColors.length]
}

// 客户状态映射
const getCustomerStatusText = (status) => {
  const statusMap = {
    'potential': '潜在客户',
    'active': '活跃客户',
    'lost': '已流失客户'
  }
  return statusMap[status] || status
}

const getCustomerStatusType = (status) => {
  const typeMap = {
    'potential': 'warning',
    'active': 'success',
    'lost': 'info'
  }
  return typeMap[status] || 'info'
}

// 合作阶段映射
const getStageText = (stage) => {
  const stageMap = {
    'initial': '初步接触',
    'communication': '需求沟通',
    'proposal': '方案制定',
    'negotiation': '商务谈判',
    'signed': '已签约',
    'cooperating': '合作中'
  }
  return stageMap[stage] || stage
}

const getStageType = (stage) => {
  const typeMap = {
    'initial': 'info',
    'communication': 'primary',
    'proposal': 'warning',
    'negotiation': 'danger',
    'signed': 'success',
    'cooperating': 'success'
  }
  return typeMap[stage] || 'info'
}

// 标签类型映射
const getTagType = (type) => {
  const typeMap = {
    'value': 'danger',
    'stage': 'warning',
    'custom': 'info'
  }
  return typeMap[type] || 'info'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatDateShort = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

// 检查是否逾期
const isOverdue = (dateStr) => {
  if (!dateStr) return false
  const date = new Date(dateStr)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date < today
}

// 检查是否是今天
const isToday = (dateStr) => {
  if (!dateStr) return false
  const date = new Date(dateStr)
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

// 筛选后的客户列表
const filteredCustomers = computed(() => {
  let result = customers.value

  // 时间筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    endDate.setHours(23, 59, 59, 999)
    
    result = result.filter(customer => {
      const createdAt = new Date(customer.created_at)
      return createdAt >= startDate && createdAt <= endDate
    })
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(customer =>
      customer.name?.toLowerCase().includes(query) ||
      customer.phone?.includes(query) ||
      customer.company?.toLowerCase().includes(query)
    )
  }

  // 状态筛选
  if (filterStatus.value) {
    result = result.filter(customer => customer.status === filterStatus.value)
  }

  // 行业筛选
  if (filterIndustry.value) {
    result = result.filter(customer => customer.industry === filterIndustry.value)
  }

  // 客户价值筛选
  if (filterValueScore.value) {
    result = result.filter(customer => customer.value_score === filterValueScore.value)
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

const filteredTotal = computed(() => {
  let result = customers.value

  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    endDate.setHours(23, 59, 59, 999)
    
    result = result.filter(customer => {
      const createdAt = new Date(customer.created_at)
      return createdAt >= startDate && createdAt <= endDate
    })
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(customer =>
      customer.name?.toLowerCase().includes(query) ||
      customer.phone?.includes(query) ||
      customer.company?.toLowerCase().includes(query)
    )
  }

  if (filterStatus.value) {
    result = result.filter(customer => customer.status === filterStatus.value)
  }

  if (filterIndustry.value) {
    result = result.filter(customer => customer.industry === filterIndustry.value)
  }

  if (filterValueScore.value) {
    result = result.filter(customer => customer.value_score === filterValueScore.value)
  }

  return result.length
})

const total = computed(() => customers.value.length)
const overdueCount = computed(() => reminderStats.value.overdue_count)
const overdueReminders = computed(() => followUpReminders.value.filter(r => r.is_overdue))
const todayReminders = computed(() => followUpReminders.value.filter(r => r.days_remaining === 0))

// 获取客户列表
const fetchCustomers = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/customers')
    customers.value = response.data
  } catch (error) {
    console.error('获取客户失败:', error)
    ElMessage.error('获取客户列表失败')
  } finally {
    loading.value = false
  }
}

// 获取跟进提醒
const fetchFollowUpReminders = async () => {
  try {
    const response = await axios.get('/api/customers/follow-up-reminders?days=30')
    if (response.data.success) {
      followUpReminders.value = response.data.reminders
      reminderStats.value = {
        total: response.data.total,
        overdue_count: response.data.overdue_count,
        today_count: response.data.today_count
      }
    }
  } catch (error) {
    console.error('获取跟进提醒失败:', error)
  }
}

// 检查客户重复
const checkDuplicate = async (field, value, excludeId = null) => {
  if (!value) {
    duplicateWarning.value[field] = ''
    return
  }
  
  try {
    const response = await axios.post('/api/customers/check-duplicate', {
      [field]: value,
      exclude_id: excludeId
    })
    
    if (response.data.is_duplicate) {
      const customer = response.data.customer
      duplicateWarning.value[field] = `该${field === 'phone' ? '电话' : '邮箱'}已被客户 "${customer.name}" 使用`
    } else {
      duplicateWarning.value[field] = ''
    }
  } catch (error) {
    console.error('查重失败:', error)
  }
}

// 设置时间范围
const setTimeRange = (range) => {
  timeRange.value = range
  if (range === 'all') {
    dateRange.value = []
    handleSearch()
  } else if (range !== 'custom') {
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth()
    
    if (range === 'month') {
      const start = new Date(year, month, 1)
      dateRange.value = [
        start.toISOString().split('T')[0],
        now.toISOString().split('T')[0]
      ]
    } else if (range === 'year') {
      const start = new Date(year, 0, 1)
      dateRange.value = [
        start.toISOString().split('T')[0],
        now.toISOString().split('T')[0]
      ]
    }
    handleSearch()
  }
}

// 处理日期范围变化
const handleDateRangeChange = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    handleSearch()
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 重置筛选
const resetFilters = () => {
  searchQuery.value = ''
  filterStatus.value = ''
  filterIndustry.value = ''
  filterValueScore.value = null
  timeRange.value = 'month'
  setTimeRange('month')
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 保存客户
const saveCustomer = async () => {
  if (!addFormRef.value) return

  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        // 转换标签格式
        const tags = newCustomer.value.tags.map(tag => ({
          name: tag,
          type: 'custom'
        }))
        
        const data = {
          ...newCustomer.value,
          tags
        }
        
        await axios.post('/api/customers', data)
        ElMessage.success('客户添加成功')
        fetchCustomers()
        showAddDialog.value = false
        resetForm()
      } catch (error) {
        console.error('保存客户失败:', error)
        ElMessage.error(error.response?.data?.message || '保存客户失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 更新客户
const updateCustomer = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        // 转换标签格式
        const tags = editCustomerForm.value.tags.map(tag => ({
          name: tag,
          type: 'custom'
        }))
        
        const data = {
          ...editCustomerForm.value,
          tags
        }
        
        await axios.put(`/api/customers/${editCustomerForm.value.id}`, data)
        ElMessage.success('客户更新成功')
        fetchCustomers()
        showEditDialog.value = false
        resetEditForm()
      } catch (error) {
        console.error('更新客户失败:', error)
        ElMessage.error(error.response?.data?.message || '更新客户失败')
      } finally {
        updating.value = false
      }
    }
  })
}

// 删除客户
const deleteCustomer = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个客户吗？此操作不可恢复！', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/customers/${id}`)
    ElMessage.success('客户删除成功')
    fetchCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除客户失败:', error)
      ElMessage.error(error.response?.data?.message || '删除客户失败')
    }
  }
}

// 查看客户
const viewCustomer = (customer) => {
  currentCustomer.value = customer
  showViewDialog.value = true
}

// 编辑客户
const editCustomer = (customer) => {
  editCustomerForm.value = {
    id: customer.id,
    name: customer.name,
    phone: customer.phone,
    email: customer.email,
    company: customer.company,
    industry: customer.industry,
    status: customer.status,
    value_score: customer.value_score || 3,
    cooperation_stage: customer.cooperation_stage || 'initial',
    tags: customer.tags ? customer.tags.map(t => t.name) : []
  }
  duplicateWarning.value = { phone: '', email: '' }
  showEditDialog.value = true
}

// 跳转到跟进页面
const goToFollowUp = (customerId) => {
  showReminderDialog.value = false
  emit('navigate', 'follow-ups')
}

// 重置表单
const resetForm = () => {
  newCustomer.value = {
    name: '',
    phone: '',
    email: '',
    company: '',
    industry: '',
    status: 'potential',
    value_score: 3,
    cooperation_stage: 'initial',
    tags: []
  }
  duplicateWarning.value = { phone: '', email: '' }
  addFormRef.value?.resetFields()
}

const resetEditForm = () => {
  editCustomerForm.value = {
    id: null,
    name: '',
    phone: '',
    email: '',
    company: '',
    industry: '',
    status: 'potential',
    value_score: 3,
    cooperation_stage: 'initial',
    tags: []
  }
  duplicateWarning.value = { phone: '', email: '' }
  editFormRef.value?.resetFields()
}

onMounted(() => {
  fetchCustomers()
  fetchFollowUpReminders()
  // 默认选择本月
  setTimeRange('month')
})
</script>

<style scoped>
.customers-container {
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

.header-right {
  display: flex;
  gap: 10px;
}

.header-icon {
  font-size: 28px;
  color: #409eff;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.count-tag {
  font-size: 14px;
}

.reminder-badge {
  margin-left: 5px;
}

.search-card {
  margin-bottom: 20px;
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.time-filter-section {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.time-filter-buttons {
  flex-shrink: 0;
}

.date-range-picker {
  width: 280px;
}

.other-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  width: 250px;
}

.filter-select {
  width: 150px;
}

.table-card {
  margin-bottom: 20px;
}

.customer-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.customer-tag {
  margin-right: 5px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.customer-detail {
  padding: 10px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.detail-title h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
}

.detail-tags {
  display: flex;
  gap: 8px;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.text-gray {
  color: #909399;
}
</style>
