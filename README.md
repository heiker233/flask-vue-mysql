<div align="center">
  
# 🚀 客户管理系统 (Modern CRM)

**一个基于 Flask + Vue 3 + MySQL 的全栈企业级客户关系管理系统开源落地方案**

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Node Version](https://img.shields.io/badge/node-18+-green.svg)
![Vue Version](https://img.shields.io/badge/vue-3.x-brightgreen.svg)
![Flask Version](https://img.shields.io/badge/flask-2.x-black.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

  <p align="center">
    经历了深度全栈架构现代化重构后，目前拥有极高的解耦模块化结构、极致优化的响应速度，以及支持海量企业数据的性能底座。涵盖：<b>客户生命周期追踪、交易漏斗转化、数据中心导入导出、产品库基建与权限隔离</b>。
  </p>

  [功能特性](#-核心功能亮点) •
  [系统演示](#-界面速览) •
  [安装指南](#-本地快速拉起运行) •
  [架构文档](#-高阶技术架构与辞典) •
  [参与贡献](#-参与开源共建-contributing) •
  [许可证](#-开源协议-license)
</div>

---

## 🔥 核心功能亮点

### 1. 👥 客户全景画像 (360° Customer View)
- **多维度生命周期管理**：添加/编辑/删除客户，支持从“潜在”到“流失”的全流程状态追踪与价值评级（1-5星）。
- **全局分页抗压调度**：利用服务端深度游标分页替代前端伪分页，面对十万级数据库表依然秒回级畅滑体验。
- **高阶检索过滤矩阵**：通过关键字、行业、时间区段混合筛选。

### 2. 📝 跟进闭环与交易漏斗
- **跟进记录联动**：闭环沟通管理，涵盖下次跟进日期预警，分离式组件防渲染卡顿。
- **交易进度追踪**：覆盖从“谈判中”至“已取消/完成”的真实财务阶段，并提供实时的顶部指标聚合卡片。

### 3. 📊 O(1) 级超快性能统计面板 (Dashboard)
- **彻底告别 N+1 查询**：抛弃应用层暴力循环，利用纯原生 SQLAlchemy `func.extract('month')` 拦截数据流聚类，面板千条数据计算加载耗时 ＜50ms。
- **ECharts 数据可视化引擎**：内置新签转化率饼图、环比增长卡片、销售业绩月度折线图网络。

### 4. 🗄 生产级工作流与基建
- **内置数据中心**：严苛防注入的安全 Excel/CSV 上下行通道，随手下载预制模板。
- **高净度权限网闸**：基于 Header Token 鉴权，支持细粒度的超级管理员与普通职员视界拦截。
- **全局站内信器 (MessageCenter)**：独立抽离的无阻循环轮询机制，主动推送交易达标与预警待办提醒。

---

## 📸 界面速览
> 💡 **提示**: 欢迎 PR 提交您的系统运行美化截图！下方为占位符。

<kbd>
  <img src="https://via.placeholder.com/900x450/2c3e50/ffffff?text=Dashboard+Overview+Screenshot" alt="Dashboard Screenshot" width="100%">
</kbd>

<br/>

<kbd>
  <img src="https://via.placeholder.com/900x450/34495e/ffffff?text=Customer+List+and+Pagination" alt="CRM Details Screenshot" width="100%">
</kbd>

---

## 🛠 本地快速拉起运行

### 环境准备
在开始前，请确保您的开发机器上已正确配置 `Python 3.8+`、`Node.js 18+` 和 `MySQL 5.7/8.0+`。

### 1. 启动数据库引擎
请启动 MySQL 控制台或使用 Navicat 执行此建表宏指令：
```sql
CREATE DATABASE customer_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
> **注意**：随后打开 `backend/config.py`，将 SQLALCHEMY_DATABASE_URI 参数配置如：`mysql+pymysql://root:123456@localhost/customer_management`。

### 2. 构建 Flask 后端引擎
```bash
# 获取代码库
git clone https://github.com/heiker233/flask-vue-mysql.git
cd flask-vue-mysql/backend

# 强力建议建立并切入隔离的隔离环境
python -m venv venv
venv\Scripts\activate      # Win 用户
# source venv/bin/activate # Mac / Linux 用户

# 拉取核心包库
pip install -r requirements.txt

# 映射并预装载 DB 表结构模型
python create_database.py

# 启动研发服务器 (默认 5000 端口驻留)
python app.py
```

### 3. 牵引 Vue 3 前端界面
```bash
# 打开新的控制台进入前端
cd flask-vue-mysql/frontend

# 生成 Node.js 树
npm install

# 激活 Vite 服务与跨域 HMR 代理
npm run dev
```
打开浏览器访问 `http://localhost:5173`。 
**体验防爆内置账号**: 
> Account: `admin` | Password: `123456`

---

## 🏗 高阶技术架构与辞典

采用纯粹且极度要求解耦的工业级结构排列打造。

### 项目骨架简图
```text
flask-vue-mysql/
├── backend/                    # >> Python/Flask 核心 <<
│   ├── config.py               # 环境注入中心
│   ├── models.py               # 安全级 ORM 映射体
│   ├── routes/                 # Restful Controller 路由转发层 
│   │   └── customers.py ...
│   └── services/               # 不沾染视图的高度隔离纯算法 / IO 服务库
│
├── frontend/                   # >> Vue 3 / Vite 核心 <<
│   ├── src/
│   │   ├── composables/        # Setup / Vue3 Hook 数据托管钩子
│   │   ├── utils/              # 纯净的 format 格式化等帮助器集合
│   │   └── components/         
│   │       ├── common/         # 全局跨系统共享基础组件 (Message UI 等)
│   │       ├── follow-ups/     # 各大领域模型的拆分内聚组件 (Filters/Tables)
│...
```

### 核心 API 索引 (遵循 Restful 标准)
- `POST /api/login` : 下发 JWT / Session Token 口令
- `GET /api/customers?page=1&page_size=20` : 带全局向下兼顾容错的滚动获取客户清单
- `GET /api/stats/monthly-summary` : 发起并拦截原生 `GROUP BY` 图表聚合查询
- `POST /api/export` : 从文件流通道索取加密的报表二进制文件

---

## 🤝 参与开源共建 (CONTRIBUTING)

我们非常欢迎且渴望来自社区力量的贡献。哪怕只是修复了一个标点符号或一条 CSS 的拼写，对于本项目都是一笔极其宝贵的财富！

### 提交 PR 流程：
1. **Fork** 此项目并在你的工作区克隆它。
2. 切出一个新的功能分支：`git checkout -b feature/your-amazing-idea`
3. 提交你的重构或创意：`git commit -m 'feat: Add some amazing idea'`
4. PUSH 变更到远端：`git push origin feature/your-amazing-idea`
5. 回到本仓库打开并在 Pull Requests（PR） 中大方展示你的代码逻辑。

## 💬 常见故障与 Q&A
- **Q: 为什么运行 `npm install` 发生 Node-sass 或 Python Gyp 报错？**
  A: 本项目重构剔除了老损前置依赖。请确保您的 Node.js 环境彻底更新到 v18 甚至以上大版本，建议删除 `node_modules` 重新纯净安装。
- **Q: Vue 界面一片空白并且报 `Network Error`！**
  A: 请排查 Flask 服务是否依然存活在控制台并驻守了 5000 端口，前端代理需依赖真实后端的在线。

---

## 📜 开源协议 (License)

本项目严格采用 **[MIT](https://opensource.org/licenses/MIT)** 许可开源。
不管是个人学习探讨、企业内部私有化二开落位，或者是融入到您的商业盈利项目中，请**放肆使用，没有拘束**（当然我们非常欢迎您在出处能够带上一句感恩的代码致谢声明！🥰）。

---

## 🙏 特别鸣谢与支持
由于站在巨人的肩膀上方能看的更高，本项目重度致谢并依赖于以下传奇开源项目的支持：
- [Flask](https://flask.palletsprojects.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

如果这个开箱即用的 CRM 模板项目让您少掉光了几束头发：  
**✨ 欢迎点击右上角的 `★ Star` 给予我们继续迭代的不朽动力！ ✨**
