# SRC 目录结构大纲

本文档介绍 `src` 目录中所有文件夹的内容和用途。

---

## 目录结构概览

```
src/
├── interpolprompt/      # 提示词生成工具
├── serena/             # Serena 核心代理系统
└── solidlsp/           # 语言服务器协议（LSP）统一实现
```

---

## 1. `src/interprompt/` - 提示词生成工具

**用途**: 多语言提示词模板生成框架，支持 Jinja2 模板引擎。

### 文件说明

| 文件 | 类型 | 用途 |
|------|------|------|
| `jinja_template.py` | Python | Jinja2 模板渲染器，处理多语言提示词模板 |
| `multilang_prompt.py` | Python | 多语言提示词抽象类和接口定义 |
| `prompt_factory.py` | Python | 提示词工厂类，`PromptFactoryBase` 基类和 `autogenerate_prompt_factory_module` 自动生成函数 |
| `util/class_decorators.py` | Python | 类装饰器工具 |
| `.syncCommitId.*` | 文件 | 同步版本控制文件 |

### `util/` 子目录

- **`__init__.py`** - 工具模块初始化
- **`class_decorators.py`** - 类装饰器（单例、缓存等）

---

## 2. `src/serena/` - Serena 核心代理系统

**用途**: Serena 编码代理的核心实现，包含项目管理、工具系统、配置管理、Web 管理面板等。

### 2.1 核心模块 (`serena/` 根目录)

| 文件 | 用途 |
|------|------|
| `agent.py` | **核心代理类** - `SerenaAgent` 主协调器，管理项目、工具、用户交互、MCP 接口 |
| `agno.py` | Agno 协议相关功能 |
| `analytics.py` | 分析和统计功能 |
| `cli.py` | 命令行接口入口 |
| `code_editor.py` | 代码编辑器抽象层 |
| `constants.py` | 全局常量定义 |
| `dashboard.py` | Web 仪表板功能 |
| `gui_log_viewer.py` | GUI 日志查看器 |
| `ls_manager.py` | 语言服务器管理器 |
| `mcp.py` | MCP (Model Context Protocol) 服务器实现 |
| `project.py` | 项目管理功能 |
| `prompt_factory.py` | 提示词工厂 |
| `symbol.py` | 符号抽象表示 |
| `task_executor.py` | 任务执行器 |
| `text_utils.py` | 文本处理工具 |

### 2.2 `admin/` - Web 管理面板

**用途**: 基于 Flask 的 Web 管理界面，提供项目管理、配置管理、工具执行等功能。

#### 文件结构

| 文件/目录 | 用途 |
|----------|------|
| `start_dashboard.py` | Web 服务器启动入口 |
| `error_handlers.py` | 错误处理器 |
| `validators.py` | 输入验证器 |

#### `routes/` - 路由定义

- **`__init__.py`** - 路由模块初始化，包含所有 Web 路由定义

#### `services/` - 业务逻辑服务层

| 文件 | 用途 |
|------|------|
| `config_service.py` | 配置管理服务 |
| `monitoring_service.py` | 监控服务（日志、LSP 状态） |
| `project_service.py` | 项目管理服务 |
| `tool_executor_service.py` | 工具执行服务 |
| `tool_service.py` | 工具信息服务 |

#### `templates/` - HTML 模板

**配置相关** (`config/`):
- `overview.html` - 配置概览页面

**监控相关** (`monitoring/`):
- `logs.html` - 日志查看页面
- `lsp.html` - LSP 状态监控页面
- `overview.html` - 监控概览页面

**项目管理** (`projects/`):
- `detail.html` - 项目详情页面
- `list.html` - 项目列表页面
- `new.html` - 新建项目页面

**工具相关** (`tools/`):
- `execute.html` - 工具执行页面
- `execute_list.html` - 执行历史列表
- `list.html` - 工具列表页面
- `stats.html` - 工具统计页面

**通用模板**:
- `base.html` - 基础模板
- `error.html` - 错误页面
- `index.html` - 首页

#### `static/` - 静态资源

- `admin.css` - 管理面板样式
- `admin.js` - 管理面板脚本

### 2.3 `tools/` - 工具系统

**用途**: MCP 工具实现，提供文件操作、符号操作、内存管理、配置管理等功能。

