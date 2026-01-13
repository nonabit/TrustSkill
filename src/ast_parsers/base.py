"""AST 解析器基类"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Tuple


class BaseASTParser(ABC):
    """AST 解析器基类"""

    @abstractmethod
    def parse(self, code: str) -> Optional[Any]:
        """解析代码，返回 AST 树或 None（解析失败时）

        Args:
            code: 源代码字符串

        Returns:
            AST 树对象，解析失败时返回 None
        """
        pass

    @abstractmethod
    def find_dangerous_patterns(self, tree: Any) -> List[Tuple]:
        """在 AST 中查找危险模式

        Args:
            tree: AST 树对象

        Returns:
            危险模式列表，格式由子类定义
        """
        pass
