"""Configuration for the distributed system"""

# Node configuration
NODES = {
    "node1": {"host": "localhost", "port": 5001, "id": 1},
    "node2": {"host": "localhost", "port": 5002, "id": 2},
    "node3": {"host": "localhost", "port": 5003, "id": 3},
    "node4": {"host": "localhost", "port": 5004, "id": 4},
    "node5": {"host": "localhost", "port": 5005, "id": 5},
}

# System parameters
QUORUM_SIZE = 3  # Majority of 5 nodes
HEARTBEAT_INTERVAL = 1  # seconds (send heartbeat every second)
HEARTBEAT_TIMEOUT = 3  # seconds (timeout if no heartbeat for 3 seconds)
ELECTION_TIMEOUT_MIN = 6  # seconds
ELECTION_TIMEOUT_MAX = 10  # seconds
ELECTION_DURATION = 2  # seconds - maximum time for an election to complete (strict limit)
ACK_TIMEOUT = 5  # seconds

# Game parameters
MIN_TARGET = 0
MAX_TARGET = 100

