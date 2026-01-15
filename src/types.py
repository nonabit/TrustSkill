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


class OutputFormat(Enum):
    """输出格式"""
    RICH = "rich"        # 终端美化输出（默认）
    JSON = "json"        # JSON 格式
    MARKDOWN = "markdown"  # Markdown 格式
    TEXT = "text"        # 纯文本（旧版兼容）


@dataclass
class Script:
    """脚本信息"""
    content: str
    language: str  # 'python', 'javascript', 'shell', 'unknown'
    source: str    # 来源：'markdown' 或文件路径
    line_offset: int = 0  # 在原文件中的行偏移


@dataclass
class CodeSnippet:
    """代码片段（用于问题上下文展示）"""
    start_line: int          # 起始行号
    lines: List[str]         # 代码行列表
    highlight_line: int      # 高亮行号（问题所在行）
    highlight_start: int = 0  # 高亮起始列
    highlight_end: int = 0    # 高亮结束列


@dataclass
class SecurityIssue:
    """安全问题"""
    rule_id: str
    title: str
    description: str
    severity: Severity
    file_path: Optional[str] = None      # 文件路径
    line_number: Optional[int] = None
    column: Optional[int] = None         # 列号
    code_snippet: Optional[str] = None   # 简单代码片段（兼容旧版）
    code_context: Optional[CodeSnippet] = None  # 详细代码上下文
    recommendation: Optional[str] = None
    analyzer: Optional[str] = None       # 来源分析器（regex/ast）


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
