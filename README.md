# 客户管理系统 (Customer Management System)

一个基于 Flask + Vue3 + MySQL 的完整客户关系管理系统，包含客户管理、跟进记录、交易管理、数据统计、权限管理和数据导入六大核心模块。

## 项目概述

本系统采用前后端分离架构，前端使用 Vue 3 + Element Plus 构建用户界面，后端使用 Flask + SQLAlchemy 提供 RESTful API 服务，数据库使用 MySQL 存储数据。系统支持多用户协同办公，区分管理员和普通用户角色，满足不同企业的客户管理需求。

## 项目结构

```
flask vue mysql/
├── backend/                    # Flask 后端应用
│   ├── app.py                 # Flask 应用入口，包含所有 API 接口
│   └── requirements.txt       # Python 依赖包列表
├── frontend/                   # Vue3 前端应用
│   ├── src/
│   │   ├── components/        # Vue 组件
│   │   │   ├── App.vue        # 根组件，包含导航和布局
│   │   │   ├── Login.vue      # 登录/注册页面
│   │   │   ├── Home.vue       # 首页（统计概览、待办事项）
│   │   │   ├── Customers.vue  # 客户管理模块
│   │   │   ├── FollowUps.vue  # 跟进记录模块
│   │   │   ├── Deals.vue      # 交易管理模块
│   │   │   ├── Stats.vue      # 统计分析模块
│   │   │   ├── Users.vue      # 权限管理模块（管理员）
│   │   │   └── DataImport.vue # 数据导入模块
│   │   ├── main.js            # 应用入口
│   │   └── style.css          # 全局样式
│   ├── index.html             # HTML 模板
│   ├── vite.config.js         # Vite 配置
│   └── package.json           # 前端依赖
└── README.md                  # 项目说明
```

## 功能模块

### 1. 客户管理
- 客户信息的添加、编辑、删除
- 支持按姓名、电话、公司进行关键词搜索
- 支持按状态（潜在客户、活跃客户、已流失客户）和行业筛选
- 支持按时间范围（本月、本年、全部、自定义）查询
- 分页显示，支持设置每页显示条数

### 2. 跟进记录
- 记录与客户的沟通内容和跟进方式（电话、邮件、面谈、微信等）
- 设置下次跟进时间，便于跟踪客户动态
- 支持编辑时更换关联客户
- 支持搜索和时间范围筛选

### 3. 交易管理
- 管理销售交易信息，包括金额、产品、状态等
- 交易状态跟踪（谈判中、已完成、已取消）
- 顶部统计卡片显示总交易金额、已完成金额、谈判中金额
- 支持编辑时更换关联客户

### 4. 数据统计
- **KPI 指标卡**：新增客户数、新增交易数、成交金额、跟进次数，显示环比增长率
- **趋势图表**：客户增长趋势折线图、交易金额趋势柱状图（单位：万）
- **分布图表**：客户状态分布饼图、行业分布柱状图
- **详细报表**：月度数据统计表格，支持导出 CSV
- 支持按本月、本年、全部、自定义时间范围统计

### 5. 权限管理
- 区分管理员和普通用户角色
- 管理员可以添加、编辑、删除用户，重置用户密码
- 普通用户无法访问权限管理模块
- 后端 API 进行权限校验，防止越权访问

### 6. 数据导入
- 支持从 Excel（.xlsx、.xls）或 CSV 文件批量导入客户数据
- 支持从 Excel 或 CSV 文件批量导入交易数据
- 提供导入模板下载
- 数据验证和错误提示，显示导入成功和失败记录

### 7. 首页功能
- 欢迎区域显示当前用户和日期
- 快捷操作按钮（新增客户、添加跟进、新增交易）
- 统计卡片展示核心指标（总客户数、总交易数、完成交易金额、跟进记录数）
- 最近活动列表（最近30天），支持搜索和查看详情
- 待办事项管理（添加、编辑、删除、标记完成、设置优先级）

