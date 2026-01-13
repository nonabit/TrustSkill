"""Python AST 解析器"""
import ast
from typing import Any, Optional, List, Tuple
from .base import BaseASTParser


class PythonASTParser(BaseASTParser):
    """Python AST 解析器 - 使用标准库 ast 模块"""

    def parse(self, code: str) -> Optional[ast.AST]:
        """解析 Python 代码

        Args:
            code: Python 源代码

        Returns:
            AST 树对象，语法错误时返回 None
        """
        try:
            return ast.parse(code)
        except SyntaxError:
            return None

    def find_dangerous_patterns(self, tree: ast.AST) -> List[Tuple[ast.AST, str, int]]:
        """查找危险模式

        Args:
            tree: Python AST 树

        Returns:
            (节点, 模式类型, 行号) 的列表
        """
        patterns = []

        for node in ast.walk(tree):
            # 检测 eval() 和 exec()
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == 'eval':
                        patterns.append((node, 'eval', node.lineno))
                    elif node.func.id == 'exec':
                        patterns.append((node, 'exec', node.lineno))
                    elif node.func.id == 'compile':
                        patterns.append((node, 'compile', node.lineno))

                # 检测 os.system() 和 subprocess 调用
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'system':
                        patterns.append((node, 'os.system', node.lineno))
                    elif node.func.attr in ['Popen', 'call', 'run', 'check_output']:
                        patterns.append((node, 'subprocess', node.lineno))

        return patterns
