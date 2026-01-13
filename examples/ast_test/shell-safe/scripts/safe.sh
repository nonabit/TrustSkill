#!/bin/bash
# 安全的 Shell 代码

# 安全的命令
echo "Hello World"
ls -la
pwd

# 安全的命令替换（获取日期）
current_date=$(date +%Y-%m-%d)
echo "Today is: $current_date"

# 安全的变量使用
name="John"
echo "Hello, $name"

# 安全的条件判断
if [ -f "file.txt" ]; then
    echo "File exists"
fi
