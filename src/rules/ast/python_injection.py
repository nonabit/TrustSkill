"""Python 代码注入检测规则（基于 AST）"""
import ast
from typing import List
from .. import SecurityRule
from ...types import SecurityIssue, Severity
from ...ast_parsers.python_parser import PythonASTParser


class PythonInjectionRule(SecurityRule):
    """检测 Python 代码注入风险（AST 分析）"""

    def __init__(self):
        self.parser = PythonASTParser()

    def check(self, script: str) -> List[SecurityIssue]:
        """检查 Python 代码注入风险

        Args:
            script: Python 源代码

        Returns:
            安全问题列表
        """
        tree = self.parser.parse(script)
        if tree is None:
            # 解析失败，返回空列表（回退到正则分析）
            return []

        issues = []
        patterns = self.parser.find_dangerous_patterns(tree)

        for node, pattern_type, line_number in patterns:
            # 提取代码片段
            try:
                code_snippet = ast.get_source_segment(script, node)
                if code_snippet is None:
                    code_snippet = f"{pattern_type}(...)"
            except Exception:
                code_snippet = f"{pattern_type}(...)"

            if pattern_type == 'eval':
                issues.append(SecurityIssue(
                    rule_id='PY_AST_EVAL',
                    title='使用 eval() 执行代码',
                    description='eval() 可以执行任意 Python 代码，存在严重安全风险',
                    severity=Severity.CRITICAL,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    recommendation='避免使用 eval()，使用 ast.literal_eval() 或其他安全方法'
                ))
            elif pattern_type == 'exec':
                issues.append(SecurityIssue(
                    rule_id='PY_AST_EXEC',
                    title='使用 exec() 执行代码',
                    description='exec() 可以执行任意 Python 代码，存在严重安全风险',
                    severity=Severity.CRITICAL,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    recommendation='避免使用 exec()，重新设计代码逻辑'
                ))
            elif pattern_type == 'compile':
                issues.append(SecurityIssue(
                    rule_id='PY_AST_COMPILE',
                    title='使用 compile() 编译代码',
                    description='compile() 可以编译任意 Python 代码，可能存在安全风险',
                    severity=Severity.HIGH,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    recommendation='谨慎使用 compile()，确保输入来源可信'
                ))
            elif pattern_type == 'os.system':
                issues.append(SecurityIssue(
                    rule_id='PY_AST_OS_SYSTEM',
                    title='使用 os.system() 执行命令',
                    description='os.system() 容易受到命令注入攻击',
                    severity=Severity.HIGH,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    recommendation='使用 subprocess.run() 并避免 shell=True'
                ))
            elif pattern_type == 'subprocess':
                issues.append(SecurityIssue(
                    rule_id='PY_AST_SUBPROCESS',
                    title='使用 subprocess 执行命令',
                    description='subprocess 调用可能存在命令注入风险，特别是使用 shell=True 时',
                    severity=Severity.HIGH,
                    line_number=line_number,
                    code_snippet=code_snippet,
                    recommendation='避免使用 shell=True，使用列表形式传递参数'
                ))

        return issues
