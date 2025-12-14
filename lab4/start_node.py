"""Start a node server"""

import sys
import argparse
from node import NodeServer
from config import NODES


def main():
    parser = argparse.ArgumentParser(description='Start a node server')
    parser.add_argument('--node-id', type=str, required=True, 
                       choices=list(NODES.keys()), 
                       help='Node ID to start')
    
    args = parser.parse_args()
    
    if args.node_id not in NODES:
        print(f"Error: Invalid node ID {args.node_id}")
        print(f"Valid node IDs: {list(NODES.keys())}")
        sys.exit(1)
    
    node = NodeServer(args.node_id)
    
    try:
        node.start()
    except KeyboardInterrupt:
        print(f"\n[{args.node_id}] Shutting down...")
        node.stop()
        sys.exit(0)


if __name__ == '__main__':
    main()

