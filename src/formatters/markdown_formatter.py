"""Markdown 格式化器"""
from datetime import datetime
from typing import Optional

from .base import BaseFormatter
from ..types import ScanResult, SecurityIssue, Severity, AnalysisMode, CodeSnippet


class MarkdownFormatter(BaseFormatter):
    """Markdown 格式化器（供 LLM/人类阅读）"""

    SEVERITY_LABELS = {
        Severity.CRITICAL: "CRITICAL",
        Severity.HIGH: "HIGH",
        Severity.MEDIUM: "MEDIUM",
        Severity.LOW: "LOW",
    }

    def format(self, result: ScanResult, mode: AnalysisMode,
               elapsed: Optional[float] = None) -> str:
        """格式化扫描结果为 Markdown"""
        lines = []

        # 标题
        lines.append("# TrustSkill 扫描报告")
        lines.append("")

        # 基本信息
        lines.append(f"**Skill**: `{result.skill_path}`")
        lines.append(f"**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**分析模式**: {mode.value}")
        if elapsed:
            lines.append(f"**耗时**: {elapsed:.2f}s")
        lines.append("")

        # 摘要表格
        lines.append("## 摘要")
        lines.append("")
        lines.append("| 级别 | 数量 |")
        lines.append("|------|------|")
        lines.append(f"| CRITICAL | {result.critical_count} |")
        lines.append(f"| HIGH | {result.high_count} |")
        lines.append(f"| MEDIUM | {sum(1 for i in result.issues if i.severity == Severity.MEDIUM)} |")
        lines.append(f"| LOW | {sum(1 for i in result.issues if i.severity == Severity.LOW)} |")
        lines.append(f"| **总计** | **{len(result.issues)}** |")
        lines.append("")

        # 问题详情
        if result.issues:
            lines.append("## 问题详情")
            lines.append("")

            for i, issue in enumerate(result.issues, 1):
                lines.extend(self._format_issue(issue, i))
        else:
            lines.append("## 结果")
            lines.append("")
            lines.append("未发现安全问题。")
            lines.append("")

        return '\n'.join(lines)

    def _format_issue(self, issue: SecurityIssue, index: int) -> list:
        """格式化单个问题"""
        lines = []
        severity_label = self.SEVERITY_LABELS.get(issue.severity, "UNKNOWN")

        # 标题
        lines.append(f"### {index}. [{severity_label}] {issue.rule_id}")
        lines.append("")

        # 基本信息
        file_info = issue.file_path or "unknown"
        if issue.line_number:
            file_info += f":{issue.line_number}"
        lines.append(f"**文件**: `{file_info}`")
        lines.append(f"**标题**: {issue.title}")
        lines.append(f"**描述**: {issue.description}")
        lines.append("")

        # 代码片段
        if issue.code_context:
            lines.extend(self._format_code_context(issue.code_context, issue.file_path))
        elif issue.code_snippet:
            lang = self._detect_language(issue.file_path)
            lines.append(f"```{lang}")
            if issue.line_number:
                lines.append(f"# {issue.file_path}:{issue.line_number}")
            lines.append(issue.code_snippet + "  # <-- 问题行")
            lines.append("```")
            lines.append("")

        # 建议
        if issue.recommendation:
            lines.append(f"**建议**: {issue.recommendation}")
            lines.append("")

        lines.append("---")
        lines.append("")

        return lines

    def _format_code_context(self, ctx: CodeSnippet, file_path: Optional[str]) -> list:
        """格式化代码上下文"""
        lines = []
        lang = self._detect_language(file_path)

        lines.append(f"```{lang}")
        if file_path:
            lines.append(f"# {file_path}:{ctx.start_line}-{ctx.start_line + len(ctx.lines) - 1}")

        for i, line_content in enumerate(ctx.lines):
            line_num = ctx.start_line + i
            if line_num == ctx.highlight_line:
                lines.append(f"{line_content}  # <-- 问题行")
            else:
                lines.append(line_content)

        lines.append("```")
        lines.append("")

        return lines

    def _detect_language(self, file_path: Optional[str]) -> str:
        """检测代码语言"""
        if not file_path:
            return ""

        if file_path.endswith('.py'):
            return "python"
        elif file_path.endswith(('.sh', '.bash')):
            return "bash"
        elif file_path.endswith('.js'):
            return "javascript"
        elif file_path.endswith('.ts'):
            return "typescript"
        else:
            return ""
