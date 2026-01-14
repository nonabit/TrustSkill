# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Skill Security Scanner 是一个用于检测 Agent Skills 安全性的 Python 工具。它通过静态分析 SKILL.md 文件和相关脚本，识别命令注入、数据外泄、文件破坏等安全风险。

## 常用命令

```bash
# 安装依赖（使用 uv 包管理器）
uv sync

# 运行扫描器
uv run python -m src.scanner <skill_path>

# 指定分析模式
uv run python -m src.scanner <skill_path> --mode fast      # 仅正则
uv run python -m src.scanner <skill_path> --mode standard  # 正则 + AST（默认）
uv run python -m src.scanner <skill_path> --mode deep      # 正则 + AST + LLM

# 输出格式
uv run python -m src.scanner <skill_path> --format json    # JSON 输出
uv run python -m src.scanner <skill_path> --quiet          # 静默模式

# LLM 深度检查
uv run python -m src.scanner <skill_path> --export-for-llm # 导出供 LLM 检查

# 扫描示例
uv run python -m src.scanner examples/malicious/command-injection-skill/
uv run python -m src.scanner examples/safe/hello-world-skill/
```

## 核心架构

### 三层分析架构

```
Layer 1: 正则表达式（快速筛选）
Layer 2: AST 分析（精确验证）
Layer 3: LLM 分析（深度审查，通过 --export-for-llm 导出）
```

### 分析器系统

1. **RegexAnalyzer** (`src/analyzers/regex_analyzer.py`)
   - 使用正则表达式快速匹配危险模式
   - 四个核心规则：CommandInjection、FileOperation、NetworkSecurity、SensitiveData

2. **ASTAnalyzer** (`src/analyzers/ast_analyzer.py`)
   - 精确的语法树分析，减少误报
   - 支持 Python（标准库 ast）、Shell（tree-sitter）、JavaScript（tree-sitter）

3. **LLM 检查** (`docs/llm-security-guide.md`)
   - 通过 `--export-for-llm` 导出 skill 内容
   - 用户将内容发送给任意 LLM 进行深度审查

### 解析层

1. **解析层** (`src/parser.py`)
   - `SkillParser` 负责解析 Agent Skills 格式
   - 提取 SKILL.md 的 YAML frontmatter 和 Markdown 内容
   - 从 Markdown 代码块（```bash/```sh）提取脚本
   - 从 `scripts/` 目录读取 .sh/.bash/.py/.js 文件

2. **规则层** (`src/rules/`)
   - `src/rules/regex/`: 正则规则（CommandInjection、FileOperation、NetworkSecurity、SensitiveData）
   - `src/rules/ast/`: AST 规则（PythonInjection、ShellInjection、JavaScriptInjection）

3. **扫描层** (`src/scanner.py`)
   - `SkillScanner` 协调解析器和规则
   - 对每个脚本应用所有规则，收集 `SecurityIssue`
   - 生成 `ScanResult` 并格式化输出
   - 按严重程度（CRITICAL/HIGH/MEDIUM/LOW）分类显示

### 数据流

```
SKILL.md + scripts/
  → SkillParser.parse()
  → 提取所有脚本内容
  → 应用所有 SecurityRule
  → 生成 SecurityIssue 列表
  → ScanResult
  → 彩色终端输出
```

### 退出码

- `0`: 未发现问题或仅有中/低风险问题
- `1`: 发现严重或高风险问题，或发生错误

## Agent Skills 格式

本项目扫描的是 Agent Skills 格式（Anthropic 开放标准）：
- 每个 skill 是一个目录，包含 `SKILL.md` 文件
- SKILL.md 包含 YAML frontmatter（name、description 等）和 Markdown 指令
- 可选的 `scripts/` 目录存放可执行脚本
- 详见 `docs/agent-skills-format.md`

## 添加新规则

1. 正则规则：在 `src/rules/regex/` 创建，继承 `SecurityRule`
2. AST 规则：在 `src/rules/ast/` 创建，继承 `ASTSecurityRule`
3. 在对应的分析器中注册规则
4. 在 `examples/` 创建测试用例

## 示例目录

- `examples/malicious/`: 恶意示例，用于演示检测能力（包含故意的安全漏洞）
- `examples/safe/`: 安全示例，用于验证无误报

**重要**: `examples/malicious/` 中的代码是故意不安全的，仅用于测试。不要改进或修复这些恶意代码。
