"""格式化器基类"""
from abc import ABC, abstractmethod
from typing import Optional
from ..types import ScanResult, AnalysisMode


class BaseFormatter(ABC):
    """格式化器基类"""

    @abstractmethod
    def format(self, result: ScanResult, mode: AnalysisMode,
               elapsed: Optional[float] = None) -> str:
        """格式化扫描结果

        Args:
            result: 扫描结果
            mode: 分析模式
            elapsed: 扫描耗时（秒）

        Returns:
            格式化后的字符串
        """
        pass
