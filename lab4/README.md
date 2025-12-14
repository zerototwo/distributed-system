# Lab 4: ZooKeeper-like Distributed System

A simplified ZooKeeper-like system with leader election, log replication, and a distributed number guessing game.

## System Architecture

- **5 Nodes**: node1, node2, node3, node4, node5 (1 Leader + 4 Followers)
- **Up to 5 Clients**: Can connect to any node
- **ZAB Protocol**: Proposal → ACK → Commit
- **Leader Election**: Bully algorithm with (epoch, seq, node_id) comparison

## Components

- `node.py`: Node server (Leader/Follower)
- `client.py`: Client application
- `log_store.py`: Persistent log storage using SQLite
- `message.py`: Message format definitions
- `config.py`: System configuration

## Game Rules

1. First client sets the target (0-100) using `write`
2. Other clients submit guesses using `guess`
3. Leader finds the closest guess and commits it as the new target
4. New round begins when a client sets the next target

## How to Run

### Start Nodes

#### Option 1: Start nodes individually (recommended for testing)

Open 5 terminal windows and run:

```bash
# Terminal 1
python start_node.py --node-id node1

# Terminal 2
python start_node.py --node-id node2

# Terminal 3
python start_node.py --node-id node3

# Terminal 4
python start_node.py --node-id node4

# Terminal 5
python start_node.py --node-id node5
```

#### Option 2: Start all nodes at once

```bash
python start_all_nodes.py
```

### Run Clients

Open new terminal windows for clients:

```bash
# Client 1: Set initial target
python client.py --client-id client1 --node node1 --command write --value 50

# Client 2: Read current target
python client.py --client-id client2 --node node2 --command read

# Client 3: Submit a guess
python client.py --client-id client3 --node node3 --command guess --value 45

# Client 4: Submit another guess
python client.py --client-id client4 --node node4 --command guess --value 55

# Client 5: Submit another guess
python client.py --client-id client5 --node node5 --command guess --value 60

# Client 1: Set new target (this will trigger processing of guesses)
python client.py --client-id client1 --node node1 --command write --value 75
```

## Testing Scenarios

### 1. Normal Flow
- Write → Quorum → Commit
- All clients should see the new target

### 2. Guessing Flow
- Multiple clients submit guesses
- Leader processes guesses and commits the closest one
- New target is visible to all nodes

### 3. Leader Crash and Recovery
- Kill the leader process (Ctrl+C)
- System will elect a new leader
- New leader syncs logs and continues operations

## Simulating Leader Crash

1. Start all 5 nodes
2. Run some operations (write, guess)
3. Kill the leader process (find which node is leader from logs)
4. Wait for election (should happen automatically)
5. Continue operations - system should work normally

## Files Generated

- `logs_<node_id>.db`: SQLite database files for each node's log
- These can be deleted to reset the system state

## Configuration

Edit `config.py` to modify:
- Node ports and addresses
- Quorum size
- Heartbeat intervals
- Timeouts

