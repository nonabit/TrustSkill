# Skill Security Scanner 重构开发计划

## 项目目标

将 Skill Security Scanner 从单纯的正则表达式分析升级为支持 AST 和 LLM 的多层分析架构。

## 总体架构

```
三层分析架构：
Layer 1: 正则表达式（快速筛选）
Layer 2: AST 分析（精确验证）
Layer 3: LLM 分析（深度审查，可选）
```

---

## Phase 1: 基础架构重构

**目标**: 建立新的架构基础，保持向后兼容

### Checklist

- [x] 1.1 添加新依赖
  - [x] 更新 `pyproject.toml` 添加 tree-sitter 相关依赖
  - [x] 添加 LLM 可选依赖（anthropic, openai）
  - [x] 运行 `uv sync` 安装依赖

- [x] 1.2 扩展类型定义
  - [x] 在 `src/types.py` 添加 `Script` 类
  - [x] 在 `src/types.py` 添加 `AnalysisMode` 枚举
  - [x] 保持现有类型不变（向后兼容）

- [ ] 1.3 创建目录结构
  - [x] 创建 `src/analyzers/` 目录
  - [x] 创建 `src/ast_parsers/` 目录
  - [x] 创建 `src/rules/regex/` 目录
  - [x] 创建 `src/rules/ast/` 目录

- [ ] 1.4 创建分析器基类
  - [ ] 创建 `src/analyzers/__init__.py`
  - [ ] 创建 `src/analyzers/base.py` 定义 `BaseAnalyzer`
  - [ ] 添加 `analyze()` 抽象方法
  - [ ] 添加 `name` 属性

- [ ] 1.5 创建配置管理
  - [ ] 创建 `src/config.py`
  - [ ] 定义 `Config` 类
  - [ ] 添加 LLM 相关配置（api_key, provider）
  - [ ] 添加分析模式配置

- [ ] 1.6 重构现有规则
  - [ ] 移动 `src/rules/command_injection.py` 到 `src/rules/regex/`
  - [ ] 移动 `src/rules/file_operations.py` 到 `src/rules/regex/`
  - [ ] 移动 `src/rules/network_security.py` 到 `src/rules/regex/`
  - [ ] 移动 `src/rules/sensitive_data.py` 到 `src/rules/regex/`
  - [ ] 创建 `src/rules/regex/__init__.py` 导出所有规则
  - [ ] 更新 `src/scanner.py` 的导入路径

- [ ] 1.7 创建 RegexAnalyzer
  - [ ] 创建 `src/analyzers/regex_analyzer.py`
  - [ ] 实现 `RegexAnalyzer` 类继承 `BaseAnalyzer`
  - [ ] 包装现有的正则规则
  - [ ] 实现 `analyze()` 方法

### 验证标准

- [ ] 所有现有测试通过
- [ ] 扫描器仍能正常工作（向后兼容）
- [ ] 代码结构清晰，目录组织合理

---

## Phase 2: Python AST 分析

**目标**: 实现 Python 代码的 AST 分析能力

### Checklist

- [ ] 2.1 创建 AST 解析器基类
  - [ ] 创建 `src/ast_parsers/__init__.py`
  - [ ] 创建 `src/ast_parsers/base.py` 定义 `BaseASTParser`
  - [ ] 定义 `parse()` 抽象方法
  - [ ] 定义通用的 AST 遍历方法

- [ ] 2.2 实现 Python AST 解析器
  - [ ] 创建 `src/ast_parsers/python_parser.py`
  - [ ] 实现 `PythonASTParser` 类
  - [ ] 实现 `parse()` 方法（使用 Python 标准库 `ast`）
  - [ ] 实现 `find_dangerous_calls()` 方法
  - [ ] 实现 `find_eval_exec()` 检测
  - [ ] 实现 `find_subprocess_calls()` 检测
  - [ ] 添加错误处理（语法错误时返回 None）

- [ ] 2.3 实现 Python AST 规则
  - [ ] 创建 `src/rules/ast/__init__.py`
  - [ ] 创建 `src/rules/ast/python_injection.py`
  - [ ] 实现 `PythonInjectionRule` 类
  - [ ] 检测 `eval()` 调用
  - [ ] 检测 `exec()` 调用
  - [ ] 检测 `subprocess` 危险用法
  - [ ] 检测 `os.system()` 调用

- [ ] 2.4 创建 ASTAnalyzer
  - [ ] 创建 `src/analyzers/ast_analyzer.py`
  - [ ] 实现 `ASTAnalyzer` 类继承 `BaseAnalyzer`
  - [ ] 根据语言选择对应的 AST 解析器
  - [ ] 实现 `analyze()` 方法
  - [ ] 添加解析失败时的回退机制

