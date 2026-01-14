# Skill Security Scanner

一个用于检测 Agent Skills 安全性的工具，帮助识别潜在的恶意行为和安全风险。

Agent Skills 是由 Anthropic 开发的开放标准，用于将指令、脚本和资源打包成可被 AI 代理使用的模块化能力。详见 [docs/agent-skills-format.md](docs/agent-skills-format.md) 了解 Agent Skills 的完整定义。

## 功能特性

- ✅ **命令注入检测**：识别危险的命令执行模式
- ✅ **文件系统安全**：检测危险的文件操作
- ✅ **网络安全**：发现未授权的网络请求和数据外泄
- ✅ **敏感信息保护**：检测敏感数据访问和泄露风险
- ✅ **多层分析**：正则表达式 + AST 分析，减少误报
- ✅ **多语言支持**：支持 Shell、Python、JavaScript 脚本分析
- ✅ **LLM 深度检查**：导出内容供 LLM 进行深度安全审查

## 安装

本项目使用 [uv](https://github.com/astral-sh/uv) 管理依赖。

```bash
# 安装依赖
uv sync
```

## 快速开始

```bash
# 扫描恶意 skill 示例
uv run python -m src.scanner examples/malicious/command-injection-skill/

# 扫描数据外泄示例
uv run python -m src.scanner examples/malicious/data-exfiltration-skill/

# 扫描安全 skill 示例
uv run python -m src.scanner examples/safe/hello-world-skill/
```

## 使用方法

```bash
# 基本用法
uv run python -m src.scanner <skill_path>

# 指定分析模式
uv run python -m src.scanner <skill_path> --mode fast      # 仅正则分析（最快）
uv run python -m src.scanner <skill_path> --mode standard  # 正则 + AST（默认）
uv run python -m src.scanner <skill_path> --mode deep      # 正则 + AST + LLM

# 输出格式
uv run python -m src.scanner <skill_path> --format json    # JSON 输出
uv run python -m src.scanner <skill_path> --quiet          # 静默模式

# 查看帮助
uv run python -m src.scanner --help
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `skill_path` | 要扫描的 skill 目录路径（必需） |
| `-m, --mode` | 分析模式: fast/standard/deep（默认 standard） |
| `--no-ast` | 禁用 AST 分析（等同于 --mode fast） |
| `-f, --format` | 输出格式: text/json（默认 text） |
| `-q, --quiet` | 静默模式，仅输出问题数量 |
| `--export-for-llm` | 导出 skill 内容供 LLM 检查 |
| `-v, --version` | 显示版本号 |

### 分析模式说明

| 模式 | 分析器 | 说明 |
|------|--------|------|
| `fast` | 正则表达式 | 最快，适合快速筛选 |
| `standard` | 正则 + AST | 默认模式，平衡速度和准确性 |
| `deep` | 正则 + AST + LLM | 使用 `--export-for-llm` 导出后手动发送给 LLM |

### LLM 深度检查

对于复杂的安全审查，可以导出 skill 内容供 LLM 分析：

```bash
# 导出 skill 内容
uv run python -m src.scanner examples/malicious/command-injection-skill/ --export-for-llm

# 将输出内容与 docs/llm-security-guide.md 中的检查提示词一起发送给 LLM
```

详见 [docs/llm-security-guide.md](docs/llm-security-guide.md)

### 示例输出

```
============================================================
扫描目标: examples/malicious/data-exfiltration-skill/
分析模式: STANDARD (RegexAnalyzer, ASTAnalyzer)
============================================================

✗ 发现 9 个安全问题:
  ● 严重: 3
  ● 高: 3
  ● 中: 3

[严重] 网络安全风险
  规则: NETWORK_SECURITY
  描述: 从网络下载并执行脚本
  建议: 避免从不可信来源下载和执行代码，使用 HTTPS

扫描耗时: 0.005 秒
```

## 项目结构

```
skill-security-scanner/
├── src/                    # 核心代码
│   ├── scanner.py         # 主扫描器
│   ├── parser.py          # SKILL.md 解析器
│   ├── types.py           # 类型定义
│   ├── analyzers/         # 分析器
│   │   ├── regex_analyzer.py   # 正则分析器
│   │   └── ast_analyzer.py     # AST 分析器
│   ├── ast_parsers/       # AST 解析器
│   │   ├── python_parser.py    # Python AST
│   │   ├── shell_parser.py     # Shell AST (tree-sitter)
│   │   └── javascript_parser.py # JavaScript AST
│   └── rules/             # 安全规则
│       ├── regex/         # 正则规则
│       └── ast/           # AST 规则
├── examples/              # 示例 skills
│   ├── malicious/        # 恶意示例（用于演示）
│   └── safe/             # 安全示例
├── docs/                  # 文档
│   ├── README.md         # 检测规则详细说明
│   ├── agent-skills-format.md  # Agent Skills 格式定义
│   └── llm-security-guide.md   # LLM 安全检查指南
├── CLAUDE.md              # 项目开发指南
└── tests/                 # 测试
```

## 检测规则

详见 [docs/README.md](docs/README.md)

## 示例

查看 `examples/` 目录了解安全和不安全的 skill 示例。所有示例都使用标准的 Agent Skills 格式（SKILL.md）。

### 恶意示例（用于演示检测能力）

- **command-injection-skill**: 演示命令注入攻击
- **data-exfiltration-skill**: 演示数据外泄（窃取 AWS 密钥、GitHub Token 等）
- **file-deletion-skill**: 演示危险的文件操作

### 安全示例

- **hello-world-skill**: 一个简单安全的示例

## Agent Skills 格式

本项目支持标准的 Agent Skills 格式。详细的格式定义请查看 [docs/agent-skills-format.md](docs/agent-skills-format.md)。

**关键特性**:
- 使用 `SKILL.md` 文件（包含 YAML frontmatter 和 Markdown 指令）
- 支持 `scripts/` 目录中的脚本文件
- 扫描 Markdown 代码块和独立脚本文件

## 许可证

MIT
