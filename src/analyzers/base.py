"""分析器基类"""
from abc import ABC, abstractmethod
from typing import List
from ..types import SecurityIssue, Script


class BaseAnalyzer(ABC):
    """分析器基类"""

    @abstractmethod
    def analyze(self, script: Script) -> List[SecurityIssue]:
        """分析脚本，返回安全问题列表"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """分析器名称"""
        pass
