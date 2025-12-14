"""Demo script to test the distributed system"""

import time
import subprocess
import sys
from client import ClientApp


def demo_normal_flow():
    """Demo 1: Normal flow - write → quorum → commit"""
    print("\n=== Demo 1: Normal Flow ===")
    print("Testing: write → quorum → commit\n")
    
    client1 = ClientApp("client1")
    client1.connect("node1")
    
    # Write initial target
    print("Step 1: Client 1 writes target = 50")
    client1.write(50)
    time.sleep(1)
    
    # Read from different nodes
    print("\nStep 2: Reading from different nodes...")
    client2 = ClientApp("client2")
    client2.connect("node2")
    client2.read()
    
    client3 = ClientApp("client3")
    client3.connect("node3")
    client3.read()


def demo_guessing_flow():
    """Demo 2: Guessing flow - multiple guesses → leader chooses closest"""
    print("\n=== Demo 2: Guessing Flow ===")
    print("Testing: multiple guesses → leader chooses closest → commit\n")
    
    # Set initial target
    client1 = ClientApp("client1")
    client1.connect("node1")
    print("Step 1: Client 1 sets initial target = 50")
    client1.write(50)
    time.sleep(2)  # Wait for commit
    
    # Submit guesses
    print("\nStep 2: Multiple clients submit guesses...")
    client2 = ClientApp("client2")
    client2.connect("node2")
    client2.guess(45)
    time.sleep(0.5)
    
    client3 = ClientApp("client3")
    client3.connect("node3")
    client3.guess(55)
    time.sleep(0.5)
    
    client4 = ClientApp("client4")
    client4.connect("node4")
    client4.guess(60)
    time.sleep(0.5)
    
    client5 = ClientApp("client5")
    client5.connect("node5")
    client5.guess(48)
    time.sleep(2)  # Wait for processing
    
    # Trigger processing by writing new target
    print("\nStep 3: Client 1 writes new target (triggers guess processing)")
    client1.write(75)
    time.sleep(2)
    
    # Read final target
    print("\nStep 4: Reading final target from all nodes...")
    client2.read()
    client3.read()
    client4.read()


def main():
    print("ZooKeeper-like Distributed System Demo")
    print("=" * 50)
    print("\nMake sure all nodes are running before starting the demo!")
    print("Start nodes with: python start_node.py --node-id node1 (for each node)")
    print("\nPress Enter to continue or Ctrl+C to exit...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nDemo cancelled.")
        sys.exit(0)
    
    try:
        demo_normal_flow()
        time.sleep(3)
        demo_guessing_flow()
        
        print("\n" + "=" * 50)
        print("Demo completed!")
        print("\nNote: Leader crash and recovery demo requires manual testing:")
        print("1. Start all nodes")
        print("2. Run some operations")
        print("3. Kill the leader process (Ctrl+C)")
        print("4. Wait for election")
        print("5. Continue operations")
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Make sure all nodes are running!")


if __name__ == '__main__':
    main()

