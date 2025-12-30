# 客户管理系统 (Customer Management System)

一个基于 Flask + Vue3 + MySQL 的完整客户关系管理系统，包含客户、跟进、交易、统计和权限管理五大核心模块。

## 项目结构

```
project-folder/
├── backend/                # Flask 后端应用
│   ├── app.py             # Flask 应用入口
│   └── requirements.txt   # Python 依赖包
├── frontend/              # Vue3 前端应用
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── App.vue        # 根组件
│   │   ├── main.js        # 应用入口
│   │   └── style.css      # 全局样式
│   ├── index.html         # HTML 模板
│   ├── vite.config.js     # Vite 配置
│   └── package.json       # 前端依赖
└── README.md             # 项目说明
```

## 系统模块

1. **客户管理** - 管理客户信息，包括添加、编辑、删除等
2. **跟进记录** - 记录客户跟进信息和后续计划
3. **交易管理** - 管理销售交易，跟踪交易状态
4. **统计分析** - 客户和交易数据的统计分析
5. **权限管理** - 用户角色和权限控制

## 环境要求

- Python 3.8+
- Node.js 18+
- MySQL 5.7+

## 安装和运行

### 1. 配置 MySQL 数据库

```sql
CREATE DATABASE customer_management;
```

### 2. 设置虚拟环境

```bash
cd d:\python test\flask vue mysql
# 激活虚拟环境
myenv\Scripts\activate
```

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 运行后端服务

```bash
python app.py
```

### 5. 安装前端依赖

```bash
cd ../frontend
npm install
```

### 6. 运行前端服务

```bash
npm run dev
```

### 7. 访问系统

- 前端地址：http://localhost:5173
- 后端地址：http://localhost:5000

## 主要技术栈

- **后端**: Flask, Flask-SQLAlchemy, Flask-CORS, PyMySQL
- **前端**: Vue3, Element Plus, Axios, Vite
- **数据库**: MySQL

## API 接口

- `/api/customers` - 客户管理 API
- `/api/follow-ups` - 跟进记录 API
- `/api/deals` - 交易 API
- `/api/stats/customers` - 客户统计 API
- `/api/stats/deals` - 交易统计 API
- `/api/login` - 登录 API

## 数据库表结构

- `users` - 用户表
- `customers` - 客户表
- `follow_ups` - 跟进记录表
- `deals` - 交易表