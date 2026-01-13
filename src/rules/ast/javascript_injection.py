"""JavaScript 代码注入检测规则（基于 AST）"""
from typing import List
from .. import SecurityRule
from ...types import SecurityIssue, Severity
from ...ast_parsers.javascript_parser import JavaScriptASTParser


class JavaScriptInjectionRule(SecurityRule):
    """检测 JavaScript 代码注入风险（AST 分析）"""

    def __init__(self):
        self.parser = JavaScriptASTParser()

    def check(self, script: str) -> List[SecurityIssue]:
        """检查 JavaScript 代码注入风险

        Args:
            script: JavaScript 源代码

        Returns:
            安全问题列表
        """
        tree = self.parser.parse(script)
        if tree is None:
            return []

        issues = []
        patterns = self.parser.find_dangerous_patterns(tree)
        code_bytes = script.encode('utf-8')

        for node, pattern_type, line_number in patterns:
            try:
                code_snippet = code_bytes[node.start_byte:node.end_byte].decode('utf-8')
                if len(code_snippet) > 100:
                    code_snippet = code_snippet[:100] + '...'
            except (UnicodeDecodeError, IndexError):
                code_snippet = f"{pattern_type}(...)"

            issue = self._create_issue(pattern_type, line_number, code_snippet)
            if issue:
                issues.append(issue)

        return issues

    def _create_issue(self, pattern_type: str, line_number: int, code_snippet: str) -> SecurityIssue | None:
        """根据模式类型创建安全问题"""
        issue_map = {
            'eval': (
                'JS_AST_EVAL',
                '使用 eval() 执行代码',
                'eval() 可以执行任意 JavaScript 代码，存在严重安全风险',
                Severity.CRITICAL,
                '避免使用 eval()，使用 JSON.parse() 或其他安全方法'
            ),
            'Function': (
                'JS_AST_FUNCTION',
                '使用 Function 构造器',
                'Function 构造器可以动态创建函数，存在代码注入风险',
                Severity.CRITICAL,
                '避免使用 Function 构造器'
            ),
            'new_Function': (
                'JS_AST_NEW_FUNCTION',
                '使用 new Function() 创建函数',
                'new Function() 可以动态创建函数，存在代码注入风险',
                Severity.CRITICAL,
                '避免使用 new Function()'
            ),
            'timer_string': (
                'JS_AST_TIMER_STRING',
                'setTimeout/setInterval 使用字符串参数',
                '传递字符串给 setTimeout/setInterval 会执行 eval',
                Severity.HIGH,
                '使用函数引用代替字符串'
            ),
            'child_process': (
                'JS_AST_CHILD_PROCESS',
                '使用 child_process 执行命令',
                'child_process 可能导致命令注入',
                Severity.HIGH,
                '验证输入，避免拼接用户输入到命令'
            ),
            'vm': (
                'JS_AST_VM',
                '使用 vm 模块执行代码',
                'vm 模块可以执行任意代码',
                Severity.HIGH,
                '谨慎使用 vm 模块，确保输入可信'
            ),
        }

        if pattern_type not in issue_map:
            return None

        rule_id, title, desc, severity, rec = issue_map[pattern_type]
        return SecurityIssue(
            rule_id=rule_id,
            title=title,
            description=desc,
            severity=severity,
            line_number=line_number,
            code_snippet=code_snippet,
            recommendation=rec
        )
