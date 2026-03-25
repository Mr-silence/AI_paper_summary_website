# AI 论文简报 (AI Paper Summary)

为 AI 开发者提供高确定性、双语对齐、历史可追溯的每日技术简报系统。

## 项目简介

本项目从 [Hugging Face Daily Papers](https://huggingface.co/papers) 抓取 AI 领域论文，经过自动化评分筛选、AI 内容生成后，生成每日技术简报。

### 核心功能

- **每日自动抓取**: 抓取 3 天前发布的 AI 论文
- **智能评分**: 基于 8 类信号（顶尖机构、社区热度、代码可用性等）进行评分筛选
- **AI 内容生成**: 使用大语言模型生成中英文双语摘要
- **订阅邮件**: 支持邮件订阅/退订功能
- **RSS 订阅**: 提供 RSS 订阅源

### 技术栈

- **后端**: FastAPI + SQLAlchemy + MySQL
- **前端**: Vue 3 + Element Plus + Vite
- **AI**: Kimi (Moonshot) 大语言模型

## 项目结构

```
.
├── backend/           # FastAPI 后端服务
│   ├── app/
│   │   ├── api/      # API 路由
│   │   ├── core/     # 配置
│   │   ├── db/       # 数据库
│   │   ├── models/   # SQLAlchemy 模型
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # 业务逻辑
│   ├── scripts/       # 本地开发脚本
│   └── database/     # 数据库脚本
├── frontend/          # Vue 3 前端
│   └── src/
│       ├── api/      # API 调用
│       ├── components/  # 组件
│       ├── router/   # 路由
│       └── views/    # 页面视图
├── database/          # SQL 脚本
└── tests/             # 测试用例
```

## 快速启动

### 前置要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 1. 克隆项目

```bash
git clone https://github.com/Mr-silence/AI_paper_summary_website.git
cd AI_paper_summary_website
```

### 2. 后端配置

#### 2.1 创建虚拟环境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

#### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

#### 2.3 配置环境变量

创建 `backend/.env` 文件：

```env
PROJECT_NAME="AI Paper Summary API"
DATABASE_URL="mysql+pymysql://root:password@localhost:3306/ai_paper_summary"
KIMI_API_KEY="your-kimi-api-key"
KIMI_BASE_URL="https://api.moonshot.cn/v1"
KIMI_MODEL="kimi-k2.5"
KIMI_TIMEOUT_SECONDS=60
KIMI_LONGFORM_TIMEOUT_SECONDS=180
KIMI_MAX_RETRIES=3
KIMI_TITLE_BATCH_SIZE=8
PIPELINE_PROBE_DAYS=14
MYSQL_UNIX_SOCKET=""
HUGGINGFACE_API_URL="https://huggingface.co/api/daily_papers"
FRONTEND_URL="http://localhost:5173"
```

#### 2.4 初始化数据库

```bash
# 方式一：自动初始化（需要 MySQL 已安装）
python scripts/setup_local_mysql.py --password your_mysql_password
python scripts/setup_local_db.py

# 方式二：手动执行 SQL
mysql -u root -p < database/schema.sql
mysql -u root -p < database/migrate_v225.sql
```

#### 2.5 启动后端服务

```bash
uvicorn app.main:app --reload --port 8000
```

后端服务将在 http://localhost:8000 运行，API 文档见 http://localhost:8000/docs

### 3. 前端配置

#### 3.1 安装依赖

```bash
cd frontend
npm install
```

#### 3.2 启动开发服务器

```bash
npm run dev
```

前端将在 http://localhost:5173 运行

#### 3.3 生产构建

```bash
npm run build
```

构建产物输出到 `frontend/dist/` 目录

## 运行流水线

### 手动运行一次完整流水线

```bash
cd backend
python scripts/run_pipeline_once.py
```

### 检查 Kimi API 配置

```bash
cd backend
python scripts/check_kimi_api.py
```

## 测试

### 后端测试

```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 运行所有测试
pytest

# 运行特定测试
pytest tests/backend/unit/
pytest tests/backend/integration/
```

### 前端测试

```bash
cd frontend
npm run test  # 如配置了 vitest
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/papers` | GET | 获取论文列表 |
| `/api/v1/papers/{paper_id}` | GET | 获取论文详情 |
| `/api/v1/subscribe` | POST | 订阅邮件 |
| `/api/v1/subscribe/verify` | GET | 验证订阅 |
| `/api/v1/unsubscribe` | POST | 退订 |
| `/api/v1/rss` | GET | 获取 RSS 订阅源 |

详细 API 文档见 http://localhost:8000/docs

## 开发指南

### 代码规范

- 后端使用 Pydantic 进行数据验证
- 前端使用 Vue 3 Composition API
- 提交前运行 `pytest` 确保测试通过

### 数据库迁移

修改模型后，生成迁移脚本：

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 许可证

MIT License