## 环境要求

- **Python**: 3.8+
- **Node.js**: 18+
- **MySQL**: 5.7+ 或 8.0+
- **操作系统**: Windows / Linux / macOS

## 安装和运行

### 1. 克隆项目

```bash
cd "d:\python test\flask vue mysql"
```

### 2. 配置 MySQL 数据库

创建数据库：
```sql
CREATE DATABASE customer_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改后端数据库配置（backend/app.py 第13行）：
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:密码@localhost/customer_management'
```

**注意**：请根据您的MySQL配置修改用户名和密码。

### 3. 配置后端环境

创建并激活虚拟环境（可选但推荐）：
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

安装依赖：
```bash
pip install -r requirements.txt
```

主要依赖包：
- Flask - Web 框架
- Flask-SQLAlchemy - ORM 框架
- Flask-CORS - 跨域处理
- PyMySQL - MySQL 驱动
- pandas - 数据处理（导入功能）
- openpyxl - Excel 文件处理
- werkzeug - WSGI 工具库（文件上传等）

### 4. 运行后端服务

```bash
python app.py
```

后端服务将在 http://localhost:5000 启动

### 5. 配置前端环境

```bash
cd ../frontend
npm install
```

主要依赖包：
- vue - Vue 3 框架
- element-plus - UI 组件库
- axios - HTTP 客户端
- echarts - 图表库
- @element-plus/icons-vue - 图标库

**注意**：本项目使用动态组件（`<component :is="currentComponent" />`）实现页面切换。

### 6. 运行前端服务

```bash
npm run dev
```

前端服务将在 http://localhost:5173 启动

### 7. 访问系统

打开浏览器访问：http://localhost:5173

默认管理员账号：
- 用户名：admin
- 密码：123456

系统启动时会自动创建管理员账号（如果不存在）。

## 主要技术栈

### 后端技术
| 技术 | 版本 | 说明 |
|------|------|------|
| Flask | 2.x | Python Web 框架 |
| Flask-SQLAlchemy | 3.x | ORM 框架 |
| Flask-CORS | 4.x | 跨域资源共享 |
| PyMySQL | 1.x | MySQL 数据库驱动 |
| pandas | 2.x | 数据处理和分析 |
| openpyxl | 3.x | Excel 文件读写 |

### 前端技术
| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.x | 前端框架 |
| Element Plus | 2.x | UI 组件库 |
| Axios | 1.x | HTTP 客户端 |
| Vue Router | 4.x | 路由管理 |
| ECharts | 5.x | 数据可视化图表 |
| Vite | 4.x | 构建工具 |

### 数据库
| 技术 | 版本 | 说明 |
|------|------|------|
| MySQL | 5.7+ / 8.0+ | 关系型数据库 |

## API 接口文档

### 用户认证
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/login` | POST | 用户登录 |
| `/api/register` | POST | 用户注册 |

### 客户管理
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/customers` | GET | 获取客户列表 |
| `/api/customers` | POST | 添加客户 |
| `/api/customers/<id>` | PUT | 更新客户 |
| `/api/customers/<id>` | DELETE | 删除客户 |

### 跟进记录
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/follow-ups` | GET | 获取跟进记录列表 |
| `/api/follow-ups` | POST | 添加跟进记录 |
| `/api/follow-ups/<id>` | PUT | 更新跟进记录 |
| `/api/follow-ups/<id>` | DELETE | 删除跟进记录 |

### 交易管理
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/deals` | GET | 获取交易列表 |
| `/api/deals` | POST | 添加交易 |
| `/api/deals/<id>` | PUT | 更新交易 |
| `/api/deals/<id>` | DELETE | 删除交易 |

