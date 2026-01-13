"""正则表达式分析器"""
from typing import List
from .base import BaseAnalyzer
from ..types import SecurityIssue, Script
from ..rules.regex import (
    CommandInjectionRule,
    FileOperationRule,
    NetworkSecurityRule,
    SensitiveDataRule,
)


class RegexAnalyzer(BaseAnalyzer):
    """正则表达式分析器 - 包装现有的正则规则"""

    def __init__(self):
        self.rules = [
            CommandInjectionRule(),
            FileOperationRule(),
            NetworkSecurityRule(),
            SensitiveDataRule(),
        ]

    def analyze(self, script: Script) -> List[SecurityIssue]:
        """使用正则规则分析脚本"""
        issues = []
        for rule in self.rules:
            # 正则规则使用字符串内容
            rule_issues = rule.check(script.content)
            issues.extend(rule_issues)
        return issues

    @property
    def name(self) -> str:
        return "RegexAnalyzer"
