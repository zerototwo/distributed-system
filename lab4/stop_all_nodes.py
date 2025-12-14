#!/usr/bin/env python3
"""Stop all running node processes"""

import subprocess
import sys
import os
import signal
import time

def find_node_processes():
    """Find all running start_node.py processes"""
    try:
        # Find all python processes running start_node.py
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        
        processes = []
        for line in result.stdout.split('\n'):
            if 'start_node.py' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = int(parts[1])
                    processes.append(pid)
        
        return processes
    except Exception as e:
        print(f"Error finding processes: {e}")
        return []

def stop_nodes():
    """Stop all node processes"""
    processes = find_node_processes()
    
    if not processes:
        print("没有找到运行中的节点进程")
        return
    
    print(f"找到 {len(processes)} 个节点进程: {processes}")
    
    # Stop processes gracefully
    for pid in processes:
        try:
            print(f"停止进程 {pid}...")
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            print(f"进程 {pid} 已不存在")
        except Exception as e:
            print(f"无法停止进程 {pid}: {e}")
    
    # Wait a bit
    time.sleep(1)
    
    # Check if any are still running
    remaining = find_node_processes()
    if remaining:
        print(f"强制停止剩余进程: {remaining}")
        for pid in remaining:
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception as e:
                print(f"无法强制停止进程 {pid}: {e}")
        time.sleep(0.5)
    
    # Final check
    final = find_node_processes()
    if final:
        print(f"警告: 以下进程仍在运行: {final}")
    else:
        print("✓ 所有节点已停止")
    
    # Ask about cleaning log files
    try:
        response = input("\n是否删除所有日志数据库文件? (y/N): ").strip().lower()
        if response == 'y':
            import glob
            log_files = glob.glob('logs_*.db')
            for log_file in log_files:
                try:
                    os.remove(log_file)
                    print(f"已删除: {log_file}")
                except Exception as e:
                    print(f"无法删除 {log_file}: {e}")
            if log_files:
                print("✓ 已删除所有日志文件")
            else:
                print("没有找到日志文件")
    except KeyboardInterrupt:
        print("\n取消")

if __name__ == '__main__':
    try:
        stop_nodes()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)

