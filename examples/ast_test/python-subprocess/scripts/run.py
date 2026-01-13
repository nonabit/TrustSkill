#!/usr/bin/env python3
"""危险的 subprocess 使用示例"""
import subprocess

def run_command(user_input):
    """危险：使用 shell=True 执行用户输入"""
    # 这是危险的，因为可能导致命令注入
    result = subprocess.call(user_input, shell=True)
    return result

def another_dangerous_call():
    """另一个危险的调用"""
    cmd = "ls -la"
    subprocess.Popen(cmd, shell=True)

if __name__ == "__main__":
    user_cmd = input("Enter command: ")
    run_command(user_cmd)
