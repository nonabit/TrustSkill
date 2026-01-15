"""安全扫描器"""
from typing import List, Optional, Callable
from colorama import Fore, Style, init

from .parser import SkillParser
from .types import ScanResult, SecurityIssue, Severity, AnalysisMode
from .analyzers.base import BaseAnalyzer
from .analyzers.regex_analyzer import RegexAnalyzer
from .analyzers.ast_analyzer import ASTAnalyzer
from .formatters import RichFormatter, JsonFormatter, MarkdownFormatter
from .formatters.rich_formatter import ScanProgress

# 初始化 colorama
init(autoreset=True)

# 进度回调类型：(当前文件名, 已处理数, 总数, 已发现问题数)
ProgressCallback = Callable[[str, int, int, int], None]


class SkillScanner:
    """Skill 安全扫描器"""

    def __init__(self, mode: AnalysisMode = AnalysisMode.STANDARD):
        """初始化扫描器

        Args:
            mode: 分析模式（FAST/STANDARD/DEEP）
        """
        self.mode = mode
        self.analyzers = self._init_analyzers()

    def _init_analyzers(self) -> List[BaseAnalyzer]:
        """根据分析模式初始化分析器

        Returns:
            分析器列表
        """
        analyzers = []

        if self.mode == AnalysisMode.FAST:
            # 仅正则分析
            analyzers.append(RegexAnalyzer())
        elif self.mode == AnalysisMode.STANDARD:
            # 正则 + AST 分析
            analyzers.append(RegexAnalyzer())
            analyzers.append(ASTAnalyzer())
        elif self.mode == AnalysisMode.DEEP:
            # 正则 + AST + LLM 分析（Phase 5）
            analyzers.append(RegexAnalyzer())
            analyzers.append(ASTAnalyzer())
            # TODO: 添加 LLMAnalyzer

        return analyzers

    def scan(self, skill_path: str,
             progress_callback: Optional[ProgressCallback] = None) -> ScanResult:
        """扫描 skill 目录

        Args:
            skill_path: skill 目录路径
            progress_callback: 可选的进度回调函数

        Returns:
            扫描结果
        """
        parser = SkillParser(skill_path)
        parser.parse()

        scripts = parser.get_all_scripts_with_metadata()
        total_scripts = len(scripts)
        all_issues: List[SecurityIssue] = []

        for idx, script in enumerate(scripts):
            # 回调进度
            if progress_callback:
                progress_callback(script.source, idx, total_scripts, len(all_issues))

            for analyzer in self.analyzers:
                issues = analyzer.analyze(script)
                # 为每个 issue 填充 file_path 和 analyzer
                for issue in issues:
                    if issue.file_path is None:
                        issue.file_path = script.source
                    if issue.analyzer is None:
                        issue.analyzer = analyzer.name
                all_issues.extend(issues)

        # 最后一次回调
        if progress_callback:
            progress_callback("", total_scripts, total_scripts, len(all_issues))

        return ScanResult(skill_path=skill_path, issues=all_issues)

    def scan_with_progress(self, skill_path: str) -> ScanResult:
        """带进度显示的扫描"""
        parser = SkillParser(skill_path)
        parser.parse()
        scripts = parser.get_all_scripts_with_metadata()

        progress = ScanProgress()
        progress.start(len(scripts))

        all_issues: List[SecurityIssue] = []

        try:
            for script in scripts:
                progress.update(script.source)

                for analyzer in self.analyzers:
                    issues = analyzer.analyze(script)
                    for issue in issues:
                        if issue.file_path is None:
                            issue.file_path = script.source
                        if issue.analyzer is None:
                            issue.analyzer = analyzer.name
                    all_issues.extend(issues)

                progress.set_issues_count(len(all_issues))
        finally:
            progress.stop()

        return ScanResult(skill_path=skill_path, issues=all_issues)

    def print_result(self, result: ScanResult):
        """打印扫描结果"""
        print(f"\n{'='*60}")
        print(f"扫描目标: {result.skill_path}")
        # 显示分析模式和使用的分析器
        analyzer_names = ', '.join([a.name for a in self.analyzers])
        print(f"分析模式: {self.mode.value.upper()} ({analyzer_names})")
        print(f"{'='*60}\n")

        if result.is_safe:
            print(f"{Fore.GREEN}✓ 未发现安全问题{Style.RESET_ALL}\n")
            return

        # 按严重程度分组
        critical = [i for i in result.issues if i.severity == Severity.CRITICAL]
        high = [i for i in result.issues if i.severity == Severity.HIGH]
        medium = [i for i in result.issues if i.severity == Severity.MEDIUM]
        low = [i for i in result.issues if i.severity == Severity.LOW]

        # 打印统计
        print(f"{Fore.RED}✗ 发现 {len(result.issues)} 个安全问题:{Style.RESET_ALL}")
        if critical:
            print(f"  {Fore.RED}● 严重: {len(critical)}{Style.RESET_ALL}")
        if high:
            print(f"  {Fore.YELLOW}● 高: {len(high)}{Style.RESET_ALL}")
        if medium:
            print(f"  {Fore.BLUE}● 中: {len(medium)}{Style.RESET_ALL}")
        if low:
            print(f"  {Fore.CYAN}● 低: {len(low)}{Style.RESET_ALL}")
        print()

        # 打印详细问题
        for issue in result.issues:
            self._print_issue(issue)

    def _print_issue(self, issue: SecurityIssue):
        """打印单个问题"""
        # 根据严重程度选择颜色
        color = {
            Severity.CRITICAL: Fore.RED,
            Severity.HIGH: Fore.YELLOW,
            Severity.MEDIUM: Fore.BLUE,
            Severity.LOW: Fore.CYAN,
        }[issue.severity]

        print(f"{color}[{issue.severity.value}] {issue.title}{Style.RESET_ALL}")
        print(f"  规则: {issue.rule_id}")
        print(f"  描述: {issue.description}")
        if issue.line_number:
            print(f"  行号: {issue.line_number}")
        if issue.code_snippet:
            print(f"  代码: {issue.code_snippet}")
        if issue.recommendation:
            print(f"  建议: {issue.recommendation}")
        print()


