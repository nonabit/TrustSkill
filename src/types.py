"""类型定义"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Severity(Enum):
    """风险等级"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "严重"


class AnalysisMode(Enum):
    """分析模式"""
    FAST = "fast"        # 仅正则
    STANDARD = "standard"  # 正则 + AST
    DEEP = "deep"        # 正则 + AST + LLM


@dataclass
class Script:
    """脚本信息"""
    content: str
    language: str  # 'python', 'javascript', 'shell', 'unknown'
    source: str    # 来源：'markdown' 或文件路径
    line_offset: int = 0  # 在原文件中的行偏移


@dataclass
class SecurityIssue:
    """安全问题"""
    rule_id: str
    title: str
    description: str
    severity: Severity
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None


@dataclass
class ScanResult:
    """扫描结果"""
    skill_path: str
    issues: List[SecurityIssue]

    @property
    def is_safe(self) -> bool:
        """是否安全"""
        return len(self.issues) == 0

    @property
    def critical_count(self) -> int:
        """严重问题数量"""
        return sum(1 for issue in self.issues if issue.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        """高风险问题数量"""
        return sum(1 for issue in self.issues if issue.severity == Severity.HIGH)
