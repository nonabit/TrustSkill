"""安全规则基类"""
from abc import ABC, abstractmethod
from typing import List
from ..types import SecurityIssue


class SecurityRule(ABC):
    """安全规则基类"""

    @abstractmethod
    def check(self, script: str) -> List[SecurityIssue]:
        """检查脚本是否存在安全问题"""
        pass
