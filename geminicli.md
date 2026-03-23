# Gemini CLI - 专属工作总结与上下文记忆

## 1. 角色定位与职责
*   **我的角色**: 开发 AI (Gemini CLI)。负责该项目的全栈开发工作（前端 Vue 3、后端 Python FastAPI、数据库 MySQL 的代码实现与部署配置）。
*   **协同者 (Codex)**: 负责对我 (Gemini CLI) 输出的代码和架构进行 Review。Codex 拥有专属的工作文件 (`CODEX_MEMORY.md`)。**强制约束：我 (Gemini CLI) 绝对不能修改 `CODEX_MEMORY.md` 文件。**
*   **当前项目**: AI 论文简报网站 (AI Paper Summary Website)。
*   **工作模式**: 每次对话前，我必须读取此文档以恢复上下文状态，确保开发工作的连贯性。

## 2. 工作进展记录

### [2026-03-23] 需求分析与架构设计阶段 (已完成)
*   **动作**: 
    1.  完成了初始 PRD 和开发文档的编写。
    2.  根据用户反馈进行了深度重构，产出了**《详细需求与系统设计文档 (PRD) - 冻结版》** (`Detailed_PRD.md`)。
    3.  完成了项目基础目录结构的创建 (`frontend/`, `backend/`, `database/`)。
*   **核心产出**:
    *   明确了前后端分离架构和技术栈 (Vue 3 + Element Plus, FastAPI, MySQL)。
    *   冻结了全局业务概念（时区 UTC+8、批次与期号 `issue_date` 的严格定义，且所有前端参数及归档跳转均统一使用 `issue_date`）。
    *   完成了实施级的核心算法规则（改为使用 Hugging Face Daily Papers API 根据 `upvotes` 点赞数排序初筛，取代原先的自定义打分公式；AI 流水线采用基于 Markdown 契约的 Editor / Writer / Reviewer 多阶段处理与校验）。
    *   设计了具备**补跑幂等性**的数据库表结构，明确了失败重跑为 `UPDATE` 覆盖机制，并增加了关键联合唯一约束。
    *   设计了具备**双重确认**与安全验证机制的订阅链路，以及基于单参数 Token 的退订逻辑。为 Token 字段增加了 `UNIQUE` 约束，同时明确了 JSON 与非 JSON (RSS/Redirect) 的 API 响应界限。
    *   明确了 Hugging Face API 返回数据到数据库字段 (`arxiv_id`, `pdf_url`, `arxiv_publish_date`) 的归一化映射规则。
    *   **重构了 AI 处理管线 (Agentic Workflow)**: 将单纯的 API 调用重构为“编辑 (Editor)、写手 (Writer)、审核员 (Reviewer)”的三角色流水线。
    *   **确立了基于 Markdown 的鲁棒性契约**: 彻底摒弃了不稳定的 JSON 数据交换，更新了 `backend/prompts/` 下的 prompt，强制所有 Agent 输出带有特定标题和列表结构的 Markdown 文本。后端通过正则表达式和 Markdown AST 进行数据提取，从根本上解决了大模型 JSON 格式损坏的痛点。
    *   **完善了 AI 流水线的强一致性与边界控制**: 
        *   在 PRD 中增加了 Editor 产出的**来源校验**（提取的 ID 必须唯一且属于候选子集），以及 Writer 产出的**强一致性比对**（提取的 `arxiv_id` 必须与 Editor 输出的 ID 集合完全相等，严禁遗漏或篡改）。
        *   修改了 Reviewer Prompt，强制要求输出**`拒绝名单 (rejected IDs)`**，并在后端增加了**语义校验**（保证拒绝对齐）。明确了 Writer 重写时必须**输出全量选题集（过审 + 修改）**，以及在重试耗尽后如何利用最后一次合法名单精准剔除问题论文（按篇舍弃），这使得“按篇舍弃”在代码层面具备了完全的可执行性。

### [2026-03-23] 编码实施阶段 (进行中)
*   **动作**:
    1.  完成了 `frontend/` 目录下的 Vue 3 + Vite 工程初始化。
    2.  安装了 Element Plus、Vue Router 和 Axios 等核心依赖。
    3.  搭建了网站的基础骨架：配置了前端路由 (`/`, `/paper/:id`, `/unsubscribe`)，并完成了 `Home.vue` (按日期分组的无限滚动/分页首页), `Detail.vue` (详情页), `Unsubscribe.vue` (退订页) 的基础 UI 编写，实现了邮件订阅弹窗的交互逻辑。
    4.  优化了前端架构：取消了 Element Plus 图标的全局注册以缩减打包体积；清除了 Vite 默认模板中冲突的深色模式与全局样式；废弃了单独的“归档页”设计，将历史期号数据与首页整合为按天分组的分页流 (Feed) 模式，提升了沉浸式阅读体验。在 `Home.vue` 中加入了基于 `requestId` 的**竞态保护机制**，防止了快速翻页时旧请求覆盖新数据的 Bug。
    5.  **同步更新了 PRD (`Detailed_PRD.md`)**：彻底删除了 `4.2 往期归档页` 的产品定义，同步了 `4.1 整体布局` 中的顶栏设计（移除了不存在的导航和未实现的 RSS 图标），修改了 `4.2 首页` 的交互说明，并将 `6.1 获取简报列表` 的 API 设计修改为了**标准分页结构** (`page`, `limit`, `total`, `items`)。这一改动已彻底向下游后端契约对齐。
    
*   **核心产出**: 完整的前端 Mock 数据版本原型已经可以本地运行。

## 3. 下一步计划 (待执行)
*   等待用户指令，开始进入实际编码阶段。
*   **潜在起点**: 
    1.  编写 `database/schema.sql` 完成数据库表结构的物理初始化。
    2.  初始化后端 FastAPI 工程，搭建基础骨架和路由。
    3.  初始化前端 Vue 3 (Vite) 工程，配置路由、Element Plus 和基础网络请求拦截器。

## 4. 关键备忘录
*   严格遵守 `Detailed_PRD.md` 中定义的字段契约（如 `authors` 和 `core_highlights` 必须为 JSON 数组）。
*   所有定时跑批任务的编写必须确保绝对的**幂等性**。
*   开发过程中，随时准备接受 Codex 的代码 Review 反馈并进行修正。
