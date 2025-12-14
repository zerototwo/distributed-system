#!/bin/bash

# 停止所有节点进程的脚本

echo "正在停止所有节点..."

# 查找所有运行中的start_node.py进程
PIDS=$(ps aux | grep "start_node.py" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "没有找到运行中的节点进程"
    exit 0
fi

# 停止所有找到的进程
for PID in $PIDS; do
    echo "停止进程 $PID (start_node.py)"
    kill $PID 2>/dev/null
done

# 等待进程结束
sleep 1

# 检查是否还有进程在运行
REMAINING=$(ps aux | grep "start_node.py" | grep -v grep | awk '{print $2}')

if [ -z "$REMAINING" ]; then
    echo "✓ 所有节点已停止"
else
    echo "警告: 以下进程仍在运行，强制停止..."
    for PID in $REMAINING; do
        echo "强制停止进程 $PID"
        kill -9 $PID 2>/dev/null
    done
    sleep 1
    echo "✓ 所有节点已强制停止"
fi

# 清理日志文件（可选）
read -p "是否删除所有日志数据库文件? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f logs_*.db
    echo "✓ 已删除所有日志文件"
fi

