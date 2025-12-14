"""Client application for the distributed game"""

import socket
import sys
import argparse
from message import Message, MessageType
from config import NODES, MIN_TARGET, MAX_TARGET


class ClientApp:
    """Client for interacting with the distributed game"""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.connected_node = None
        self.node_host = None
        self.node_port = None
    
    def connect(self, node_id: str):
        """Connect to a node"""
        if node_id not in NODES:
            print(f"Error: Unknown node {node_id}")
            return False
        
        node_info = NODES[node_id]
        self.node_host = node_info["host"]
        self.node_port = node_info["port"]
        self.connected_node = node_id
        
        print(f"[Client {self.client_id}] Connected to {node_id} at {self.node_host}:{self.node_port}")
        return True
    
    def _send_request(self, msg: Message) -> Message:
        """Send a request and wait for response"""
        if not self.node_host or not self.node_port:
            print("Error: Not connected to any node")
            return None
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.node_host, self.node_port))
            
            sock.sendall(msg.to_string().encode('utf-8'))
            
            data = sock.recv(4096)
            sock.close()
            
            if data:
                response = Message.from_string(data.decode('utf-8'))
                return response
            return None
        except Exception as e:
            print(f"Error sending request: {e}")
            return None
    
    def write(self, value: int) -> bool:
        """Write (set target)"""
        if value < MIN_TARGET or value > MAX_TARGET:
            print(f"Error: Value must be between {MIN_TARGET} and {MAX_TARGET}")
            return False
        
        msg = Message(
            MessageType.WRITE,
            value=str(value),
            from_node=self.client_id
        )
        
        response = self._send_request(msg)
        if response:
            if response.type == MessageType.RESPONSE:
                print(f"[Client {self.client_id}] Write successful: target = {value}")
                return True
            elif response.type == MessageType.ERROR:
                print(f"[Client {self.client_id}] Write failed: {response.value}")
                return False
        else:
            print(f"[Client {self.client_id}] No response from server")
            return False
    
    def guess(self, value: int) -> bool:
        """Submit a guess"""
        if value < MIN_TARGET or value > MAX_TARGET:
            print(f"Error: Guess must be between {MIN_TARGET} and {MAX_TARGET}")
            return False
        
        msg = Message(
            MessageType.GUESS,
            value=str(value),
            from_node=self.client_id
        )
        
        response = self._send_request(msg)
        if response:
            if response.type == MessageType.RESPONSE:
                print(f"[Client {self.client_id}] Guess submitted: {value}")
                return True
            elif response.type == MessageType.ERROR:
                print(f"[Client {self.client_id}] Guess failed: {response.value}")
                return False
        else:
            print(f"[Client {self.client_id}] No response from server")
            return False
    
    def read(self) -> int:
        """Read current target"""
        msg = Message(
            MessageType.READ,
            from_node=self.client_id
        )
        
        response = self._send_request(msg)
        if response and response.type == MessageType.RESPONSE:
            try:
                if response.value == "No target set":
                    print(f"[Client {self.client_id}] No target set yet")
                    return None
                target = int(response.value)
                print(f"[Client {self.client_id}] Current target: {target}")
                return target
            except ValueError:
                print(f"[Client {self.client_id}] Invalid target value: {response.value}")
                return None
        else:
            print(f"[Client {self.client_id}] Failed to read target")
            return None


def main():
    parser = argparse.ArgumentParser(description='Distributed Game Client')
    parser.add_argument('--client-id', type=str, required=True, help='Client ID')
    parser.add_argument('--node', type=str, default='node1', help='Node to connect to (default: node1)')
    parser.add_argument('--command', type=str, choices=['write', 'guess', 'read'], required=True, help='Command to execute')
    parser.add_argument('--value', type=int, help='Value for write/guess command')
    
    args = parser.parse_args()
    
    client = ClientApp(args.client_id)
    
    if not client.connect(args.node):
        sys.exit(1)
    
    if args.command == 'write':
        if args.value is None:
            print("Error: --value required for write command")
            sys.exit(1)
        client.write(args.value)
    elif args.command == 'guess':
        if args.value is None:
            print("Error: --value required for guess command")
            sys.exit(1)
        client.guess(args.value)
    elif args.command == 'read':
        client.read()


if __name__ == '__main__':
    main()

