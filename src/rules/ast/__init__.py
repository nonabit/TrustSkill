"""AST 规则模块"""
from .python_injection import PythonInjectionRule
from .shell_injection import ShellInjectionRule

__all__ = ['PythonInjectionRule', 'ShellInjectionRule']
