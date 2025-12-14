"""Start all nodes in separate processes"""

import subprocess
import sys
import time
from config import NODES


def main():
    processes = []
    
    print("Starting all nodes...")
    
    # Start all nodes
    for node_id in NODES.keys():
        print(f"Starting {node_id}...")
        proc = subprocess.Popen(
            [sys.executable, 'start_node.py', '--node-id', node_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append((node_id, proc))
        time.sleep(0.5)  # Small delay between starts
    
    print("\nAll nodes started. Press Ctrl+C to stop all nodes.")
    print("Node outputs are redirected to separate files.")
    
    try:
        # Wait for all processes
        for node_id, proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down all nodes...")
        for node_id, proc in processes:
            proc.terminate()
            proc.wait()
        print("All nodes stopped.")


if __name__ == '__main__':
    main()

