"""Shell 命令注入检测规则（基于 AST）"""
from typing import List
from .. import SecurityRule
from ...types import SecurityIssue, Severity
from ...ast_parsers.shell_parser import ShellASTParser


class ShellInjectionRule(SecurityRule):
    """检测 Shell 命令注入风险（AST 分析）"""

    def __init__(self):
        self.parser = ShellASTParser()

    def check(self, script: str) -> List[SecurityIssue]:
        """检查 Shell 命令注入风险

        Args:
            script: Shell 源代码

        Returns:
            安全问题列表
        """
        tree = self.parser.parse(script)
        if tree is None or tree.root_node is None:
            # 解析失败，返回空列表（回退到正则分析）
            return []

        issues = []
        patterns = self.parser.find_dangerous_patterns(tree)
        code_bytes = script.encode('utf-8')

        for node, pattern_type, line_number in patterns:
            # 提取代码片段
            try:
                code_snippet = code_bytes[node.start_byte:node.end_byte].decode('utf-8')
                # 限制代码片段长度
                if len(code_snippet) > 100:
                    code_snippet = code_snippet[:100] + '...'
            except (UnicodeDecodeError, IndexError):
                code_snippet = f"{pattern_type}(...)"

            if pattern_type == 'eval':
                issues.append(SecurityIssue(
                    rule_id='SH_AST_EVAL',
                    title='使用 eval 执行命令',
                    description='eval 可以执行任意 Shell 命令，存在严重安全风险',
                    severity=Severity.CRITICAL,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    recommendation='避免使用 eval，直接调用命令或使用数组'
                ))
            elif pattern_type == 'pipe_to_shell':
                issues.append(SecurityIssue(
                    rule_id='SH_AST_PIPE_TO_SHELL',
                    title='管道到 shell 执行',
                    description='将数据管道到 bash/sh 可能执行恶意代码',
                    severity=Severity.HIGH,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    recommendation='避免管道到 shell，先保存到文件并验证内容'
                ))
            elif pattern_type == 'command_substitution':
                issues.append(SecurityIssue(
                    rule_id='SH_AST_CMD_SUBST',
                    title='命令替换',
                    description='命令替换可能导致命令注入，需确保输入可信',
                    severity=Severity.MEDIUM,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    recommendation='谨慎使用命令替换，验证输入来源'
                ))

        return issues
