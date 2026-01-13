"""网络安全检测规则"""
import re
from typing import List
from .. import SecurityRule
from ...types import SecurityIssue, Severity


class NetworkSecurityRule(SecurityRule):
    """检测网络安全风险"""

    DANGEROUS_PATTERNS = [
        (r'\bcurl\s+.*\|\s*sh', '从网络下载并执行脚本', Severity.CRITICAL),
        (r'\bwget\s+.*\|\s*sh', '从网络下载并执行脚本', Severity.CRITICAL),
        (r'\bcurl\s+.*\|\s*bash', '从网络下载并执行脚本', Severity.CRITICAL),
        (r'\bwget\s+.*\|\s*bash', '从网络下载并执行脚本', Severity.CRITICAL),
        (r'http://[^\s]+', '使用不安全的 HTTP 协议', Severity.MEDIUM),
        (r'\bcurl\s+.*-X\s+POST.*\$', '可能的数据外泄', Severity.HIGH),
        (r'\bwget\s+.*--post-data.*\$', '可能的数据外泄', Severity.HIGH),
        (r'\bnc\s+.*-e', '使用 netcat 反向 shell', Severity.CRITICAL),
        (r'/dev/tcp/', '使用 TCP 连接', Severity.HIGH),
    ]

    def check(self, script: str) -> List[SecurityIssue]:
        """检查网络安全风险"""
        issues = []

        for pattern, description, severity in self.DANGEROUS_PATTERNS:
            matches = re.finditer(pattern, script, re.MULTILINE)
            for match in matches:
                line_number = script[:match.start()].count('\n') + 1

                issues.append(SecurityIssue(
                    rule_id='NETWORK_SECURITY',
                    title='网络安全风险',
                    description=f'{description}: {match.group()}',
                    severity=severity,
                    line_number=line_number,
                    code_snippet=match.group(),
                    recommendation='避免从不可信来源下载和执行代码，使用 HTTPS'
                ))

        return issues
