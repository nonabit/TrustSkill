# TrustSkill 交互式 CLI 增强设计

## 概述

提升 TrustSkill 的终端用户体验，使扫描过程更直观、输出更专业。

## 目标

1. 实时扫描进度显示
2. 美观的终端报告（Rust/Cargo 风格）
3. LLM 友好的结构化输出（JSON + Markdown）

## 功能设计

### 功能一：实时扫描进度

**显示内容：**
- 进度条（百分比 + 可视化条）
- 当前扫描文件名
- 已发现问题数量

**示例效果：**
```
扫描中 ━━━━━━━━━━━━━━━━━━━━ 60% scripts/deploy.sh
已发现 3 个问题
```

**实现方式：**
- 使用 Rich 的 `Progress` 组件
- 扫描器回调机制，每处理一个文件更新进度

### 功能二：终端美化报告

采用 Rust/Cargo 编译器风格，专业且清晰。

**示例效果：**
```
critical[python-injection]: 命令注入风险
  --> scripts/run.py:15:1
   |
14 |     user_input = sys.argv[1]
15 |     eval(user_input)
   |     ^^^^^^^^^^^^^^^^ eval() 执行用户输入
16 |     print("done")
   |

warning[network-security]: 网络安全风险
  --> scripts/install.sh:8:1
   |
 8 |     curl -sSL $URL | bash
   |     ^^^^^^^^^^^^^^^^^^^^ 使用 curl 下载并执行脚本
   |
```

**风格约定：**
- `critical` - 严重风险（红色）
- `warning` - 高/中风险（黄色）
- `note` - 低风险（蓝色）
- 使用 `-->` 指向文件位置
- 使用 `^^^` 下划线高亮问题代码
- 显示问题代码的上下文（前后各 1-2 行）

### 功能三：LLM 友好的结构化输出

**JSON 格式**（`--format json`）：
```json
{
  "version": "0.2.0",
  "skill_path": "my-skill/",
  "scan_time": "2026-01-15T02:45:00Z",
  "mode": "standard",
  "summary": {
    "total": 3,
    "critical": 1,
    "high": 0,
    "medium": 2,
    "low": 0
  },
  "issues": [
    {
      "id": "python-injection",
      "severity": "critical",
      "file": "scripts/run.py",
      "line": 15,
      "column": 1,
      "title": "命令注入风险",
      "description": "eval() 执行用户输入",
      "code_snippet": {
        "start_line": 14,
        "lines": [
          "user_input = sys.argv[1]",
          "eval(user_input)",
          "print(\"done\")"
        ],
        "highlight_line": 15
      },
      "rule": "PythonInjection",
      "analyzer": "ast"
    }
  ]
}
```

**Markdown 格式**（`--format markdown`）：
```markdown
# TrustSkill 扫描报告

**Skill**: my-skill/
**扫描时间**: 2026-01-15 02:45:00
**分析模式**: standard

## 摘要

| 级别 | 数量 |
|------|------|
| CRITICAL | 1 |
| HIGH | 0 |
| MEDIUM | 2 |

## 问题详情

### [CRITICAL] python-injection

**文件**: scripts/run.py:15
**描述**: 命令注入风险 - eval() 执行用户输入

```python
# scripts/run.py:14-16
user_input = sys.argv[1]
eval(user_input)  # <-- 问题行
print("done")
```

**建议**: 避免使用 eval()，改用安全的替代方案如 ast.literal_eval()
```

**命令行参数：**
- `--format json` - 输出 JSON
- `--format markdown` - 输出 Markdown
- `--format rich` - 终端美化输出（默认）

## 技术实现

### 新增依赖

```toml
[project.dependencies]
rich = ">=13.0.0"
```

### 代码结构

```
src/
├── scanner.py              # 添加进度回调支持
├── formatters/             # 新建格式化模块
│   ├── __init__.py
│   ├── base.py            # 格式化器基类
│   ├── rich_formatter.py  # Rich 终端格式化
│   ├── json_formatter.py  # JSON 格式化
│   └── markdown_formatter.py  # Markdown 格式化
└── types.py               # 添加 code_snippet 字段到 SecurityIssue
```

### 实现步骤

1. 添加 `rich` 依赖到 pyproject.toml
2. 扩展 `SecurityIssue` 类型，添加 `code_snippet` 字段
3. 修改 `SkillScanner`，添加进度回调机制
4. 创建 `formatters/` 模块，实现三种格式化器
5. 更新 CLI 参数，支持 `--format` 选项
6. 更新现有测试和示例

## 后续扩展

完成本次 CLI 增强后，可考虑：
- Web 界面（基于结构化输出）
- 接入第三方 skill 信息站点
- IDE 插件集成
