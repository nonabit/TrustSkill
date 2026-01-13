"""配置管理"""
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """全局配置"""
    # LLM 配置
    llm_enabled: bool = False
    llm_provider: str = "anthropic"  # 'anthropic' or 'openai'
    anthropic_api_key: str = field(default_factory=lambda: os.getenv('ANTHROPIC_API_KEY', ''))
    openai_api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))

    # 分析配置
    enable_ast: bool = True
    enable_regex: bool = True


# 全局配置实例
config = Config()
