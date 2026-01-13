"""文件系统安全检测规则"""
import re
from typing import List
from .. import SecurityRule
from ...types import SecurityIssue, Severity


class FileOperationRule(SecurityRule):
    """检测危险的文件操作"""

    DANGEROUS_PATTERNS = [
        (r'\brm\s+-rf\s+/', '删除根目录文件', Severity.CRITICAL),
        (r'\brm\s+-rf\s+~', '删除用户目录', Severity.CRITICAL),
        (r'\brm\s+-rf\s+\$HOME', '删除 HOME 目录', Severity.CRITICAL),
        (r'\bchmod\s+777', '设置过于宽松的权限', Severity.HIGH),
        (r'\bchown\s+.*\s+/', '修改根目录所有权', Severity.HIGH),
        (r'>\s*/etc/', '写入系统配置目录', Severity.HIGH),
        (r'>\s*/usr/', '写入系统目录', Severity.HIGH),
        (r'>\s*/var/', '写入系统变量目录', Severity.MEDIUM),
        (r'\b\.ssh/', '访问 SSH 密钥目录', Severity.HIGH),
        (r'\b\.aws/', '访问 AWS 凭证目录', Severity.HIGH),
    ]

    def check(self, script: str) -> List[SecurityIssue]:
        """检查文件操作风险"""
        issues = []

        for pattern, description, severity in self.DANGEROUS_PATTERNS:
            matches = re.finditer(pattern, script, re.MULTILINE)
            for match in matches:
                line_number = script[:match.start()].count('\n') + 1

                issues.append(SecurityIssue(
                    rule_id='FILE_OPERATION',
                    title='危险的文件操作',
                    description=f'{description}: {match.group()}',
                    severity=severity,
                    line_number=line_number,
                    code_snippet=match.group(),
                    recommendation='避免操作系统关键目录和敏感文件'
                ))

        return issues
