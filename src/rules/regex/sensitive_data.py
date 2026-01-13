"""敏感信息检测规则"""
import re
from typing import List
from .. import SecurityRule
from ...types import SecurityIssue, Severity


class SensitiveDataRule(SecurityRule):
    """检测敏感信息泄露风险"""

    DANGEROUS_PATTERNS = [
        (r'\$AWS_SECRET_ACCESS_KEY', '访问 AWS 密钥', Severity.CRITICAL),
        (r'\$AWS_ACCESS_KEY_ID', '访问 AWS 访问密钥', Severity.HIGH),
        (r'\$GITHUB_TOKEN', '访问 GitHub Token', Severity.HIGH),
        (r'\$OPENAI_API_KEY', '访问 OpenAI API Key', Severity.HIGH),
        (r'\$ANTHROPIC_API_KEY', '访问 Anthropic API Key', Severity.HIGH),
        (r'\$DATABASE_URL', '访问数据库连接字符串', Severity.HIGH),
        (r'\$PRIVATE_KEY', '访问私钥', Severity.CRITICAL),
        (r'\$PASSWORD', '访问密码', Severity.HIGH),
        (r'\$SECRET', '访问密钥', Severity.HIGH),
        (r'\.env\b', '访问环境变量文件', Severity.MEDIUM),
        (r'id_rsa', '访问 SSH 私钥', Severity.CRITICAL),
        (r'credentials\.json', '访问凭证文件', Severity.HIGH),
    ]

    def check(self, script: str) -> List[SecurityIssue]:
        """检查敏感信息泄露风险"""
        issues = []

        for pattern, description, severity in self.DANGEROUS_PATTERNS:
            matches = re.finditer(pattern, script, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_number = script[:match.start()].count('\n') + 1

                issues.append(SecurityIssue(
                    rule_id='SENSITIVE_DATA',
                    title='敏感信息泄露风险',
                    description=f'{description}: {match.group()}',
                    severity=severity,
                    line_number=line_number,
                    code_snippet=match.group(),
                    recommendation='避免在脚本中直接访问敏感信息，使用安全的密钥管理方案'
                ))

        return issues
