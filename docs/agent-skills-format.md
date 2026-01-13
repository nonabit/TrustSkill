# Agent Skills 格式定义

## 概述

Agent Skills 是由 Anthropic 开发并作为开放标准发布的一种格式，用于将指令、脚本和资源打包成可被 AI 代理发现和使用的模块化能力。

**官方网站**: https://agentskills.io

## 核心概念

Agent Skills 允许：
- **领域专业知识**: 将专业知识打包成可重用的指令
- **新能力**: 赋予代理新的能力（如创建演示文稿、构建 MCP 服务器、分析数据集）
- **可重复工作流**: 将多步骤任务转化为一致且可审计的工作流
- **互操作性**: 在不同的支持 skills 的代理产品中重用相同的 skill

## 支持的工具

- Claude Code
- Claude AI
- Cursor
- VS Code
- GitHub Copilot
- Gemini CLI
- 等等

## 目录结构

```
skill-name/
├── SKILL.md          # 必需：主要的 skill 定义文件
├── scripts/          # 可选：可执行代码（Python、Bash、JS 等）
├── references/       # 可选：额外的文档和参考资料
└── assets/           # 可选：模板、图片、数据文件
```

## SKILL.md 文件格式

### 1. Frontmatter（必需）

使用 YAML 格式的 frontmatter，包含元数据：

```yaml
---
name: skill-name
description: 描述 skill 的功能和使用场景（1-1024 字符）
license: Apache-2.0                    # 可选
compatibility: 需要 git, docker        # 可选：环境要求
metadata:                              # 可选：额外元数据
  author: example-org
  version: "1.0"
allowed-tools: Bash(git:*) Read        # 可选：预批准的工具（实验性）
---
```

#### 必需字段

- **name**: 1-64 字符，仅小写字母、数字和连字符，不能以连字符开头/结尾，不能有连续连字符，必须与目录名匹配
- **description**: 1-1024 字符，描述功能和使用场景，包含关键词帮助代理识别何时使用

#### 可选字段

- **license**: 许可证名称或文件引用
- **compatibility**: 1-500 字符，环境要求说明
- **metadata**: 键值对映射，存储额外元数据（如 author、version）
- **allowed-tools**: 空格分隔的预批准工具列表（实验性功能）

### 2. 主体内容（Frontmatter 之后）

使用标准 Markdown 格式编写指令，没有格式限制。推荐的章节结构：

```markdown
## 概述
简要说明 skill 的功能。

## 使用说明
1. 分步骤的指令
2. 如何执行任务
3. 预期的输入和输出

## 示例
展示具体的使用示例。

## 边缘情况
记录常见问题和处理方法。
```

### 3. 引用文件

使用相对路径从 skill 根目录引用：

```markdown
查看 [详细参考](references/REFERENCE.md) 了解更多信息。

运行脚本：
\`\`\`bash
scripts/extract.py input.pdf
\`\`\`
```

### 4. 渐进式披露

Agent Skills 使用渐进式加载策略：

- **元数据** (~100 tokens): `name` + `description` 在启动时加载
- **指令** (<5000 tokens): 激活时加载完整的 SKILL.md
- **资源**: 仅在需要时加载文件

**最佳实践**: 保持 SKILL.md 在 500 行以内，将详细内容移到 `references/` 目录。

## 完整示例

### 示例 1: Python 项目设置

```
python-project-setup/
├── SKILL.md
└── scripts/
    ├── setup_project.ps1
    ├── check_uv.py
    └── create_pyproject.py
```

**SKILL.md**:
```markdown
---
name: python-project-setup
description: 使用 uv 设置新的 Python 项目，包含虚拟环境和最佳实践。当创建新 Python 项目或帮助用户设置 Python 开发环境时使用。
---

## Python 项目设置

使用 `uv` 进行快速、可靠的包管理。

### 1. 检查并安装 uv

\`\`\`bash
python scripts/check_uv.py
\`\`\`

### 2. 快速设置

\`\`\`bash
./scripts/setup_project.ps1 -ProjectName "my-project"
\`\`\`

### 3. 手动步骤

#### 创建虚拟环境
\`\`\`bash
uv venv
\`\`\`

#### 激活虚拟环境
\`\`\`bash
source .venv/bin/activate  # Linux/Mac
.venv\\Scripts\\Activate.ps1  # Windows
\`\`\`
```

### 示例 2: 简单的 Hello World

```
hello-world/
└── SKILL.md
```

**SKILL.md**:
```markdown
---
name: hello-world
description: 一个简单的示例 skill，演示基本的问候功能。
---

## 概述

这是一个简单的 Hello World skill。

## 使用说明

1. 向用户问好
2. 显示当前时间
3. 提供友好的欢迎信息

## 示例

\`\`\`bash
echo "Hello, World!"
date
\`\`\`
```

## 安全考虑

Agent Skills 可能包含脚本，存在以下安全风险：

### 潜在威胁

1. **命令注入**: 恶意 skill 可能执行任意命令
2. **数据外泄**: 窃取环境变量、API 密钥等敏感信息
3. **文件破坏**: 删除或修改重要文件
4. **网络攻击**: 从不可信来源下载并执行代码

### 检测要点

- 检查 `scripts/` 目录中的所有脚本
- 审查 SKILL.md 中的命令示例
- 验证 `allowed-tools` 字段的权限范围
- 检查是否访问敏感环境变量
- 确认网络请求的目标地址

## 验证工具

使用官方验证工具检查 skill 格式：

```bash
skills-ref validate ./my-skill
```

## 参考资源

- **官方规范**: https://agentskills.io/specification
- **GitHub 组织**: https://github.com/agentskills
- **参考库**: https://github.com/agentskills/agentskills
- **示例 Skills**: https://github.com/anthropics/skills

## 相关标准

- **CLAUDE.md**: Claude Code 的项目级配置文件，用于自定义代理行为
- **MCP (Model Context Protocol)**: 标准化应用程序如何向 LLM 提供上下文的协议

---

**来源**:
- [Agent Skills 官方网站](https://agentskills.io)
- [Agent Skills GitHub](https://github.com/agentskills/agentskills)
- [Stefan Stranger's Blog - Agent Skills in GitHub Copilot](https://stefanstranger.github.io/2025/12/29/AgentSkillsInGithubCopilot/)