def main():
    """主函数"""
    import sys
    import argparse
    import time

    parser = argparse.ArgumentParser(
        prog='trustskill',
        description='TrustSkill - 检测 Agent Skills 的安全风险'
    )
    parser.add_argument('skill_path', help='要扫描的 skill 目录路径')
    parser.add_argument('-m', '--mode', choices=['fast', 'standard', 'deep'],
                        default='standard', help='分析模式 (默认: standard)')
    parser.add_argument('--no-ast', action='store_true',
                        help='禁用 AST 分析 (等同于 --mode fast)')
    parser.add_argument('-f', '--format', choices=['rich', 'json', 'markdown', 'text'],
                        default='rich', help='输出格式 (默认: rich)')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='静默模式，仅输出问题数量')
    parser.add_argument('--no-progress', action='store_true',
                        help='禁用进度显示')
    parser.add_argument('--export-for-llm', action='store_true',
                        help='导出 skill 内容供 LLM 检查（配合 docs/llm-security-guide.md 使用）')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.3.0')

    args = parser.parse_args()

    # 处理 --export-for-llm
    if args.export_for_llm:
        skill_parser = SkillParser(args.skill_path)
        skill_parser.parse()
        config = skill_parser.config or {}
        print("=== SKILL 信息 ===")
        print(f"名称: {config.get('name', '未知')}")
        print(f"描述: {config.get('description', '无')}")
        print("\n=== 脚本内容 ===\n")
        for script in skill_parser.get_all_scripts_with_metadata():
            print(f"--- {script.source} ({script.language}) ---")
            print(script.content)
            print()
        print("---")
        print("请将以上内容与 docs/llm-security-guide.md 中的检查提示词一起发送给 LLM 进行安全审查。")
        sys.exit(0)

    # 确定分析模式
    if args.no_ast:
        mode = AnalysisMode.FAST
    else:
        mode = AnalysisMode(args.mode)

    scanner = SkillScanner(mode=mode)

    # 选择格式化器
    if args.format == 'json':
        formatter = JsonFormatter()
    elif args.format == 'markdown':
        formatter = MarkdownFormatter()
    elif args.format == 'rich':
        formatter = RichFormatter()
    else:
        formatter = None  # 使用旧版 text 格式

    try:
        start_time = time.time()

        # 根据设置决定是否显示进度
        if args.format == 'rich' and not args.no_progress and not args.quiet:
            result = scanner.scan_with_progress(args.skill_path)
        else:
            result = scanner.scan(args.skill_path)

        elapsed = time.time() - start_time

        # 输出结果
        if args.quiet:
            # 静默模式：仅输出统计
            print(f"问题数量: {len(result.issues)} (严重: {result.critical_count}, 高: {result.high_count})")
        elif formatter:
            if args.format == 'rich':
                formatter.print(result, mode, elapsed)
            else:
                print(formatter.format(result, mode, elapsed))
        else:
            # 旧版 text 格式
            scanner.print_result(result)
            print(f"扫描耗时: {elapsed:.3f} 秒")

        # 退出码
        if result.critical_count > 0 or result.high_count > 0:
            sys.exit(1)

    except Exception as e:
        if args.format == 'json':
            import json
            print(json.dumps({'error': str(e)}, ensure_ascii=False))
        else:
            print(f"{Fore.RED}错误: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
