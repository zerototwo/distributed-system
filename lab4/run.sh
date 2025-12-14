#!/bin/bash

# 启动脚本 - 在5个终端窗口中启动5个节点
# 使用方法: ./run.sh

echo "启动ZooKeeper-like分布式系统"
echo "================================"
echo ""
echo "这个脚本会在5个终端窗口中启动5个节点"
echo "每个节点会在独立的终端窗口中运行"
echo ""

# 检查是否在正确的目录
if [ ! -f "start_node.py" ]; then
    echo "错误: 请在lab4目录下运行此脚本"
    exit 1
fi

# 获取当前目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 在macOS上打开新的终端窗口
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "在macOS上启动节点..."
    
    # 启动node1
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && python3 start_node.py --node-id node1\""
    sleep 1
    
    # 启动node2
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && python3 start_node.py --node-id node2\""
    sleep 1
    
    # 启动node3
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && python3 start_node.py --node-id node3\""
    sleep 1
    
    # 启动node4
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && python3 start_node.py --node-id node4\""
    sleep 1
    
    # 启动node5
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && python3 start_node.py --node-id node5\""
    
    echo ""
    echo "所有节点已启动！"
    echo "每个节点都在独立的终端窗口中运行"
    echo ""
    echo "现在可以在新的终端窗口中运行客户端命令："
    echo "  python3 client.py --client-id client1 --node node1 --command write --value 50"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "在Linux上启动节点..."
    # Linux可以使用gnome-terminal或xterm
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && python3 start_node.py --node-id node1; exec bash"
        sleep 1
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && python3 start_node.py --node-id node2; exec bash"
        sleep 1
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && python3 start_node.py --node-id node3; exec bash"
        sleep 1
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && python3 start_node.py --node-id node4; exec bash"
        sleep 1
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && python3 start_node.py --node-id node5; exec bash"
        echo "所有节点已启动！"
    else
        echo "错误: 未找到gnome-terminal，请手动启动节点"
    fi
else
    echo "不支持的操作系统，请手动启动节点"
    echo "运行以下命令："
    for i in {1..5}; do
        echo "  python3 start_node.py --node-id node$i"
    done
fi