- [ ] 2.5 扩展 SkillParser
  - [ ] 修改 `src/parser.py` 添加语言检测
  - [ ] 实现 `detect_language()` 方法
  - [ ] 修改 `get_all_scripts()` 返回 `Script` 对象
  - [ ] 添加 `get_all_scripts_with_metadata()` 方法
  - [ ] 保持向后兼容（保留原有方法）

- [ ] 2.6 更新 SkillScanner
  - [ ] 修改 `src/scanner.py` 支持多分析器
  - [ ] 添加 `mode` 参数（默认 STANDARD）
  - [ ] 实现 `_init_analyzers()` 方法
  - [ ] 更新 `scan()` 方法使用 Script 对象
  - [ ] 保持向后兼容

- [ ] 2.7 添加测试用例
  - [ ] 创建 `examples/ast_test/python-false-positive/`
  - [ ] 创建包含注释中危险模式的 SKILL.md
  - [ ] 创建 `examples/ast_test/python-eval/`
  - [ ] 创建包含 eval() 的 Python 脚本
  - [ ] 验证 AST 能区分注释和代码

### 验证标准

- [ ] Python AST 分析能正确检测 eval/exec
- [ ] 能区分注释中的危险模式（不误报）
- [ ] 能区分字符串字面量中的危险模式（不误报）
- [ ] 所有现有测试仍然通过
- [ ] 新增的 Python 测试用例通过

---

## Phase 3: Shell AST 分析

**目标**: 实现 Shell 脚本的 AST 分析能力

### Checklist

- [ ] 3.1 配置 Tree-sitter
  - [ ] 创建 `build_languages.py` 脚本
  - [ ] 编译 tree-sitter-bash 语言库
  - [ ] 编译 tree-sitter-python 语言库
  - [ ] 编译 tree-sitter-javascript 语言库
  - [ ] 生成 `build/languages.so` 文件

- [ ] 3.2 实现 Shell AST 解析器
  - [ ] 创建 `src/ast_parsers/shell_parser.py`
  - [ ] 实现 `ShellASTParser` 类
  - [ ] 实现 `parse()` 方法（使用 tree-sitter-bash）
  - [ ] 实现 `find_command_substitutions()` 方法
  - [ ] 实现 `find_pipe_to_shell()` 方法
  - [ ] 实现 `find_dangerous_redirects()` 方法
  - [ ] 添加错误处理

- [ ] 3.3 实现 Shell AST 规则
  - [ ] 创建 `src/rules/ast/shell_injection.py`
  - [ ] 实现 `ShellInjectionRule` 类
  - [ ] 检测命令替换
  - [ ] 检测管道到 shell
  - [ ] 检测危险的重定向
  - [ ] 检测 eval 使用

- [ ] 3.4 添加测试用例
  - [ ] 创建 `examples/ast_test/shell-complex/`
  - [ ] 创建复杂的 Shell 脚本测试用例
  - [ ] 验证 tree-sitter 能正确解析

### 验证标准

- [ ] Shell AST 分析能正确检测命令替换
- [ ] 能处理复杂的嵌套结构
- [ ] 解析失败时能回退到正则分析
- [ ] 所有测试通过

---

## Phase 4: JavaScript AST 分析

**目标**: 实现 JavaScript 代码的 AST 分析能力

### Checklist

- [ ] 4.1 实现 JavaScript AST 解析器
  - [ ] 创建 `src/ast_parsers/javascript_parser.py`
  - [ ] 实现 `JavaScriptASTParser` 类
  - [ ] 实现 `parse()` 方法（使用 tree-sitter-javascript）
  - [ ] 实现 `find_eval_calls()` 方法
  - [ ] 实现 `find_exec_calls()` 方法
  - [ ] 添加错误处理

- [ ] 4.2 实现 JavaScript AST 规则
  - [ ] 创建 `src/rules/ast/js_injection.py`
  - [ ] 实现 `JavaScriptInjectionRule` 类
  - [ ] 检测 `eval()` 调用
  - [ ] 检测 `Function()` 构造函数
  - [ ] 检测 `child_process.exec()` 调用

- [ ] 4.3 添加测试用例
  - [ ] 创建 `examples/ast_test/javascript-eval/`
  - [ ] 创建 JavaScript 测试用例
  - [ ] 验证检测能力

### 验证标准

- [ ] JavaScript AST 分析能正确检测 eval
- [ ] 能检测 child_process 危险用法
- [ ] 所有测试通过

---

## Phase 5: LLM 分析（可选）

**目标**: 添加 LLM 深度分析能力

### Checklist

- [ ] 5.1 实现 LLM 分析器
  - [ ] 创建 `src/analyzers/llm_analyzer.py`
  - [ ] 实现 `LLMAnalyzer` 类继承 `BaseAnalyzer`
  - [ ] 实现 Anthropic Claude 集成
  - [ ] 实现 OpenAI GPT 集成（可选）
  - [ ] 实现 `analyze()` 方法
  - [ ] 添加 API 错误处理

