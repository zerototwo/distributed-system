#!/usr/bin/env python3
"""Detailed test that captures output and analyzes leader election"""

import subprocess
import time
import sys
import os
import glob
import threading
import queue

def capture_output(proc, node_id, output_queue):
    """Capture output from a process"""
    try:
        for line in iter(proc.stdout.readline, ''):
            if line:
                output_queue.put((node_id, line.strip()))
    except:
        pass

def main():
    print("=" * 70)
    print("DETAILED LEADER ELECTION TEST")
    print("=" * 70)
    
    # Cleanup
    for log_file in glob.glob('logs_*.db'):
        try:
            os.remove(log_file)
        except:
            pass
    
    processes = []
    output_queue = queue.Queue()
    threads = []
    
    try:
        # Start nodes with unbuffered output
        print("\nStarting nodes...")
        for node_id in ['node1', 'node2', 'node3', 'node4', 'node5']:
            # Use unbuffered Python and redirect to file for reliability
            log_file = f"test_output_{node_id}.log"
            with open(log_file, 'w') as f:
                proc = subprocess.Popen(
                    [sys.executable, '-u', 'start_node.py', '--node-id', node_id],
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            processes.append((node_id, proc, log_file))
            time.sleep(0.8)
        
        print("Nodes started. Waiting 20 seconds and analyzing logs...\n")
        
        # Wait for election
        time.sleep(20)
        
        # Read log files
        start_time = time.time()
        leader_found = set()
        election_events = []
        
        for node_id, proc, log_file in processes:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                # Check for leader
                                if "Becoming LEADER" in line:
                                    leader_found.add(node_id)
                                    election_events.append((node_id, line, 0))
                                elif "Election succeeded" in line:
                                    election_events.append((node_id, line, 0))
                                elif "Election failed" in line:
                                    election_events.append((node_id, line, 0))
                                elif "Starting election" in line:
                                    election_events.append((node_id, line, 0))
                                elif "VOTING" in line or "REJECTING" in line:
                                    election_events.append((node_id, line, 0))
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")
        
        # Final analysis
        print("\n" + "=" * 70)
        print("ANALYSIS")
        print("=" * 70)
        
        if len(leader_found) == 0:
            print("❌ NO LEADER ELECTED")
            print("\nElection events found:")
            for node_id, event, timestamp in election_events:
                print(f"  {timestamp:.1f}s: [{node_id}] {event}")
        elif len(leader_found) == 1:
            leader = list(leader_found)[0]
            print(f"✅ SUCCESS: {leader} is the LEADER")
            print(f"\nElection timeline:")
            for node_id, event, timestamp in election_events:
                marker = "★" if node_id == leader and "LEADER" in event else " "
                print(f"  {marker} {timestamp:.1f}s: [{node_id}] {event}")
        else:
            print(f"❌ SPLIT-BRAIN: {len(leader_found)} nodes claim to be leader:")
            for leader in leader_found:
                print(f"  - {leader}")
            print(f"\nElection events:")
            for node_id, event, timestamp in election_events:
                marker = "⚠" if node_id in leader_found else " "
                print(f"  {marker} {timestamp:.1f}s: [{node_id}] {event}")
        
        print("=" * 70)
        
        return len(leader_found) == 1
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
        return False
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\nStopping nodes...")
        for item in processes:
            if len(item) == 3:
                node_id, proc, log_file = item
            else:
                node_id, proc = item
                log_file = None
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except:
                try:
                    proc.kill()
                except:
                    pass
            # Clean up log file
            if log_file and os.path.exists(log_file):
                try:
                    os.remove(log_file)
                except:
                    pass

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