| 文件 | 用途 |
|------|------|
| `tools_base.py` | **工具基类** - `Tool` 抽象基类，所有工具的父类 |
| `file_tools.py` | 文件系统工具 - 读取、写入、搜索、替换文件内容 |
| `symbol_tools.py` | 符号操作工具 - 查找、导航、编辑代码符号 |
| `memory_tools.py` | 内存/知识管理工具 - 项目知识持久化和检索 |
| `config_tools.py` | 配置工具 - 项目激活、模式切换 |
| `workflow_tools.py` | 工作流工具 - 入门培训、元操作 |
| `cmd_tools.py` | 命令执行工具 |
| `jetbrains_tools.py` | JetBrains IDE 集成工具 |
| `jetbrains_plugin_client.py` | JetBrains 插件客户端 |
| `jetbrains_types.py` | JetBrains 类型定义 |

**主要工具类** (来自 `symbol_tools.py`):
- `RestartLanguageServerTool` - 重启语言服务器
- `GetSymbolsOverviewTool` - 获取符号概览
- `FindSymbolTool` - 查找符号
- `FindReferencingSymbolsTool` - 查找符号引用
- `ReplaceSymbolBodyTool` - 替换符号体
- `InsertAfterSymbolTool` - 在符号后插入
- `InsertBeforeSymbolTool` - 在符号前插入
- `RenameSymbolTool` - 重命名符号

### 2.4 `config/` - 配置管理

| 文件 | 用途 |
|------|------|
| `serena_config.py` | Serena 配置类 |
| `context_mode.py` | 上下文和模式管理 |

### 2.5 `util/` - 工具函数库

| 文件 | 用途 |
|------|------|
| `class_decorators.py` | 类装饰器 |
| `cli_util.py` | CLI 工具函数 |
| `dataclass.py` | 数据类扩展 |
| `exception.py` | 异常定义 |
| `file_system.py` | 文件系统操作 |
| `git.py` | Git 操作封装 |
| `gui.py` | GUI 工具 |
| `inspection.py` | 代码检查工具 |
| `logging.py` | 日志配置 |
| `shell.py` | Shell 命令执行 |
| `thread.py` | 线程工具 |
| `version.py` | 版本信息 |
| `yaml.py` | YAML 处理 |

### 2.6 `generated/` - 自动生成代码

| 文件 | 用途 |
|------|------|
| `generated_prompt_factory.py` | 自动生成的提示词工厂 |

### 2.7 `resources/` - 资源文件

#### `config/` - 配置文件

**上下文配置** (`contexts/`):
- `agent.yml` - 代理模式上下文
- `chatgpt.yml` - ChatGPT 集成配置
- `claude-code.yml` - Claude Code 配置
- `codex.yml` - Codex 集成配置
- `desktop-app.yml` - 桌面应用上下文
- `ide.yml` - IDE 集成配置
- `oaicompat-agent.yml` - OpenAI 兼容代理配置
- `context.template.yml` - 上下文模板

**模式配置** (`modes/`):
- `editing.yml` - 编辑模式
- `interactive.yml` - 交互模式
- `no-memories.yml` - 无内存模式
- `no-onboarding.yml` - 无入门培训模式
- `one-shot.yml` - 单次执行模式
- `planning.yml` - 规划模式
- `mode.template.yml` - 模式模板

**内部模式** (`internal_modes/`):
- `jetbrains.yml` - JetBrains 插件模式

**提示词模板** (`prompt_templates/`):
- `simple_tool_outputs.yml` - 简单工具输出模板
- `system_prompt.yml` - 系统提示词模板

#### `dashboard/` - 仪表板资源

- `index.html` - 仪表板主页
- `dashboard.css` - 样式文件
- `dashboard.js` - 脚本文件
- `jquery.min.js` - jQuery 库
- `serena-icon-*.png/svg` - Serena 图标资源
- `news/20260111.html` - 新闻页面

---

## 3. `src/solidlsp/` - 语言服务器协议实现

**用途**: LSP (Language Server Protocol) 的统一封装，支持多种编程语言的语言服务器。

### 3.1 核心模块 (`solidlsp/` 根目录)

| 文件 | 用途 |
|------|------|
| `ls.py` | **核心语言服务器类** - `SolidLanguageServer` 统一接口，管理 LSP 生命周期、缓存、错误恢复 |
| `ls_config.py` | 语言服务器配置 |
| `ls_handler.py` | LSP 处理器 |
| `ls_request.py` | LSP 请求封装 |
| `ls_types.py` | LSP 类型定义 |
| `ls_utils.py` | LSP 工具函数 |
| `ls_exceptions.py` | LSP 异常定义 |
| `settings.py` | 设置管理 |

**核心类** (来自 `ls.py`):
- `SolidLanguageServer` - 主语言服务器类，提供统一的符号操作接口
- `DocumentSymbols` - 文档符号管理
- `SymbolBody` - 符号体表示
- `SymbolBodyFactory` - 符号体工厂
- `LSPFileBuffer` - 文件缓冲区
- `LanguageServerDependencyProvider` - 语言服务器依赖提供者

