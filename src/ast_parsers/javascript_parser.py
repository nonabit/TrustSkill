"""JavaScript AST 解析器"""
import tree_sitter
import tree_sitter_javascript
from typing import Optional, List, Tuple
from .base import BaseASTParser


class JavaScriptASTParser(BaseASTParser):
    """JavaScript AST 解析器 - 使用 tree-sitter-javascript"""

    def __init__(self):
        """初始化 tree-sitter parser"""
        self.language = tree_sitter.Language(tree_sitter_javascript.language())
        self.parser = tree_sitter.Parser(self.language)
        self.last_code_bytes = None

    def parse(self, code: str) -> Optional[tree_sitter.Tree]:
        """解析 JavaScript 代码

        Args:
            code: JavaScript 源代码

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
        code_bytes = self.last_code_bytes
        if code_bytes is None:
            return patterns

        def get_text(node) -> str:
            """获取节点文本"""
            return code_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')

        def traverse(node):
            """递归遍历 AST 节点"""
            # 检测函数调用
            if node.type == 'call_expression':
                func_node = node.child_by_field_name('function')
                if func_node:
                    func_text = get_text(func_node)

                    # eval() 调用
                    if func_text == 'eval':
                        patterns.append((node, 'eval', node.start_point.row + 1))
                    # Function() 构造器
                    elif func_text == 'Function':
                        patterns.append((node, 'Function', node.start_point.row + 1))
                    # setTimeout/setInterval 字符串参数
                    elif func_text in ['setTimeout', 'setInterval']:
                        # 查找 arguments 子节点
                        for child in node.children:
                            if child.type == 'arguments' and child.child_count > 0:
                                # 获取第一个非括号参数
                                for arg in child.children:
                                    if arg.type == 'string':
                                        patterns.append((node, 'timer_string', node.start_point.row + 1))
                                        break
                                break
                    # exec/spawn 等直接调用（解构导入的情况）
                    elif func_text in ['exec', 'execSync', 'spawn', 'spawnSync', 'execFile', 'execFileSync']:
                        patterns.append((node, 'child_process', node.start_point.row + 1))
                    # child_process 方法（成员访问的情况）
                    elif self._is_child_process_call(func_node, code_bytes):
                        patterns.append((node, 'child_process', node.start_point.row + 1))
                    # vm 模块调用
                    elif self._is_vm_call(func_node, code_bytes):
                        patterns.append((node, 'vm', node.start_point.row + 1))

            # 检测 new Function()
            if node.type == 'new_expression':
                constructor = node.child_by_field_name('constructor')
                if constructor:
                    text = get_text(constructor)
                    if text == 'Function':
                        patterns.append((node, 'new_Function', node.start_point.row + 1))

            # 递归遍历子节点
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return patterns

    def _is_child_process_call(self, func_node, code_bytes: bytes) -> bool:
        """检查是否为 child_process 调用"""
        if func_node.type == 'member_expression':
            prop = func_node.child_by_field_name('property')
            if prop:
                prop_text = code_bytes[prop.start_byte:prop.end_byte].decode('utf-8', errors='ignore')
                if prop_text in ['exec', 'execSync', 'spawn', 'spawnSync', 'execFile', 'execFileSync']:
                    return True
        return False

    def _is_vm_call(self, func_node, code_bytes: bytes) -> bool:
        """检查是否为 vm 模块调用"""
        if func_node.type == 'member_expression':
            prop = func_node.child_by_field_name('property')
            if prop:
                prop_text = code_bytes[prop.start_byte:prop.end_byte].decode('utf-8', errors='ignore')
                if prop_text in ['runInContext', 'runInNewContext', 'runInThisContext', 'compileFunction']:
                    return True
        return False
