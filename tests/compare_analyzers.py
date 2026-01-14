"""对比分析器测试脚本

对比正则分析器和 AST 分析器的检测结果，统计差异。
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scanner import SkillScanner
from src.types import AnalysisMode


def compare_analyzers(skill_path: str):
    """对比不同分析模式的检测结果"""
    print(f"\n{'='*60}")
    print(f"对比分析: {skill_path}")
    print(f"{'='*60}\n")

    # Fast 模式（仅正则）
    fast_scanner = SkillScanner(mode=AnalysisMode.FAST)
    fast_result = fast_scanner.scan(skill_path)

    # Standard 模式（正则 + AST）
    standard_scanner = SkillScanner(mode=AnalysisMode.STANDARD)
    standard_result = standard_scanner.scan(skill_path)

    # 统计
    fast_issues = set((i.rule_id, i.line_number, i.code_snippet) for i in fast_result.issues)
    standard_issues = set((i.rule_id, i.line_number, i.code_snippet) for i in standard_result.issues)

    # 仅正则检测到的（可能是误报）
    regex_only = fast_issues - standard_issues
    # 仅 AST 检测到的（AST 新增）
    ast_only = standard_issues - fast_issues
    # 两者都检测到的
    both = fast_issues & standard_issues

    print(f"FAST 模式 (仅正则): {len(fast_result.issues)} 个问题")
    print(f"STANDARD 模式 (正则+AST): {len(standard_result.issues)} 个问题")
    print()
    print(f"两者都检测到: {len(both)}")
    print(f"仅正则检测到: {len(regex_only)}")
    print(f"仅 AST 检测到: {len(ast_only)}")

    if regex_only:
        print("\n--- 仅正则检测到（可能是误报）---")
        for rule_id, line, snippet in sorted(regex_only):
            print(f"  [{rule_id}] 行 {line}: {snippet}")

    if ast_only:
        print("\n--- 仅 AST 检测到 ---")
        for rule_id, line, snippet in sorted(ast_only):
            print(f"  [{rule_id}] 行 {line}: {snippet}")

    return {
        'fast_count': len(fast_result.issues),
        'standard_count': len(standard_result.issues),
        'both': len(both),
        'regex_only': len(regex_only),
        'ast_only': len(ast_only),
    }


def main():
    """主函数"""
    # 测试目录
    examples_dir = Path(__file__).parent.parent / "examples"

    test_paths = [
        examples_dir / "safe" / "hello-world-skill",
        examples_dir / "malicious" / "command-injection-skill",
        examples_dir / "ast_test" / "python-false-positive",
        examples_dir / "ast_test" / "python-eval",
        examples_dir / "ast_test" / "shell-complex",
    ]

    total_stats = {
        'fast_count': 0,
        'standard_count': 0,
        'both': 0,
        'regex_only': 0,
        'ast_only': 0,
    }

    for path in test_paths:
        if path.exists():
            stats = compare_analyzers(str(path))
            for key in total_stats:
                total_stats[key] += stats[key]

    print(f"\n{'='*60}")
    print("总计统计")
    print(f"{'='*60}")
    print(f"FAST 模式总问题数: {total_stats['fast_count']}")
    print(f"STANDARD 模式总问题数: {total_stats['standard_count']}")
    print(f"两者都检测到: {total_stats['both']}")
    print(f"仅正则检测到: {total_stats['regex_only']}")
    print(f"仅 AST 检测到: {total_stats['ast_only']}")


if __name__ == "__main__":
    main()