### 数据统计
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/stats` | GET | 获取首页统计数据 |
| `/api/stats/customers` | GET | 客户统计 |
| `/api/stats/deals` | GET | 交易统计 |
| `/api/stats/kpi` | GET | KPI指标数据 |
| `/api/stats/trend` | GET | 趋势数据（客户/交易） |
| `/api/stats/comparison` | GET | 环比对比数据 |
| `/api/stats/monthly` | GET | 月度报表 |
| `/api/stats/monthly-summary` | GET | 月度汇总 |
| `/api/stats/status` | GET | 客户状态分布 |
| `/api/stats/industry` | GET | 行业分布 |
| `/api/stats/recent-customers` | GET | 最近新增客户 |
| `/api/stats/recent-follow-ups` | GET | 最近跟进记录 |

### 待办事项
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/todos` | GET | 获取待办事项列表 |
| `/api/todos` | POST | 添加待办事项 |
| `/api/todos/<id>` | PUT | 更新待办事项 |
| `/api/todos/<id>` | DELETE | 删除待办事项 |

### 数据导入
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/import/customers` | POST | 导入客户数据 |
| `/api/import/deals` | POST | 导入交易数据 |

### 用户管理（管理员）
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/users` | GET | 获取用户列表 |
| `/api/users` | POST | 添加用户 |
| `/api/users/<id>` | PUT | 更新用户 |
| `/api/users/<id>` | DELETE | 删除用户 |
| `/api/users/<id>/reset-password` | POST | 重置密码 |

## 数据库表结构

### users（用户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(50) | 用户名，唯一 |
| password | VARCHAR(100) | 密码 |
| role | VARCHAR(20) | 角色（admin/user） |
| created_at | DATETIME | 创建时间 |

### customers（客户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| name | VARCHAR(100) | 客户姓名 |
| phone | VARCHAR(20) | 联系电话 |
| email | VARCHAR(100) | 邮箱 |
| company | VARCHAR(100) | 公司名称 |
| industry | VARCHAR(50) | 所属行业 |
| status | VARCHAR(20) | 客户状态 |
| created_by | INT | 创建者ID |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### follow_ups（跟进记录表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| customer_id | INT | 客户ID（外键） |
| content | TEXT | 跟进内容 |
| follow_type | VARCHAR(50) | 跟进方式 |
| next_follow_date | DATE | 下次跟进日期 |
| created_by | INT | 创建者ID |
| created_at | DATETIME | 创建时间 |

### deals（交易表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| customer_id | INT | 客户ID（外键） |
| amount | FLOAT | 交易金额 |
| deal_status | VARCHAR(20) | 交易状态 |
| product | VARCHAR(100) | 产品名称 |
| expected_close_date | DATE | 预期完成日期 |
| actual_close_date | DATE | 实际完成日期 |
| created_by | INT | 创建者ID |
| created_at | DATETIME | 创建时间 |

### todos（待办事项表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| user_id | INT | 用户ID（外键） |
| content | VARCHAR(200) | 待办内容 |
| priority | VARCHAR(20) | 优先级 |
| completed | BOOLEAN | 是否完成 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 系统截图

（此处可以添加系统运行截图）

## 开发计划

- [x] 用户登录和权限管理
- [x] 客户管理模块
- [x] 跟进记录模块
- [x] 交易管理模块
- [x] 数据统计模块
- [x] 数据导入功能（Excel/CSV）
- [x] 数据导出功能（统计报表导出CSV）
- [x] 首页和待办事项
- [ ] 客户数据导出功能
- [ ] 交易数据导出功能
- [ ] 邮件提醒功能
- [ ] 移动端适配
- [ ] 数据权限细化（按用户隔离数据）

## 常见问题

### 1. 数据库连接失败
检查 MySQL 服务是否启动，以及数据库配置是否正确。

### 2. 前端无法访问后端
检查后端服务是否启动，以及 CORS 配置是否正确。

### 3. 中文乱码
确保数据库使用 utf8mb4 字符集，前端页面使用 UTF-8 编码。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进本项目。

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎联系项目维护者。

---

**注意**：本项目仅供学习和参考使用，生产环境使用前请进行充分测试和安全加固。
