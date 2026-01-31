# Serena 管理后台 Web 化设计文档

**目标:** 为 Serena 创建一个基于 Web 的管理后台，将 MCP 命令行操作迁移到可视化界面，支持项目、工具、配置和系统监控的全面管理。

**架构:** 基于现有 Flask Dashboard 扩展，采用纯服务端渲染（Jinja2 + 简单 CSS/JS），通过 YAML 配置文件实现数据持久化，双界面分离（用户仪表板 + 管理后台）。

**技术栈:** Flask 3.x、Jinja2、原生 JavaScript、YAML 配置文件

---

## 系统架构

### 整体架构

管理后台作为 Serena 现有 Flask 应用的扩展，通过 `/admin` 路径访问。架构分为三层：

1. **路由层** (`/admin/*`)：处理 HTTP 请求，验证输入，调用业务逻辑
2. **业务层**：封装现有的 MCP 工具调用，提供统一接口
3. **数据层**：读写 YAML 配置文件（复用现有 `SerenaConfig` 和 `ProjectConfig`）

关键设计原则：
- **最小侵入**：不修改现有 Dashboard 代码
- **复用优先**：现有的配置加载/保存逻辑直接调用
- **YAML 单一源**：配置文件始终是真理来源，管理后台只是编辑器

### 目录结构

```
src/serena/
├── dashboard.py          # 现有用户仪表板
├── admin/               # 🆕 管理后台模块
│   ├── __init__.py
│   ├── routes.py         # /admin/* 路由定义
│   ├── services/         # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── project_service.py
│   │   ├── tool_service.py
│   │   ├── config_service.py
│   │   └── monitoring_service.py
│   ├── templates/        # Jinja2 模板
│   │   ├── base.html
│   │   ├── projects/
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   └── new.html
│   │   ├── tools/
│   │   │   ├── list.html
│   │   │   └── stats.html
│   │   ├── config/
│   │   │   ├── overview.html
│   │   │   ├── modes.html
│   │   │   └── contexts.html
│   │   └── monitoring/
│   │       ├── overview.html
│   │       ├── lsp.html
│   │       ├── logs.html
│   │       └── tasks.html
│   └── static/           # CSS/JS 资源
│       ├── admin.css
│       └── admin.js
```

---

## 路由设计

### 项目模块 (`/admin/projects`)
- `GET /admin/projects` - 项目列表页面
- `GET /admin/projects/new` - 添加新项目页面
- `POST /admin/projects/new` - 创建新项目 API
- `GET /admin/projects/{name}` - 项目详情页面
- `POST /admin/projects/{name}/edit` - 编辑项目配置
- `POST /admin/projects/{name}/activate` - 激活项目
- `POST /admin/projects/{name}/delete` - 删除项目

### 工具模块 (`/admin/tools`)
- `GET /admin/tools` - 工具列表页面
- `POST /admin/tools/{name}/toggle` - 切换工具状态
- `GET /admin/tools/stats` - 工具使用统计页面

### 配置模块 (`/admin/config`)
- `GET /admin/config` - 全局配置查看/编辑
- `POST /admin/config/save` - 保存全局配置
- `GET /admin/config/modes` - 模式管理页面
- `GET /admin/config/contexts` - 上下文管理页面

### 系统监控模块 (`/admin/monitoring`)
- `GET /admin/monitoring` - 系统状态总览
- `GET /admin/monitoring/lsp` - LSP 服务器状态
- `GET /admin/monitoring/logs` - 日志查看器
- `GET /admin/monitoring/tasks` - 任务队列状态

---

## 页面结构设计

### 布局组件

**顶部导航栏**：
- Logo + "Serena Admin"
- 主导航：项目 | 工具 | 配置 | 监控
- 右上角：当前活跃项目显示

**侧边栏**（可选）：
- 项目列表快速切换
- 常用操作快捷方式

**主内容区**：
- 面包屑导航
- 页面标题 + 操作按钮
- 数据展示/表单区域

### 核心页面

#### 1. 项目管理页面 (`/admin/projects`)

**列表视图**：
- 表格展示所有注册项目
- 列：名称、路径、语言、状态、操作
- 操作按钮：激活、编辑、删除
- 顶部："添加新项目" 按钮

**项目详情页**：
- 项目基本信息卡片
- 语言服务器状态
- 可用工具列表
- 项目记忆列表
- 相关操作：添加/移除语言

#### 2. 工具管理页面 (`/admin/tools`)

**工具列表**：
- 按分类分组显示
- Toggle 开关切换状态
- 使用统计显示
- 点击查看详情

#### 3. 配置管理页面 (`/admin/config`)

**全局配置**：
- 分组表单编辑
- 预览 YAML 功能
- 保存配置按钮

**模式管理**：
- 模式列表卡片
- 默认模式选择

#### 4. 系统监控页面 (`/admin/monitoring`)

**总览仪表板**：
- 4 个状态卡片（LSP、内存、任务、错误）
- 实时状态指示器

**LSP 状态页**：
- 每个语言服务器的状态卡片
- 重启按钮

**日志查看器**：
- 实时日志流
- 过滤器：级别、模块、时间
- 搜索功能

---

## 数据流设计

### 配置读取流程

```
用户访问 /admin/config
    ↓
Flask 路由处理
    ↓
调用 agent.get_current_config()
    ↓
解析数据（项目、工具、模式、上下文）
    ↓
渲染 Jinja2 模板
    ↓
返回 HTML 页面
```

### 配置保存流程

```
用户提交配置表单
    ↓
POST /admin/config/save
    ↓
验证输入数据
    ↓
转换为 YAML 格式
    ↓
写入 ~/.serena/serena_config.yml
    ↓
调用 agent.serena_config.save()
    ↓
返回成功/失败响应
    ↓
前端显示 Toast 通知
```

### 状态同步机制

- **读取策略**：页面加载时从配置文件读取最新状态
- **写入策略**：修改后立即写入配置文件
- **冲突处理**：配置文件外部编辑时提示用户刷新

---

## 错误处理与安全性

### 错误处理策略

**分层错误处理**：
1. 路由层：404/400/500 错误处理
2. 业务层：配置解析、LSP 启动失败
3. 数据层：文件操作错误

**错误响应格式**：
```json
{
  "status": "error",
  "code": "PROJECT_NOT_FOUND",
  "message": "项目未找到",
  "suggestions": ["查看可用项目列表"],
  "details": "..."
}
```

### 安全性考虑

- **本地访问限制**：绑定 127.0.0.1
- **输入验证**：Pydantic 模型验证
- **路径遍历防护**：检查路径范围
- **危险操作确认**：删除/重启需二次确认

---

## 测试策略

### 测试层次

1. **单元测试**：业务逻辑层测试，Mock 外部依赖
2. **集成测试**：Flask 路由端到端测试
3. **手动测试**：功能清单、浏览器兼容性

### 测试文件结构

```
test/admin/
├── __init__.py
├── test_routes.py
├── test_services.py
├── fixtures/
│   ├── test_config.yml
│   └── test_project/
└── conftest.py
```

---

## UI/UX 设计原则

- **简单直接**：表单字段清晰，操作直观
- **即时反馈**：Toast 提示，加载状态
- **错误友好**：清晰错误消息和恢复建议
- **一致性**：统一布局和交互模式
