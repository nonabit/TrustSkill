"""JSON 格式化器"""
import json
from datetime import datetime
from typing import Optional

from .base import BaseFormatter
from ..types import ScanResult, SecurityIssue, Severity, AnalysisMode, CodeSnippet


class JsonFormatter(BaseFormatter):
    """JSON 格式化器（供程序/API 使用）"""

    VERSION = "0.2.0"

    def format(self, result: ScanResult, mode: AnalysisMode,
               elapsed: Optional[float] = None) -> str:
        """格式化扫描结果为 JSON"""
        output = {
            "version": self.VERSION,
            "skill_path": result.skill_path,
            "scan_time": datetime.now().isoformat(),
            "mode": mode.value,
            "elapsed_seconds": round(elapsed, 3) if elapsed else None,
            "summary": self._build_summary(result),
            "issues": [self._format_issue(issue) for issue in result.issues]
        }
        return json.dumps(output, ensure_ascii=False, indent=2)

    def _build_summary(self, result: ScanResult) -> dict:
        """构建摘要信息"""
        return {
            "total": len(result.issues),
            "critical": result.critical_count,
            "high": result.high_count,
            "medium": sum(1 for i in result.issues if i.severity == Severity.MEDIUM),
            "low": sum(1 for i in result.issues if i.severity == Severity.LOW),
            "is_safe": result.is_safe
        }

    def _format_issue(self, issue: SecurityIssue) -> dict:
        """格式化单个问题为 dict"""
        result = {
            "id": issue.rule_id,
            "severity": self._severity_to_str(issue.severity),
            "title": issue.title,
            "description": issue.description,
            "file": issue.file_path,
            "line": issue.line_number,
            "column": issue.column,
        }

        # 代码上下文
        if issue.code_context:
            result["code_snippet"] = self._format_code_context(issue.code_context)
        elif issue.code_snippet:
            result["code_snippet"] = {
                "text": issue.code_snippet
            }

        if issue.recommendation:
            result["recommendation"] = issue.recommendation

        if issue.analyzer:
            result["analyzer"] = issue.analyzer

        return result

    def _format_code_context(self, ctx: CodeSnippet) -> dict:
        """格式化代码上下文"""
        return {
            "start_line": ctx.start_line,
            "lines": ctx.lines,
            "highlight_line": ctx.highlight_line,
            "highlight_start": ctx.highlight_start,
            "highlight_end": ctx.highlight_end
        }

    def _severity_to_str(self, severity: Severity) -> str:
        """严重程度转英文字符串"""
        mapping = {
            Severity.CRITICAL: "critical",
            Severity.HIGH: "high",
            Severity.MEDIUM: "medium",
            Severity.LOW: "low",
        }
        return mapping.get(severity, "unknown")
