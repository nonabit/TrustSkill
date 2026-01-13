# Skill Security Scanner

一个用于检测 Agent Skills 安全性的工具，帮助识别潜在的恶意行为和安全风险。

Agent Skills 是由 Anthropic 开发的开放标准，用于将指令、脚本和资源打包成可被 AI 代理使用的模块化能力。详见 [docs/agent-skills-format.md](docs/agent-skills-format.md) 了解 Agent Skills 的完整定义。

## 功能特性

- ✅ **命令注入检测**：识别危险的命令执行模式
- ✅ **文件系统安全**：检测危险的文件操作
- ✅ **网络安全**：发现未授权的网络请求和数据外泄
- ✅ **敏感信息保护**：检测敏感数据访问和泄露风险

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
# 扫描单个 skill
uv run python -m src.scanner <skill_path>

# 示例输出
============================================================
扫描目标: examples/malicious/data-exfiltration-skill/
============================================================

✗ 发现 9 个安全问题:
  ● 严重: 3
  ● 高: 3
  ● 中: 3

[严重] 网络安全风险
  规则: NETWORK_SECURITY
  描述: 从网络下载并执行脚本
  建议: 避免从不可信来源下载和执行代码，使用 HTTPS
```

## 项目结构

```
skill-security-scanner/
├── src/                    # 核心代码
│   ├── scanner.py         # 主扫描器
│   ├── parser.py          # SKILL.md 解析器
│   ├── types.py           # 类型定义
│   └── rules/             # 安全规则
│       ├── command_injection.py
│       ├── file_operations.py
│       ├── network_security.py
│       └── sensitive_data.py
├── examples/              # 示例 skills
│   ├── malicious/        # 恶意示例（用于演示）
│   │   ├── command-injection-skill/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   ├── data-exfiltration-skill/
│   │   └── file-deletion-skill/
│   └── safe/             # 安全示例
│       └── hello-world-skill/
│           └── SKILL.md
├── docs/                  # 文档
│   ├── README.md         # 检测规则详细说明
│   └── agent-skills-format.md  # Agent Skills 格式定义
├── CLAUDE.md              # 项目开发指南（给 Claude Code 使用）
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
