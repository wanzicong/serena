# Web Admin 工具调用功能设计文档

**日期**: 2025-01-31
**目的**: 为 Serena Admin Dashboard 添加工具调用能力，支持测试调试和远程操作

## 概述

在现有 Admin Dashboard 中新增"工具执行"模块，允许用户通过 Web 界面调用 Serena 的各种工具。采用简单表单模式，每个工具独立页面，参数自动解析生成表单，执行结果分区展示。

## 架构设计

### 三层架构

| 层级 | 组件 | 职责 |
|------|------|------|
| 路由层 | `routes/__init__.py` | 为每个工具添加独立路由端点 |
| 服务层 | `services/tool_executor_service.py` | 工具发现、参数解析、执行调度 |
| 视图层 | `templates/tools/` | 工具列表、执行表单、结果展示 |

### 新增文件

```
src/serena/admin/
├── routes/
│   └── __init__.py          # 添加工具执行路由
├── services/
│   └── tool_executor_service.py  # 新建：工具执行服务
├── templates/tools/
│   ├── execute_list.html    # 新建：工具列表页
│   └── execute.html         # 新建：工具执行页
└── config/
    └── tool_forms.yml       # 新建：表单定制配置
```

## 参数表单生成

### 自动生成规则

| 参数类型 | 表单控件 | 示例 |
|----------|----------|------|
| string + "path" | 文件输入框 + 浏览按钮 | `project_path` |
| boolean | 复选框 | `include_body` |
| enum/有限选项 | 下拉选择框 | `mode` |
| array | 多行文本框 | `excluded_tools` |
| 其他 | 文本输入框 | `name` |

### 定制化配置

`tool_forms.yml` 支持为特殊工具定制布局：

```yaml
find_symbol:
  layout:
    - row: [name_path_pattern, relative_path]
    - row: [depth, include_body]
  field_options:
    name_path_pattern:
      placeholder: "支持通配符，如 Foo/*"
```

## 结果展示

### 分区布局 (60:40)

**左侧 - 结果预览**：
- 成功：代码高亮 / JSON 树 / 符号表格
- 失败：错误卡片 + trace 信息

**右侧 - 执行详情**：
- 执行状态（成功/失败/超时）
- 执行耗时
- 工具名称
- 参数摘要（可折叠）
- 返回大小
- 时间戳

## 工具分类

| 分类 | 工具 |
|------|------|
| 📁 文件操作 | read_file, create_text_file, replace_content, list_dir, find_file |
| 🔍 符号操作 | find_symbol, find_referencing_symbols, get_symbols_overview, rename_symbol |
| 🧠 内存管理 | list_memories, read_memory, write_memory, edit_memory, delete_memory |
| ⚙️ 配置管理 | activate_project, switch_modes, get_current_config |
| 🔧 编辑操作 | replace_symbol_body, insert_after_symbol, insert_before_symbol |
| 📊 其他工具 | search_for_pattern, execute_shell_command |

## 路由设计

```
GET  /admin/tools/execute           # 工具列表
GET  /admin/tools/execute/{name}    # 工具执行页面
POST /admin/tools/execute/{name}    # 执行工具
```

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 参数验证失败 | 422 错误，表单上方显示具体错误 |
| 工具执行异常 | 捕获异常，显示友好错误消息 |
| 执行超时 | 30s 超时限制，显示"执行超时" |
| 未激活项目 | 提示用户先激活项目 |

## 安全策略

- Admin Dashboard 默认本地使用，无额外权限限制
- 危险工具（如 execute_shell_command）显示警告横幅
- 修改类操作建议添加二次确认（前端实现）

## 测试计划

1. **单元测试**：ToolExecutorService 参数解析和执行逻辑
2. **集成测试**：实际调用常用工具验证返回结果
3. **前端测试**：表单验证和结果渲染
4. **E2E 测试**：完整工作流测试

## 实施优先级

| 阶段 | 内容 |
|------|------|
| Phase 1 | 核心架构、工具列表、基础表单生成 |
| Phase 2 | 常用工具执行（文件类、符号类） |
| Phase 3 | 高级工具（编辑类、内存类） |
| Phase 4 | 定制化配置、历史记录、优化 |
