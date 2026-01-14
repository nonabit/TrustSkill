"""安全扫描器"""
from pathlib import Path
from typing import List
from colorama import Fore, Style, init

from .parser import SkillParser
from .types import ScanResult, SecurityIssue, Severity, AnalysisMode
from .analyzers.base import BaseAnalyzer
from .analyzers.regex_analyzer import RegexAnalyzer
from .analyzers.ast_analyzer import ASTAnalyzer

# 初始化 colorama
init(autoreset=True)


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

    def scan(self, skill_path: str) -> ScanResult:
        """扫描 skill 目录"""
        parser = SkillParser(skill_path)
        parser.parse()

        all_issues: List[SecurityIssue] = []

        # 使用新的分析器系统
        for script in parser.get_all_scripts_with_metadata():
            for analyzer in self.analyzers:
                issues = analyzer.analyze(script)
                all_issues.extend(issues)

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
    import json
    import time

    parser = argparse.ArgumentParser(
        prog='skill-scanner',
        description='Skill Security Scanner - 检测 Agent Skills 的安全风险'
    )
    parser.add_argument('skill_path', help='要扫描的 skill 目录路径')
    parser.add_argument('-m', '--mode', choices=['fast', 'standard', 'deep'],
                        default='standard', help='分析模式 (默认: standard)')
    parser.add_argument('--no-ast', action='store_true',
                        help='禁用 AST 分析 (等同于 --mode fast)')
    parser.add_argument('-f', '--format', choices=['text', 'json'],
                        default='text', help='输出格式 (默认: text)')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='静默模式，仅输出问题数量')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.2.0')

    args = parser.parse_args()

    # 确定分析模式
    if args.no_ast:
        mode = AnalysisMode.FAST
    else:
        mode = AnalysisMode(args.mode)

    scanner = SkillScanner(mode=mode)

    try:
        start_time = time.time()
        result = scanner.scan(args.skill_path)
        elapsed = time.time() - start_time

        # 输出结果
        if args.format == 'json':
            output = {
                'skill_path': result.skill_path,
                'mode': mode.value,
                'elapsed_seconds': round(elapsed, 3),
                'is_safe': result.is_safe,
                'summary': {
                    'total': len(result.issues),
                    'critical': result.critical_count,
                    'high': result.high_count,
                },
                'issues': [
                    {
                        'rule_id': i.rule_id,
                        'title': i.title,
                        'description': i.description,
                        'severity': i.severity.value,
                        'line_number': i.line_number,
                        'code_snippet': i.code_snippet,
                        'recommendation': i.recommendation,
                    }
                    for i in result.issues
                ]
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        elif args.quiet:
            # 静默模式：仅输出统计
            print(f"问题数量: {len(result.issues)} (严重: {result.critical_count}, 高: {result.high_count})")
        else:
            scanner.print_result(result)
            print(f"扫描耗时: {elapsed:.3f} 秒")

        # 退出码
        if result.critical_count > 0 or result.high_count > 0:
            sys.exit(1)

    except Exception as e:
        if args.format == 'json':
            print(json.dumps({'error': str(e)}, ensure_ascii=False))
        else:
            print(f"{Fore.RED}错误: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