### 3.2 `language_servers/` - 各语言服务器实现

**用途**: 各种编程语言的 LSP 服务器适配器。

| 文件 | 支持语言 |
|------|----------|
| `jedi_server.py` | Python |
| `pyright_server.py` | Python (Pyright) |
| `gopls.py` | Go |
| `clangd_language_server.py` | C/C++ |
| `typescript_language_server.py` | TypeScript |
| `vue_language_server.py` | Vue.js |
| `rust_analyzer.py` | Rust |
| `eclipse_jdtls.py` | Java |
| `omnisharp.py` | C# |
| `intelephense.py` | PHP |
| `ruby_lsp.py` | Ruby |
| `solargraph.py` | Ruby (Solargraph) |
| `bash_language_server.py` | Bash |
| `powershell_language_server.py` | PowerShell |
| `perl_language_server.py` | Perl |
| `clojure_lsp.py` | Clojure |
| `haskell_language_server.py` | Haskell |
| `scala_language_server.py` | Scala |
| `kotlin_language_server.py` | Kotlin |
| `dart_language_server.py` | Dart |
| `lua_ls.py` | Lua |
| `elm_language_server.py` | Elm |
| `erlang_language_server.py` | Erlang |
| `fortran_language_server.py` | Fortran |
| `fsharp_language_server.py` | F# |
| `groovy_language_server.py` | Groovy |
| `julia_server.py` | Julia |
| `matlab_language_server.py` | MATLAB |
| `nixd_ls.py` | Nix |
| `pascal_server.py` | Pascal |
| `al_language_server.py` | AL (Business Central) |
| `regal_server.py` | Regal |
| `r_language_server.py` | R |
| `sourcekit_lsp.py` | Swift |
| `taplo_server.py` | TOML |
| `terraform_ls.py` | Terraform |
| `vts_language_server.py` | VTS |
| `yaml_language_server.py` | YAML |
| `zls.py` | Zig |
| `marksman.py` | Markdown |
| `csharp_language_server.py` | C# (另一种实现) |
| `common.py` | 通用工具函数 |

#### `omnisharp/` - OmniSharp 专用配置

- `initialize_params.json` - 初始化参数
- `runtime_dependencies.json` - 运行时依赖
- `workspace_did_change_configuration.json` - 工作区配置变更

#### `elixir_tools/` - Elixir 工具

- `elixir_tools.py` - Elixir 语言服务器
- `README.md` - 说明文档

### 3.3 `lsp_protocol_handler/` - LSP 协议处理

**用途**: LSP 协议的底层实现。

| 文件 | 用途 |
|------|------|
| `server.py` | LSP 服务器基类 |
| `lsp_constants.py` | LSP 常量定义 |
| `lsp_requests.py` | LSP 请求实现 |
| `lsp_types.py` | LSP 类型定义 |

### 3.4 `util/` - 工具函数

| 文件 | 用途 |
|------|------|
| `cache.py` | 缓存管理 |
| `subprocess_util.py` | 子进程工具 |
| `zip.py` | ZIP 压缩工具 |

---

## 架构总结

```
┌─────────────────────────────────────────────────────────────┐
│                        SerenaAgent                          │
│                    (核心协调器 - agent.py)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Tools     │  │   Config    │  │   Memory System     │  │
│  │  (工具系统)  │  │  (配置管理)  │  │   (知识持久化)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    SolidLanguageServer                      │
│              (语言服务器统一接口 - ls.py)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐  │
│  │  Python   │ │    Go     │ │  Rust     │ │  ... +35    │  │
│  │   (LSP)   │ │   (LSP)   │ │  (LSP)    │ │  Languages  │  │
│  └───────────┘ └───────────┘ └───────────┘ └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      Admin Dashboard                        │
│                  (Web 管理面板 - Flask)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 关键设计模式

1. **工厂模式**: `PromptFactory`, `SymbolBodyFactory`
2. **策略模式**: 多语言服务器适配器
3. **单例模式**: `SerenaAgent` 实例管理
4. **装饰器模式**: `class_decorators.py`
5. **模板方法**: `Tool` 基类

---

## 支持的编程语言（共 40+ 种）

Python, Go, Java, C/C++, C#, Rust, TypeScript, JavaScript, Vue.js, PHP, Ruby, Perl, Bash, PowerShell, Clojure, Haskell, Scala, Kotlin, Dart, Lua, Elm, Erlang, Fortran, F#, Groovy, Julia, MATLAB, Nix, Pascal, AL, Regal, Swift, Terraform, TOML, YAML, Zig, Markdown, Elixir...
