"""AST 分析器"""
from typing import List
from .base import BaseAnalyzer
from ..types import SecurityIssue, Script
from ..rules.ast import PythonInjectionRule, ShellInjectionRule


class ASTAnalyzer(BaseAnalyzer):
    """AST 分析器 - 使用 AST 进行精确分析"""

    def __init__(self):
        # 语言到规则的映射
        self.language_rules = {
            'python': [PythonInjectionRule()],
            'shell': [ShellInjectionRule()],  # 新增
            # 后续添加：'javascript'
        }

    def analyze(self, script: Script) -> List[SecurityIssue]:
        """使用 AST 分析脚本

        Args:
            script: 脚本对象

        Returns:
            安全问题列表
        """
        # 检查是否支持该语言的 AST 分析
        if script.language not in self.language_rules:
            return []

        issues = []
        rules = self.language_rules[script.language]

        # 应用所有规则
        for rule in rules:
            rule_issues = rule.check(script.content)
            # 调整行号（加上脚本在原文件中的偏移）
            for issue in rule_issues:
                if issue.line_number:
                    issue.line_number += script.line_offset
            issues.extend(rule_issues)

        return issues

    @property
    def name(self) -> str:
        return "ASTAnalyzer"
