"""Message formats for node communication"""

import json
from enum import Enum
from typing import Optional


class MessageType(Enum):
    # Client messages
    WRITE = "WRITE"
    GUESS = "GUESS"
    READ = "READ"
    
    # Node-to-node messages
    PROPOSE = "PROPOSE"
    ACK = "ACK"
    COMMIT = "COMMIT"
    HEARTBEAT = "HEARTBEAT"
    ELECTION = "ELECTION"
    VOTE = "VOTE"
    FORWARD = "FORWARD"
    
    # Responses
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"


class Message:
    """Message format: TYPE|epoch|seq|op|value|from"""
    
    def __init__(self, msg_type: MessageType, epoch: int = 0, seq: int = 0,
                 op: str = "", value: str = "", from_node: str = ""):
        self.type = msg_type
        self.epoch = epoch
        self.seq = seq
        self.op = op
        self.value = value
        self.from_node = from_node
    
    def to_string(self) -> str:
        """Serialize message to string format"""
        return f"{self.type.value}|{self.epoch}|{self.seq}|{self.op}|{self.value}|{self.from_node}"
    
    @staticmethod
    def from_string(msg_str: str) -> 'Message':
        """Parse message from string format"""
        parts = msg_str.strip().split("|")
        if len(parts) < 6:
            raise ValueError(f"Invalid message format: {msg_str}")
        
        msg_type = MessageType(parts[0])
        epoch = int(parts[1]) if parts[1] else 0
        seq = int(parts[2]) if parts[2] else 0
        op = parts[3]
        value = parts[4]
        from_node = parts[5]
        
        return Message(msg_type, epoch, seq, op, value, from_node)
    
    def to_json(self) -> str:
        """Serialize message to JSON format"""
        return json.dumps({
            "type": self.type.value,
            "epoch": self.epoch,
            "seq": self.seq,
            "op": self.op,
            "value": self.value,
            "from_node": self.from_node
        })
    
    @staticmethod
    def from_json(json_str: str) -> 'Message':
        """Parse message from JSON format"""
        data = json.loads(json_str)
        return Message(
            MessageType(data["type"]),
            data.get("epoch", 0),
            data.get("seq", 0),
            data.get("op", ""),
            data.get("value", ""),
            data.get("from_node", "")
        )

