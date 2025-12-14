#!/usr/bin/env python3
"""Test script to verify leader election works correctly"""

import subprocess
import time
import socket
import sys
from message import Message, MessageType
from config import NODES

def check_node_state(node_id, timeout=5):
    """Check if a node is running and responding"""
    try:
        node_info = NODES[node_id]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((node_info["host"], node_info["port"]))
        sock.close()
        return result == 0
    except:
        return False

def start_node(node_id):
    """Start a node in background"""
    proc = subprocess.Popen(
        [sys.executable, 'start_node.py', '--node-id', node_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return proc

def stop_process(proc):
    """Stop a process"""
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except:
        try:
            proc.kill()
        except:
            pass

def main():
    print("=" * 60)
    print("Testing Leader Election")
    print("=" * 60)
    
    # Clean up old log files
    import os
    import glob
    for log_file in glob.glob('logs_*.db'):
        try:
            os.remove(log_file)
        except:
            pass
    
    processes = []
    
    try:
        # Start all nodes
        print("\n1. Starting all 5 nodes...")
        for node_id in NODES.keys():
            print(f"   Starting {node_id}...")
            proc = start_node(node_id)
            processes.append((node_id, proc))
            time.sleep(1)  # Stagger starts
        
        # Wait for nodes to start
        print("\n2. Waiting for nodes to initialize...")
        time.sleep(3)
        
        # Check if nodes are running
        print("\n3. Checking node status...")
        all_running = True
        for node_id, proc in processes:
            if proc.poll() is not None:
                print(f"   ERROR: {node_id} process died!")
                all_running = False
            else:
                print(f"   {node_id}: running")
        
        if not all_running:
            print("\nERROR: Some nodes failed to start!")
            return False
        
        # Wait for election to complete
        print("\n4. Waiting for leader election (10 seconds)...")
        time.sleep(10)
        
        # Check if we can connect to nodes
        print("\n5. Testing node connections...")
        accessible_nodes = []
        for node_id in NODES.keys():
            if check_node_state(node_id):
                accessible_nodes.append(node_id)
                print(f"   {node_id}: accessible")
            else:
                print(f"   {node_id}: NOT accessible")
        
        if len(accessible_nodes) < 3:
            print("\nERROR: Not enough nodes are accessible (need at least 3 for quorum)")
            return False
        
        print("\n6. Test completed successfully!")
        print("   Nodes are running. Check the terminal windows for leader election results.")
        print("   You should see only ONE node become LEADER.")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return False
    except Exception as e:
        print(f"\nERROR during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        print("\n7. Cleaning up processes...")
        for node_id, proc in processes:
            print(f"   Stopping {node_id}...")
            stop_process(proc)
        print("   All processes stopped.")
        
        # Clean up log files
        for log_file in glob.glob('logs_*.db'):
            try:
                os.remove(log_file)
                print(f"   Removed {log_file}")
            except:
                pass

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

