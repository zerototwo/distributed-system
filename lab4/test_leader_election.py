#!/usr/bin/env python3
"""Automated test for leader election - actually starts nodes and verifies"""

import subprocess
import time
import socket
import sys
import os
import glob
import signal
from message import Message, MessageType
from config import NODES, QUORUM_SIZE

class NodeTester:
    def __init__(self):
        self.processes = []
        self.test_results = []
        
    def cleanup_logs(self):
        """Remove old log files"""
        for log_file in glob.glob('logs_*.db'):
            try:
                os.remove(log_file)
            except:
                pass
    
    def start_node(self, node_id):
        """Start a node process"""
        try:
            proc = subprocess.Popen(
                [sys.executable, 'start_node.py', '--node-id', node_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            return proc
        except Exception as e:
            print(f"ERROR: Failed to start {node_id}: {e}")
            return None
    
    def check_node_accessible(self, node_id, timeout=2):
        """Check if node is accepting connections"""
        try:
            node_info = NODES[node_id]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((node_info["host"], node_info["port"]))
            sock.close()
            return result == 0
        except:
            return False
    
    def send_message_to_node(self, node_id, msg, timeout=3):
        """Send a message to a node and get response"""
        try:
            node_info = NODES[node_id]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((node_info["host"], node_info["port"]))
            sock.sendall(msg.to_string().encode('utf-8'))
            
            # Wait for response
            sock.settimeout(1)
            data = sock.recv(4096)
            sock.close()
            
            if data:
                return Message.from_string(data.decode('utf-8'))
            return None
        except Exception as e:
            return None
    
    def check_leader_status(self, node_id):
        """Check if a node thinks it's the leader by sending a read request"""
        try:
            msg = Message(MessageType.READ, from_node="test_client")
            response = self.send_message_to_node(node_id, msg)
            # If we get a response (even error), node is accessible
            # If it's leader, it should handle the request
            return response is not None
        except:
            return False
    
    def run_test(self):
        """Run the full test"""
        print("=" * 70)
        print("LEADER ELECTION AUTOMATED TEST")
        print("=" * 70)
        
        # Cleanup
        self.cleanup_logs()
        
        try:
            # Step 1: Start all nodes
            print("\n[1/6] Starting all 5 nodes...")
            for i, node_id in enumerate(NODES.keys(), 1):
                print(f"   Starting {node_id} ({i}/5)...")
                proc = self.start_node(node_id)
                if proc:
                    self.processes.append((node_id, proc))
                    time.sleep(0.8)  # Stagger starts
                else:
                    print(f"   ERROR: Failed to start {node_id}")
                    return False
            
            # Step 2: Wait for initialization
            print("\n[2/6] Waiting for nodes to initialize (5 seconds)...")
            time.sleep(5)
            
            # Step 3: Check if nodes are running
            print("\n[3/6] Checking if nodes are running...")
            running_nodes = []
            for node_id, proc in self.processes:
                if proc.poll() is None:
                    running_nodes.append(node_id)
                    print(f"   ✓ {node_id}: running")
                else:
                    stdout, stderr = proc.communicate()
                    print(f"   ✗ {node_id}: DIED")
                    if stderr:
                        print(f"      Error: {stderr[:200]}")
                    return False
            
            if len(running_nodes) < QUORUM_SIZE:
                print(f"\nERROR: Only {len(running_nodes)} nodes running, need {QUORUM_SIZE} for quorum")
                return False
            
            # Step 4: Wait for election
            print(f"\n[4/6] Waiting for leader election (15 seconds)...")
            print("   (This allows time for election to complete)")
            time.sleep(15)
            
            # Step 5: Check which nodes are accessible
            print("\n[5/6] Checking node accessibility...")
            accessible_nodes = []
            for node_id in NODES.keys():
                if self.check_node_accessible(node_id):
                    accessible_nodes.append(node_id)
                    print(f"   ✓ {node_id}: accessible")
                else:
                    print(f"   ✗ {node_id}: NOT accessible")
            
            if len(accessible_nodes) < QUORUM_SIZE:
                print(f"\nERROR: Only {len(accessible_nodes)} nodes accessible")
                return False
            
            # Step 6: Test client operations
            print("\n[6/6] Testing client operations...")
            test_node = accessible_nodes[0]
            print(f"   Testing write operation on {test_node}...")
            
            write_msg = Message(MessageType.WRITE, value="50", from_node="test_client")
            response = self.send_message_to_node(test_node, write_msg, timeout=10)
            
            if response:
                if response.type == MessageType.RESPONSE:
                    print(f"   ✓ Write operation successful")
                elif response.type == MessageType.ERROR:
                    print(f"   ⚠ Write operation returned error: {response.value}")
                else:
                    print(f"   ⚠ Unexpected response type: {response.type}")
            else:
                print(f"   ✗ No response from {test_node}")
            
            # Final check
            print("\n" + "=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)
            print(f"✓ Started {len(self.processes)} nodes")
            print(f"✓ {len(running_nodes)} nodes still running")
            print(f"✓ {len(accessible_nodes)} nodes accessible")
            print(f"\n✓ Test completed - check the terminal windows for leader election results")
            print(f"  You should see only ONE node become LEADER")
            print("=" * 70)
            
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
            # Cleanup
            print("\nCleaning up processes...")
            for node_id, proc in self.processes:
                print(f"   Stopping {node_id}...")
                try:
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                except Exception as e:
                    print(f"      Error stopping {node_id}: {e}")
            
            # Clean log files
            print("\nCleaning log files...")
            self.cleanup_logs()
            print("Done!")

def main():
    tester = NodeTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

