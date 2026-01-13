"""Shell AST 解析器"""
import tree_sitter
import tree_sitter_bash
from typing import Optional, List, Tuple
from .base import BaseASTParser


class ShellASTParser(BaseASTParser):
    """Shell AST 解析器 - 使用 tree-sitter-bash"""

    def __init__(self):
        """初始化 tree-sitter parser"""
        self.language = tree_sitter.Language(tree_sitter_bash.language())
        self.parser = tree_sitter.Parser(self.language)
        self.last_code_bytes = None  # 保存最后解析的代码

    def parse(self, code: str) -> Optional[tree_sitter.Tree]:
        """解析 Shell 代码

        Args:
            code: Shell 源代码

        Returns:
            tree-sitter Tree 对象，解析失败时返回 None
        """
        try:
            self.last_code_bytes = code.encode('utf-8')
            return self.parser.parse(self.last_code_bytes)
        except Exception:
            return None

    def find_dangerous_patterns(self, tree: tree_sitter.Tree) -> List[Tuple[tree_sitter.Node, str, int]]:
        """查找危险模式

        Args:
            tree: tree-sitter Tree 对象

        Returns:
            (节点, 模式类型, 行号) 的列表
        """
        patterns = []
        code_bytes = self.last_code_bytes  # 使用保存的代码

        def traverse(node):
            """递归遍历 AST 节点"""
            # 检测 eval 命令
            if node.type == 'command_name':
                text = code_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
                if text == 'eval':
                    patterns.append((node, 'eval', node.start_point.row + 1))

            # 检测管道到 shell
            if node.type == 'pipeline':
                if self._is_pipe_to_shell(node, code_bytes):
                    patterns.append((node, 'pipe_to_shell', node.start_point.row + 1))

            # 检测命令替换
            if node.type == 'command_substitution':
                patterns.append((node, 'command_substitution', node.start_point.row + 1))

            # 递归遍历子节点
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return patterns

    def _is_pipe_to_shell(self, pipeline_node: tree_sitter.Node, code_bytes: bytes) -> bool:
        """检查管道是否指向 shell

        Args:
            pipeline_node: pipeline 节点
            code_bytes: 源代码字节

        Returns:
            是否管道到 shell
        """
        # 遍历管道中的命令，查找 bash/sh/zsh
        for child in pipeline_node.children:
            if child.type == 'command':
                for subchild in child.children:
                    if subchild.type == 'command_name':
                        cmd = code_bytes[subchild.start_byte:subchild.end_byte].decode('utf-8', errors='ignore')
                        if cmd in ['bash', 'sh', 'zsh']:
                            return True
        return False