- [ ] 5.2 设计安全分析 Prompt
  - [ ] 创建 Prompt 模板
  - [ ] 定义输出格式（JSON）
  - [ ] 添加示例（few-shot learning）
  - [ ] 优化 Prompt 以提高准确性

- [ ] 5.3 实现响应解析
  - [ ] 实现 `_parse_response()` 方法
  - [ ] 解析 JSON 响应
  - [ ] 转换为 `SecurityIssue` 对象
  - [ ] 添加错误处理

- [ ] 5.4 添加成本控制
  - [ ] 实现缓存机制（避免重复分析）
  - [ ] 添加成本估算
  - [ ] 添加 token 限制
  - [ ] 添加批量分析支持

- [ ] 5.5 更新配置
  - [ ] 在 `Config` 中添加 LLM 配置
  - [ ] 支持环境变量配置
  - [ ] 添加 provider 选择
  - [ ] 添加 model 选择

### 验证标准

- [ ] LLM 分析能检测复杂的逻辑漏洞
- [ ] 能处理混淆代码
- [ ] API 调用成功
- [ ] 成本在可控范围内
- [ ] 所有测试通过

---

## Phase 6: 命令行接口和文档

**目标**: 完善用户接口和文档

### Checklist

- [ ] 6.1 添加命令行参数
  - [ ] 在 `src/scanner.py` 添加 argparse
  - [ ] 添加 `--mode` 参数（fast/standard/deep）
  - [ ] 添加 `--llm-provider` 参数
  - [ ] 添加 `--no-ast` 参数
  - [ ] 添加 `--help` 帮助信息

- [ ] 6.2 更新输出格式
  - [ ] 在输出中显示使用的分析器
  - [ ] 添加分析模式说明
  - [ ] 优化彩色输出
  - [ ] 添加统计信息

- [ ] 6.3 更新文档
  - [ ] 更新 `README.md` 添加新功能说明
  - [ ] 更新 `CLAUDE.md` 添加架构说明
  - [ ] 更新 `docs/README.md` 添加 AST 规则说明
  - [ ] 添加使用示例

- [ ] 6.4 创建对比测试
  - [ ] 创建 `tests/compare_analyzers.py`
  - [ ] 对比正则 vs AST 的检测结果
  - [ ] 统计误报率和漏报率
  - [ ] 生成对比报告

- [ ] 6.5 性能优化
  - [ ] 添加并行处理支持
  - [ ] 优化 AST 解析性能
  - [ ] 添加缓存机制
  - [ ] 性能基准测试

### 验证标准

- [ ] 命令行接口友好易用
- [ ] 文档完整清晰
- [ ] 性能满足要求（< 2x slowdown）
- [ ] 所有功能正常工作

---

## 最终验证清单

### 功能验证

- [ ] Fast 模式（仅正则）正常工作
- [ ] Standard 模式（正则 + AST）正常工作
- [ ] Deep 模式（正则 + AST + LLM）正常工作
- [ ] 所有语言（Python、Shell、JavaScript）都能正确分析
- [ ] 误报率显著降低（通过 AST）

### 性能验证

- [ ] Fast 模式：< 1 秒/skill
- [ ] Standard 模式：< 2 秒/skill
- [ ] Deep 模式：5-10 秒/skill

### 兼容性验证

- [ ] 向后兼容：现有用法不受影响
- [ ] 所有现有测试通过
- [ ] 新增测试全部通过

### 文档验证

- [ ] README.md 更新完整
- [ ] CLAUDE.md 更新完整
- [ ] 代码注释清晰
- [ ] 使用示例完整

---

## 当前进度

**Phase 1: 基础架构重构** - 进行中

- [x] 1.1 添加新依赖 ✅
- [x] 1.2 扩展类型定义 ✅
- [x] 1.3 创建目录结构 ✅
- [ ] 1.4 创建分析器基类
- [ ] 1.5 创建配置管理
- [ ] 1.6 重构现有规则
- [ ] 1.7 创建 RegexAnalyzer

**下一步**: 完成 Phase 1 的剩余任务

---

## 注意事项

1. **向后兼容**: 每个阶段都要确保现有功能不受影响
2. **增量开发**: 每完成一个小任务就验证
3. **测试驱动**: 先写测试，再实现功能
4. **文档同步**: 代码和文档同步更新
5. **性能监控**: 持续监控性能影响

## 风险管理

1. **Tree-sitter 编译**: 提供预编译库和安装脚本
2. **LLM 成本**: 默认不启用，添加成本控制
3. **性能下降**: 并行处理，可选禁用 AST
4. **向后兼容**: 完整的回归测试

---

**最后更新**: 2026-01-13
**当前阶段**: Phase 1 - 基础架构重构
**完成度**: 15% (3/20 主要任务完成)
