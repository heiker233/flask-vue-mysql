/**
 * 前端通用工具函数库
 * 统一管理跨组件的重复工具函数，避免各文件中重复定义
 */

// 头像颜色池
const avatarColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8E44AD', '#16A085']

/**
 * 根据姓名字符串生成固定的头像背景色（哈希算法）
 * @param {string} name
 * @returns {string} hex 颜色值
 */
const padNumber = (value) => String(value).padStart(2, '0')

export const getAvatarColor = (name) => {
  if (!name) return '#409EFF'
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return avatarColors[Math.abs(hash) % avatarColors.length]
}

/**
 * 格式化日期时间字符串（UTC → 北京时间 +8h）
 * @param {string} dateStr ISO 格式的日期字符串
 * @returns {string} 格式化后的日期时间字符串，如 "2024-01-01 14:30"
 */
export const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const localDate = new Date(date.getTime() + 8 * 60 * 60 * 1000)
  return localDate.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 仅格式化日期部分（不含时间）
 * @param {string} dateStr
 * @returns {string} 如 "2024-01-01"
 */
export const formatDateOnly = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const localDate = new Date(date.getTime() + 8 * 60 * 60 * 1000)
  return localDate.toLocaleDateString('zh-CN')
}

/**
 * 鐢熸垚鏈湴鏃ユ湡杈撳叆瀛楃涓诧紙YYYY-MM-DD锛夛紝閬垮厤 UTC 杞崲瀵艰嚧鏃ユ湡鍋忕Щ
 * @param {Date|string|number} input
 * @returns {string}
 */
export const formatLocalDateInput = (input = new Date()) => {
  const date = input instanceof Date ? input : new Date(input)
  if (Number.isNaN(date.getTime())) return ''

  return [
    date.getFullYear(),
    padNumber(date.getMonth() + 1),
    padNumber(date.getDate())
  ].join('-')
}

/**
 * 格式化金额数字（保留两位小数，千分位分隔）
 * @param {number} num
 * @returns {string} 如 "1,234.56"
 */
export const formatNumber = (num) => {
  if (typeof num !== 'number') return '0.00'
  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}
