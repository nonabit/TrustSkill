"""Rich 终端格式化器（Cargo 风格）"""
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from .base import BaseFormatter
from ..types import ScanResult, SecurityIssue, Severity, AnalysisMode, CodeSnippet


class RichFormatter(BaseFormatter):
    """Rich 终端格式化器（Rust/Cargo 风格）"""

    # 严重程度映射
    SEVERITY_STYLES = {
        Severity.CRITICAL: ('critical', 'bold red'),
        Severity.HIGH: ('warning', 'bold yellow'),
        Severity.MEDIUM: ('warning', 'yellow'),
        Severity.LOW: ('note', 'blue'),
    }

    def __init__(self):
        self.console = Console()

    def format(self, result: ScanResult, mode: AnalysisMode,
               elapsed: Optional[float] = None) -> str:
        """格式化扫描结果为 Cargo 风格输出"""
        output_parts = []

        # 如果没有问题
        if result.is_safe:
            output_parts.append(self._format_success(result, mode, elapsed))
        else:
            # 输出每个问题
            for issue in result.issues:
                output_parts.append(self._format_issue(issue))

            # 输出摘要
            output_parts.append(self._format_summary(result, mode, elapsed))

        return '\n'.join(output_parts)

    def _format_success(self, result: ScanResult, mode: AnalysisMode,
                        elapsed: Optional[float]) -> str:
        """格式化成功结果"""
        lines = []
        lines.append(f"   [bold green]Finished[/] 扫描 `{result.skill_path}`")
        if elapsed:
            lines.append(f"    [dim]耗时 {elapsed:.2f}s，模式 {mode.value}[/]")
        lines.append("")
        lines.append("[bold green]    ok[/] 未发现安全问题")
        return '\n'.join(lines)

    def _format_issue(self, issue: SecurityIssue) -> str:
        """格式化单个问题（Cargo 风格）"""
        label, style = self.SEVERITY_STYLES.get(
            issue.severity, ('note', 'blue')
        )
        lines = []

        # 第一行：severity[rule_id]: title
        lines.append(f"[{style}]{label}[{issue.rule_id}][/]: {issue.title}")

        # 第二行：文件位置
        file_path = issue.file_path or 'unknown'
        line_num = issue.line_number or 1
        col = issue.column or 1
        lines.append(f"  [bold blue]-->[/] {file_path}:{line_num}:{col}")

        # 代码上下文
        if issue.code_context:
            lines.extend(self._format_code_context(issue.code_context, issue.description))
        elif issue.code_snippet:
            # 兼容旧版简单代码片段
            lines.append("   [dim]|[/]")
            snippet_line = issue.line_number or 1
            lines.append(f"[dim]{snippet_line:>3}[/] [dim]|[/]     {issue.code_snippet}")
            lines.append(f"   [dim]|[/]     [bold {style}]{'~' * min(len(issue.code_snippet), 40)}[/] {issue.description}")
            lines.append("   [dim]|[/]")
        else:
            # 没有代码上下文时只显示描述
            lines.append(f"   [dim]|[/]")
            lines.append(f"   [dim]|[/] {issue.description}")
            lines.append(f"   [dim]|[/]")

        # 建议
        if issue.recommendation:
            lines.append(f"   [dim]=[/] [bold]建议[/]: {issue.recommendation}")

        lines.append("")  # 空行分隔
        return '\n'.join(lines)

    def _format_code_context(self, ctx: CodeSnippet, description: str) -> list:
        """格式化代码上下文"""
        lines = []
        lines.append("   [dim]|[/]")

        for i, line_content in enumerate(ctx.lines):
            line_num = ctx.start_line + i
            is_highlight = line_num == ctx.highlight_line

            if is_highlight:
                lines.append(f"[bold red]{line_num:>3}[/] [dim]|[/]     {line_content}")
                # 下划线指示
                if ctx.highlight_start > 0 and ctx.highlight_end > ctx.highlight_start:
                    underline_len = ctx.highlight_end - ctx.highlight_start
                    underline = ' ' * ctx.highlight_start + '^' * underline_len
                else:
                    # 默认下划线整行有效内容
                    stripped = line_content.lstrip()
                    indent = len(line_content) - len(stripped)
                    underline = ' ' * indent + '^' * len(stripped)
                lines.append(f"   [dim]|[/]     [bold red]{underline}[/] {description}")
            else:
                lines.append(f"[dim]{line_num:>3}[/] [dim]|[/]     {line_content}")

        lines.append("   [dim]|[/]")
        return lines

    def _format_summary(self, result: ScanResult, mode: AnalysisMode,
                        elapsed: Optional[float]) -> str:
        """格式化摘要"""
        lines = []

        # 统计
        critical = result.critical_count
        high = result.high_count
        medium = sum(1 for i in result.issues if i.severity == Severity.MEDIUM)
        low = sum(1 for i in result.issues if i.severity == Severity.LOW)

        # 摘要行
        summary_parts = []
        if critical:
            summary_parts.append(f"[bold red]{critical} critical[/]")
        if high:
            summary_parts.append(f"[bold yellow]{high} high[/]")
        if medium:
            summary_parts.append(f"[yellow]{medium} medium[/]")
        if low:
            summary_parts.append(f"[blue]{low} low[/]")

        total = len(result.issues)
        status = "[bold red]error[/]" if critical or high else "[bold yellow]warning[/]"
        lines.append(f"{status}: 扫描完成，发现 {total} 个问题 ({', '.join(summary_parts)})")

        if elapsed:
            lines.append(f"    [dim]扫描 `{result.skill_path}`，耗时 {elapsed:.2f}s，模式 {mode.value}[/]")

        return '\n'.join(lines)

    def print(self, result: ScanResult, mode: AnalysisMode,
              elapsed: Optional[float] = None):
        """直接打印到终端（带 Rich 样式）"""
        output = self.format(result, mode, elapsed)
        self.console.print(output)


class ScanProgress:
    """扫描进度显示"""

    def __init__(self):
        self.console = Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]扫描中[/]"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("{task.fields[filename]}"),
            console=self.console,
        )
        self.task_id = None
        self.issues_found = 0

    def start(self, total_files: int):
        """开始进度显示"""
        self.progress.start()
        self.task_id = self.progress.add_task(
            "扫描",
            total=total_files,
            filename=""
        )

    def update(self, filename: str, advance: int = 1):
        """更新进度"""
        if self.task_id is not None:
            self.progress.update(
                self.task_id,
                advance=advance,
                filename=filename
            )

    def set_issues_count(self, count: int):
        """更新发现的问题数量"""
        self.issues_found = count

    def stop(self):
        """停止进度显示"""
        self.progress.stop()
        if self.issues_found > 0:
            self.console.print(f"[dim]已发现 {self.issues_found} 个问题[/]")
