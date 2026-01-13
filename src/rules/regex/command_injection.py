"""命令注入检测规则"""
import re
from typing import List
from .. import SecurityRule
from ...types import SecurityIssue, Severity


class CommandInjectionRule(SecurityRule):
    """检测命令注入风险"""

    # 危险的命令执行模式
    DANGEROUS_PATTERNS = [
        (r'\beval\s*\(', '使用 eval() 执行代码', Severity.CRITICAL),
        (r'\bexec\s*\(', '使用 exec() 执行代码', Severity.CRITICAL),
        (r'\$\([^)]*\$', '嵌套命令替换', Severity.HIGH),
        (r'`[^`]*\$', '命令替换中使用变量', Severity.HIGH),
        (r'\|\s*sh\b', '管道到 sh', Severity.HIGH),
        (r'\|\s*bash\b', '管道到 bash', Severity.HIGH),
        (r';\s*rm\s+-rf', '危险的删除命令', Severity.CRITICAL),
        (r'&&\s*rm\s+-rf', '危险的删除命令', Severity.CRITICAL),
    ]

    def check(self, script: str) -> List[SecurityIssue]:
        """检查命令注入风险"""
        issues = []

        for pattern, description, severity in self.DANGEROUS_PATTERNS:
            matches = re.finditer(pattern, script, re.MULTILINE)
            for match in matches:
                # 计算行号
                line_number = script[:match.start()].count('\n') + 1

                issues.append(SecurityIssue(
                    rule_id='CMD_INJECTION',
                    title='命令注入风险',
                    description=f'{description}: {match.group()}',
                    severity=severity,
                    line_number=line_number,
                    code_snippet=match.group(),
                    recommendation='避免使用动态命令执行，使用参数化的方式调用命令'
                ))

        return issues
