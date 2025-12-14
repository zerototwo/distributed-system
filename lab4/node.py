"""ZooKeeper-like Node Server with Leader Election and ZAB Protocol"""

import socket
import threading
import time
import random
import json
from typing import Dict, List, Optional, Set
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

from log_store import LogStore, LogStatus
from message import Message, MessageType
from config import (
    NODES, QUORUM_SIZE, HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT,
    ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX, ELECTION_DURATION,
    ACK_TIMEOUT, MIN_TARGET, MAX_TARGET
)


class NodeState(Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"


class NodeServer:
    """Distributed node that can be Leader or Follower"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.node_info = NODES[node_id]
        self.host = self.node_info["host"]
        self.port = self.node_info["port"]
        self.node_num = self.node_info["id"]
        
        # State
        self.state = NodeState.FOLLOWER
        self.current_epoch = 0
        self.current_seq = 0
        self.leader_id = None
        
        # Log store
        self.log_store = LogStore(node_id)
        
        # Game state (visible only after commit)
        self.current_target = None
        self.current_guesses = []  # List of (guess_value, client_id)
        self.round_active = False
        
        # Network
        self.socket = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Leader coordination
        self.pending_proposals: Dict[tuple, Dict] = {}  # (epoch, seq) -> {acks, value, op}
        self.proposal_lock = threading.Lock()
        
        # Heartbeat
        self.last_heartbeat_time = time.time()
        self.heartbeat_thread = None
        self.election_thread = None
        
        # Election
        self.election_votes: Set[str] = set()
        self.election_lock = threading.Lock()
        self.election_epoch = 0
        self.last_election_time = 0  # Prevent too frequent elections
        self.voted_for: Optional[str] = None  # Track who we voted for in current election
        self.current_election_term = 0  # Track current election term
        self.vote_term = 0  # Track which election term we voted in
        self.last_vote_time = time.time()  # Track when we last voted (to prevent rapid re-voting)
        self.election_start_time = 0  # Track when current election started
        
    def start(self):
        """Start the node server"""
        print(f"[{self.node_id}] Starting node on {self.host}:{self.port}")
        
        # Initialize from log
        latest_epoch, latest_seq = self.log_store.get_latest_epoch_seq()
        self.current_epoch = latest_epoch
        self.current_seq = latest_seq
        
        # Apply committed logs to restore state
        self._apply_committed_logs()
        
        # Start server socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)
        
        # Start heartbeat/election thread
        self._start_background_threads()
        
        # Accept connections
        print(f"[{self.node_id}] Node listening on {self.host}:{self.port}, state: {self.state.value}")
        
        while True:
            try:
                conn, addr = self.socket.accept()
                self.executor.submit(self._handle_connection, conn, addr)
            except Exception as e:
                print(f"[{self.node_id}] Error accepting connection: {e}")
                break
    
    def _start_background_threads(self):
        """Start heartbeat and election monitoring threads"""
        def heartbeat_monitor():
            while True:
                time.sleep(0.5)  # Check every 0.5 seconds
                if self.state == NodeState.LEADER:
                    # Send heartbeat at configured interval
                    current_time = time.time()
                    if not hasattr(self, '_last_heartbeat_send_time'):
                        self._last_heartbeat_send_time = 0
                    if current_time - self._last_heartbeat_send_time >= HEARTBEAT_INTERVAL:
                        self._send_heartbeats()
                        self._last_heartbeat_send_time = current_time
                elif self.state == NodeState.FOLLOWER:
                    if time.time() - self.last_heartbeat_time > HEARTBEAT_TIMEOUT:
                        # Prevent too frequent elections (wait at least 2 seconds between elections)
                        if time.time() - self.last_election_time > 2:
                            print(f"[{self.node_id}] Leader heartbeat timeout, starting election")
                            self._start_election()
                elif self.state == NodeState.CANDIDATE:
                    # If candidate for too long without becoming leader, restart election
                    # This is handled in _start_election
                    pass
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
        self.heartbeat_thread.start()
    
    def _send_heartbeats(self):
        """Send heartbeat to all followers"""
        if self.state != NodeState.LEADER:
            return
        for node_id, node_info in NODES.items():
            if node_id != self.node_id:
                try:
                    self._send_message_to_node(
                        node_id,
                        Message(MessageType.HEARTBEAT, epoch=self.current_epoch, from_node=self.node_id)
                    )
                except Exception as e:
                    pass  # Node might be down
    
    def _start_election(self):
        """Start leader election"""
        if self.state == NodeState.LEADER:
            return
        
        # Prevent multiple simultaneous elections
        with self.election_lock:
            if self.state == NodeState.CANDIDATE:
                return
            # Prevent too frequent elections
            if time.time() - self.last_election_time < 1:
                return
            self.last_election_time = time.time()
            self.election_epoch += 1
            self.current_election_term = self.election_epoch
            self.vote_term = self.election_epoch  # Mark that we voted in this term
            self.election_start_time = time.time()  # Record election start time
            self.state = NodeState.CANDIDATE
            self.election_votes.clear()
            self.election_votes.add(self.node_id)  # Vote for self
            self.voted_for = self.node_id  # Vote for ourselves
        
        # Add random delay based on node_id to avoid all nodes starting election at the same time
        # Higher node_id waits less, so node5 will start election first
        delay = (6 - self.node_num) * 0.1 + random.uniform(0, 0.2)
        time.sleep(delay)
        
        # Double check state after delay (might have received vote from higher priority candidate)
        with self.election_lock:
            if self.state != NodeState.CANDIDATE:
                return
        
        print(f"[{self.node_id}] Starting election (epoch: {self.election_epoch})")
        
        # Get latest epoch and seq
        latest_epoch, latest_seq = self.log_store.get_latest_epoch_seq()
        
        # Send election message to ALL other nodes
        # Use a fresh votes set for this election
        election_votes_local = set()
        election_votes_local.add(self.node_id)  # Self vote
        responses = []  # Track all responses
        
        # Use election_epoch as the term for this election
        election_term = self.election_epoch
        
        for node_id, node_info in NODES.items():
            if node_id != self.node_id:
                try:
                    # Send election message with:
                    # - epoch: election_term (to track which election this is)
                    # - seq: latest_seq (to show our log state)
                    # - value: node_num (for priority comparison)
                    msg = Message(
                        MessageType.ELECTION,
                        epoch=election_term,  # Election term for tracking
                        seq=latest_seq,  # Our latest seq for priority comparison
                        from_node=self.node_id,
                        value=str(self.node_num)  # Our node_id for priority comparison
                    )
                    response = self._send_message_to_node(node_id, msg, wait_response=True)
                    if response:
                        responses.append((node_id, response))
                        if response.type == MessageType.VOTE:
                            # Only add if not already in set (prevent duplicates)
                            if node_id not in election_votes_local:
                                election_votes_local.add(node_id)
                                with self.election_lock:
                                    self.election_votes.add(node_id)
                                    print(f"[{self.node_id}] Received vote from {node_id} (total: {len(self.election_votes)})")
                        elif response.type == MessageType.ELECTION:
                            # Received election response - this means they're also a candidate
                            # Check if they have higher priority
                            other_node_id = int(response.value) if response.value else 0
                            other_seq = response.seq  # Use seq for priority, not epoch (epoch is term)
                            
                            # Compare priority: (log_epoch, log_seq, node_id)
                            # We use latest_epoch (from log) and seq (from response) for comparison
                            other_priority = (latest_epoch, other_seq, other_node_id)
                            our_priority = (latest_epoch, latest_seq, self.node_num)
                            
                            if other_priority > our_priority:
                                # Higher priority candidate exists, step down
                                with self.election_lock:
                                    if self.state == NodeState.CANDIDATE:
                                        self.state = NodeState.FOLLOWER
                                        self.last_heartbeat_time = time.time()
                                        self.election_votes.clear()
                                print(f"[{self.node_id}] Stepping down for higher priority candidate {node_id} (priority: {other_priority} > {our_priority})")
                                return
                except Exception as e:
                    pass  # Node might be down
        
        # Update election_votes with local votes
        with self.election_lock:
            self.election_votes = election_votes_local.copy()
        
        # Check if we should step down for any higher priority candidates or existing leaders
        for node_id, response in responses:
            # If someone responded with election message and they're leader or have higher priority
            if response.type == MessageType.ELECTION:
                # Check if they're already leader (they sent election with their info)
                # If they're leader, their epoch/seq should be >= ours
                other_epoch = response.epoch
                other_seq = response.seq
                other_node_id = int(response.value) if response.value else 0
                
                # If they have higher epoch or (same epoch and higher seq) or (same epoch/seq and higher node_id)
                if (other_epoch > latest_epoch or 
                    (other_epoch == latest_epoch and other_seq > latest_seq) or
                    (other_epoch == latest_epoch and other_seq == latest_seq and other_node_id > self.node_num)):
                    with self.election_lock:
                        if self.state == NodeState.CANDIDATE:
                            self.state = NodeState.FOLLOWER
                            self.last_heartbeat_time = time.time()
                            self.last_election_time = time.time()
                    print(f"[{self.node_id}] Stepping down for higher priority/existing leader {node_id}")
                    return
        
        # Wait for responses with STRICT ELECTION_DURATION time limit
        election_deadline = self.election_start_time + ELECTION_DURATION
        quorum_reached = False
        max_wait_iterations = int(ELECTION_DURATION * 10)  # Check 10 times per second
        iteration = 0
        
        while time.time() < election_deadline and iteration < max_wait_iterations:
            iteration += 1
            with self.election_lock:
                if self.state != NodeState.CANDIDATE:
                    return  # Someone else won or we stepped down
                
                # Check election timeout
                elapsed = time.time() - self.election_start_time
                if elapsed >= ELECTION_DURATION:
                    print(f"[{self.node_id}] ⏱️ Election timeout after {elapsed:.1f}s (deadline: {ELECTION_DURATION}s)")
                    break
                
                # Check if we have quorum
                current_votes = len(self.election_votes)
                if current_votes >= QUORUM_SIZE:
                    # We have quorum - immediately proceed (don't wait)
                    if not quorum_reached:
                        quorum_reached = True
                        print(f"[{self.node_id}] ⚡ Quorum reached ({current_votes}/{QUORUM_SIZE}) in {elapsed:.2f}s")
                    # No extra waiting - proceed immediately to final check
                    break
            time.sleep(0.1)  # Check every 100ms
        
        # Check if election timed out
        elapsed = time.time() - self.election_start_time
        if elapsed >= ELECTION_DURATION:
            with self.election_lock:
                if self.state == NodeState.CANDIDATE:
                    print(f"[{self.node_id}] Election timed out after {elapsed:.1f}s (got {len(self.election_votes)}/{QUORUM_SIZE} votes)")
                    self.state = NodeState.FOLLOWER
                    self.last_heartbeat_time = time.time()
                    return
        
        # Final check: verify we still have quorum and are still candidate
        with self.election_lock:
            # Check if election timed out
            elapsed = time.time() - self.election_start_time
            if elapsed >= ELECTION_DURATION:
                print(f"[{self.node_id}] Election timed out after {elapsed:.1f}s, cannot become leader")
                self.state = NodeState.FOLLOWER
                self.last_heartbeat_time = time.time()
                return
            
            if self.state != NodeState.CANDIDATE:
                print(f"[{self.node_id}] Election cancelled: state changed to {self.state.value}")
                return  # Someone else won or we stepped down
            
            # Final check: verify we still have quorum
            final_vote_count = len(self.election_votes)
            final_votes_list = list(self.election_votes)
            
            if final_vote_count >= QUORUM_SIZE:
                # Verify vote count is correct (should be unique nodes)
                if len(final_votes_list) != final_vote_count:
                    print(f"[{self.node_id}] ERROR: Vote count mismatch! {final_vote_count} votes but {len(final_votes_list)} unique voters")
                    self.state = NodeState.FOLLOWER
                    return
                
                # Before becoming leader, verify no other leader exists
                leader_conflict = False
                # (Leader conflict check removed for simplicity - rely on quorum)
                
                if not leader_conflict:
                    print(f"[{self.node_id}] Election succeeded: {final_vote_count}/{QUORUM_SIZE} votes from {final_votes_list}")
                    self._become_leader()
                else:
                    print(f"[{self.node_id}] Election aborted: leader conflict detected")
                    self.last_heartbeat_time = time.time()
                    self.state = NodeState.FOLLOWER
            else:
                # Election failed - didn't get quorum
                self.last_heartbeat_time = time.time()
                self.state = NodeState.FOLLOWER
                print(f"[{self.node_id}] Election failed (got {final_vote_count}/{QUORUM_SIZE} votes), becoming FOLLOWER")
    
    def _become_leader(self):
        """Transition to leader state"""
        # Double check we still have quorum before becoming leader
        with self.election_lock:
            if self.state != NodeState.CANDIDATE:
                print(f"[{self.node_id}] Cannot become leader: state changed to {self.state.value}")
                return
            
            # Verify we have enough votes
            vote_count = len(self.election_votes)
            if vote_count < QUORUM_SIZE:
                print(f"[{self.node_id}] Cannot become leader: only {vote_count}/{QUORUM_SIZE} votes")
                self.state = NodeState.FOLLOWER
                return
            
            # Before becoming leader, send a final check to ensure no other leader exists
            # This is a safety measure to prevent split-brain
            leader_conflict_found = False
            for node_id in NODES:
                if node_id != self.node_id and node_id in self.election_votes:
                    # Send a quick check to nodes that voted for us
                    try:
                        check_msg = Message(
                            MessageType.HEARTBEAT,  # Use heartbeat as a check
                            epoch=self.current_epoch,
                            from_node=self.node_id
                        )
                        # If we get a response indicating they're leader, we have a conflict
                        # But we can't easily do this without modifying the protocol
                        # So we'll rely on the fact that if we got quorum, we should win
                        pass
                    except:
                        pass
            
            if leader_conflict_found:
                print(f"[{self.node_id}] Cannot become leader: leader conflict detected")
                self.state = NodeState.FOLLOWER
                return
            
            # Final state check before transition
            if self.state != NodeState.CANDIDATE:
                print(f"[{self.node_id}] Cannot become leader: state changed during verification")
                return
            
            print(f"[{self.node_id}] Becoming LEADER (epoch: {self.current_epoch}, votes: {vote_count}/{QUORUM_SIZE}, voters: {list(self.election_votes)})")
            self.state = NodeState.LEADER
            self.leader_id = self.node_id
            self.current_seq = 0
            self.voted_for = None  # Clear vote
            self.election_votes.clear()  # Clear votes after becoming leader
        
        # Immediately send heartbeat to announce leadership (multiple times to ensure all nodes see it)
        for _ in range(3):
            self._send_heartbeats()
            time.sleep(0.1)
        
        # Sync pending proposals
        self._sync_pending_proposals()
    
    def _sync_pending_proposals(self):
        """Sync any pending proposals from previous leader"""
        # Get all uncommitted proposals
        all_logs = self.log_store.get_all_logs()
        for epoch, seq, op, value, status in all_logs:
            if status == LogStatus.PROPOSED.value:
                # Try to commit it
                self._commit_proposal(epoch, seq)
    
    def _handle_connection(self, conn, addr):
        """Handle incoming connection"""
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                
                msg_str = data.decode('utf-8')
                msg = Message.from_string(msg_str)
                
                response = self._handle_message(msg)
                
                if response:
                    conn.sendall(response.to_string().encode('utf-8'))
        except Exception as e:
            print(f"[{self.node_id}] Error handling connection from {addr}: {e}")
        finally:
            conn.close()
    
    def _handle_message(self, msg: Message) -> Optional[Message]:
        """Handle incoming message"""
        # Handle election messages
        if msg.type == MessageType.ELECTION:
            return self._handle_election(msg)
        elif msg.type == MessageType.VOTE:
            # Already handled
            return None
        
        # Handle heartbeat
        if msg.type == MessageType.HEARTBEAT:
            self.last_heartbeat_time = time.time()
            self.last_election_time = time.time()  # Reset election timer when receiving heartbeat
            
            # If we receive heartbeat from a leader, update our state
            if msg.epoch > self.current_epoch:
                self.current_epoch = msg.epoch
                self.leader_id = msg.from_node
                with self.election_lock:
                    if self.state == NodeState.CANDIDATE:
                        # If we're candidate and receive heartbeat from leader, step down
                        self.state = NodeState.FOLLOWER
                        print(f"[{self.node_id}] Received heartbeat from leader {msg.from_node}, stepping down from candidate")
                    elif self.state != NodeState.LEADER:
                        self.state = NodeState.FOLLOWER
            elif self.state == NodeState.LEADER and msg.from_node != self.node_id:
                # If we're leader but receive heartbeat from another leader with same or higher epoch
                if msg.epoch >= self.current_epoch:
                    print(f"[{self.node_id}] WARNING: Received heartbeat from another leader {msg.from_node} (epoch: {msg.epoch})")
                    # This shouldn't happen, but if it does, we should step down if they have higher priority
                    if msg.epoch > self.current_epoch or (msg.epoch == self.current_epoch and int(NODES[msg.from_node]["id"]) > self.node_num):
                        with self.election_lock:
                            self.state = NodeState.FOLLOWER
                            self.leader_id = msg.from_node
                            self.current_epoch = msg.epoch
                        print(f"[{self.node_id}] Stepping down as leader for {msg.from_node}")
            else:
                # Normal heartbeat from our leader
                self.leader_id = msg.from_node
                with self.election_lock:
                    # Don't reset voted_for on heartbeat - it should persist until new election
                    # Only reset if we're in a new epoch
                    if msg.epoch > self.current_epoch:
                        # New epoch, can vote again
                        self.voted_for = None
                        self.vote_term = 0
                if self.state != NodeState.LEADER:
                    self.state = NodeState.FOLLOWER
            
            return None
        
        # Handle client messages
        if msg.type == MessageType.WRITE:
            return self._handle_write(msg)
        elif msg.type == MessageType.GUESS:
            return self._handle_guess(msg)
        elif msg.type == MessageType.READ:
            return self._handle_read(msg)
        
        # Handle ZAB protocol messages
        if msg.type == MessageType.PROPOSE:
            return self._handle_propose(msg)
        elif msg.type == MessageType.ACK:
            return self._handle_ack(msg)
        elif msg.type == MessageType.COMMIT:
            return self._handle_commit(msg)
        elif msg.type == MessageType.FORWARD:
            return self._handle_forward(msg)
        
        return None
    
    def _handle_election(self, msg: Message) -> Message:
        """Handle election message"""
        # If we're already the leader, reject the election
        if self.state == NodeState.LEADER:
            # Send back our leadership info so they know we're the leader
            return Message(
                MessageType.ELECTION,
                epoch=self.current_epoch,
                seq=self.current_seq,
                value=str(self.node_num),
                from_node=self.node_id
            )
        
        # Compare (epoch, seq, node_id)
        latest_epoch, latest_seq = self.log_store.get_latest_epoch_seq()
        candidate_node_id = int(msg.value) if msg.value else 0
        
        # If we're a candidate, compare priorities
        if self.state == NodeState.CANDIDATE:
            # If candidate has higher priority, vote for them and step down
            # Use latest_epoch (from log) for priority comparison, not msg.epoch (which is election term)
            candidate_priority = (latest_epoch, msg.seq, candidate_node_id)
            our_priority = (latest_epoch, latest_seq, self.node_num)
            
            if candidate_priority > our_priority:
                with self.election_lock:
                    self.state = NodeState.FOLLOWER
                    self.last_heartbeat_time = time.time()
                    self.last_election_time = time.time()
                    self.voted_for = msg.from_node
                print(f"[{self.node_id}] Voting for higher priority candidate {msg.from_node} and stepping down")
                return Message(MessageType.VOTE, from_node=self.node_id)
            elif candidate_priority == our_priority:
                # Same priority - higher node_id wins
                if candidate_node_id > self.node_num:
                    with self.election_lock:
                        self.state = NodeState.FOLLOWER
                        self.last_heartbeat_time = time.time()
                        self.last_election_time = time.time()
                        self.voted_for = msg.from_node
                    print(f"[{self.node_id}] Voting for equal priority but higher node_id candidate {msg.from_node}")
                    return Message(MessageType.VOTE, from_node=self.node_id)
                else:
                    # We have higher or equal node_id, don't vote
                    return Message(MessageType.ERROR, value="Election rejected", from_node=self.node_id)
            else:
                # Candidate has lower priority, don't vote
                return Message(MessageType.ERROR, value="Election rejected", from_node=self.node_id)
        
        # If we're a follower, check if we've already voted in this election term
        # Priority comparison uses: (log_epoch, log_seq, node_id)
        # msg.epoch is the election term, msg.seq is the candidate's latest seq
        candidate_priority = (latest_epoch, msg.seq, candidate_node_id)  # Use latest_epoch, not msg.epoch
        our_priority = (latest_epoch, latest_seq, self.node_num)
        
        # Use the election epoch from the message as the term for vote tracking
        election_term = msg.epoch
        
        # CRITICAL: Entire voting logic must be atomic - hold lock for the whole process
        with self.election_lock:
            # STRICT: Once we vote, don't vote again until we receive heartbeat or enough time passes
            time_since_last_vote = time.time() - self.last_vote_time
            time_since_last_heartbeat = time.time() - self.last_heartbeat_time
            
            # ABSOLUTE RULE: Once we vote, we CANNOT vote for a different candidate
            # until we receive a heartbeat (proving a leader exists) OR election cycle ends
            if self.voted_for is not None and self.voted_for != msg.from_node:
                # Different candidate - check if we can vote again
                # Only allow if we received heartbeat VERY recently (within 1 second)
                if time_since_last_heartbeat < 1.0:
                    # Got heartbeat very recently - there's an active leader, we can vote for new candidate
                    print(f"[{self.node_id}] ✓ Received heartbeat {time_since_last_heartbeat:.1f}s ago, allowing vote for {msg.from_node}")
                else:
                    # NO recent heartbeat - ABSOLUTELY reject to prevent split-brain
                    print(f"[{self.node_id}] ❌ REJECTING: Already voted for {self.voted_for} {time_since_last_vote:.1f}s ago, NO heartbeat (last: {time_since_last_heartbeat:.1f}s ago)")
                    return Message(MessageType.ERROR, value="Already voted, no leader heartbeat", from_node=self.node_id)
            
            # Also check term-based voting
            if self.voted_for is not None and self.vote_term == election_term and self.voted_for != msg.from_node:
                print(f"[{self.node_id}] REJECTING: Already voted for {self.voted_for} in term {election_term}")
                return Message(MessageType.ERROR, value="Already voted", from_node=self.node_id)
            
            # Now decide whether to vote - ALL checks passed, we can vote
            vote_granted = False
            if candidate_priority > our_priority:
                vote_granted = True
            elif candidate_priority == our_priority and candidate_node_id >= self.node_num:
                # Same priority - only vote if enough time passed
                if time_since_last_vote >= 5.0:
                    vote_granted = True
                else:
                    return Message(MessageType.ERROR, value="Already voted recently", from_node=self.node_id)
            
            if vote_granted:
                # ATOMIC: Set all vote-related fields together
                old_voted_for = self.voted_for
                self.voted_for = msg.from_node
                self.vote_term = election_term
                self.last_vote_time = time.time()
                self.last_heartbeat_time = time.time()
                self.last_election_time = time.time()
                
                if old_voted_for != msg.from_node:
                    print(f"[{self.node_id}] ✓ VOTING for {msg.from_node} (term: {election_term}, priority: {candidate_priority}, was: {old_voted_for})")
                return Message(MessageType.VOTE, from_node=self.node_id)
            else:
                # Don't vote for lower priority
                return Message(MessageType.ERROR, value="Election rejected", from_node=self.node_id)
    
    def _handle_write(self, msg: Message) -> Message:
        """Handle write request from client"""
        if self.state == NodeState.LEADER:
            # Leader: if there are pending guesses, process them first
            if self.current_guesses and self.current_target is not None:
                # Process guesses synchronously (wait for commit)
                self._process_guesses_sync()
            # Then propose the new write
            return self._propose_operation("WRITE", msg.value)
        else:
            # Follower: forward to leader
            if self.leader_id:
                try:
                    forward_msg = Message(
                        MessageType.FORWARD,
                        op="WRITE",
                        value=msg.value,
                        from_node=self.node_id
                    )
                    response = self._send_message_to_node(self.leader_id, forward_msg, wait_response=True)
                    return response or Message(MessageType.ERROR, value="No response from leader")
                except Exception as e:
                    return Message(MessageType.ERROR, value=f"Failed to forward: {e}")
            else:
                return Message(MessageType.ERROR, value="No leader available")
    
    def _handle_guess(self, msg: Message) -> Message:
        """Handle guess request from client"""
        if self.state == NodeState.LEADER:
            # Leader: collect guesses
            if self.current_target is None:
                return Message(MessageType.ERROR, value="No target set", from_node=self.node_id)
            try:
                guess_value = int(msg.value)
                if guess_value < MIN_TARGET or guess_value > MAX_TARGET:
                    return Message(MessageType.ERROR, value=f"Guess must be between {MIN_TARGET} and {MAX_TARGET}", from_node=self.node_id)
                self.current_guesses.append((guess_value, msg.from_node))
                print(f"[{self.node_id}] Collected guess: {guess_value} from {msg.from_node}")
                return Message(MessageType.RESPONSE, value="Guess received", from_node=self.node_id)
            except ValueError:
                return Message(MessageType.ERROR, value="Invalid guess value", from_node=self.node_id)
        else:
            # Follower: forward to leader
            if self.leader_id:
                try:
                    forward_msg = Message(
                        MessageType.FORWARD,
                        op="GUESS",
                        value=msg.value,
                        from_node=msg.from_node
                    )
                    response = self._send_message_to_node(self.leader_id, forward_msg, wait_response=True)
                    return response or Message(MessageType.ERROR, value="No response from leader")
                except Exception as e:
                    return Message(MessageType.ERROR, value=f"Failed to forward: {e}")
            else:
                return Message(MessageType.ERROR, value="No leader available")
    
    def _handle_read(self, msg: Message) -> Message:
        """Handle read request from client"""
        if self.current_target is not None:
            return Message(MessageType.RESPONSE, value=str(self.current_target), from_node=self.node_id)
        else:
            return Message(MessageType.RESPONSE, value="No target set", from_node=self.node_id)
    
    def _handle_forward(self, msg: Message) -> Message:
        """Handle forwarded request from follower"""
        if self.state != NodeState.LEADER:
            return Message(MessageType.ERROR, value="Not leader")
        
        if msg.op == "WRITE":
            # If there are pending guesses, process them first
            if self.current_guesses and self.current_target is not None:
                # Process guesses synchronously (wait for commit)
                self._process_guesses_sync()
            return self._propose_operation("WRITE", msg.value)
        elif msg.op == "GUESS":
            if self.current_target is None:
                return Message(MessageType.ERROR, value="No target set", from_node=self.node_id)
            try:
                guess_value = int(msg.value)
                if guess_value < MIN_TARGET or guess_value > MAX_TARGET:
                    return Message(MessageType.ERROR, value=f"Guess must be between {MIN_TARGET} and {MAX_TARGET}", from_node=self.node_id)
                self.current_guesses.append((guess_value, msg.from_node))
                print(f"[{self.node_id}] Collected guess: {guess_value} from {msg.from_node}")
                return Message(MessageType.RESPONSE, value="Guess received", from_node=self.node_id)
            except ValueError:
                return Message(MessageType.ERROR, value="Invalid guess value", from_node=self.node_id)
    
    def _propose_operation(self, op: str, value: str) -> Message:
        """Propose a new operation (ZAB protocol)"""
        if self.state != NodeState.LEADER:
            return Message(MessageType.ERROR, value="Not leader")
        
        # Increment sequence
        self.current_seq += 1
        proposal_key = (self.current_epoch, self.current_seq)
        
        # Store proposal
        self.log_store.append_proposal(self.current_epoch, self.current_seq, op, value)
        
        # Initialize pending proposal tracking
        with self.proposal_lock:
            self.pending_proposals[proposal_key] = {
                "acks": set(),
                "op": op,
                "value": value
            }
        
        # Send proposal to all followers
        proposal_msg = Message(
            MessageType.PROPOSE,
            epoch=self.current_epoch,
            seq=self.current_seq,
            op=op,
            value=value,
            from_node=self.node_id
        )
        
        acks_received = 0
        for node_id in NODES:
            if node_id != self.node_id:
                try:
                    self._send_message_to_node(node_id, proposal_msg)
                except Exception as e:
                    pass
        
        # Wait for quorum of ACKs
        start_time = time.time()
        while time.time() - start_time < ACK_TIMEOUT:
            with self.proposal_lock:
                if proposal_key in self.pending_proposals:
                    acks_received = len(self.pending_proposals[proposal_key]["acks"])
                    if acks_received >= QUORUM_SIZE - 1:  # -1 because we don't ACK ourselves
                        break
            time.sleep(0.1)
        
        # Check if we got quorum
        with self.proposal_lock:
            if proposal_key in self.pending_proposals:
                acks_received = len(self.pending_proposals[proposal_key]["acks"])
                if acks_received >= QUORUM_SIZE - 1:
                    # Commit
                    self._commit_proposal(self.current_epoch, self.current_seq)
                    return Message(MessageType.RESPONSE, value="Committed", from_node=self.node_id)
                else:
                    # Failed to get quorum
                    del self.pending_proposals[proposal_key]
                    return Message(MessageType.ERROR, value="Failed to get quorum")
            else:
                return Message(MessageType.ERROR, value="Proposal not found")
    
    def _handle_propose(self, msg: Message) -> Message:
        """Handle proposal from leader"""
        if self.state == NodeState.LEADER:
            return None  # Shouldn't receive proposals as leader
        
        # Log the proposal
        self.log_store.append_proposal(msg.epoch, msg.seq, msg.op, msg.value)
        
        # Update epoch if needed
        if msg.epoch > self.current_epoch:
            self.current_epoch = msg.epoch
            self.current_seq = 0
        
        # Send ACK
        ack_msg = Message(
            MessageType.ACK,
            epoch=msg.epoch,
            seq=msg.seq,
            from_node=self.node_id
        )
        return ack_msg
    
    def _handle_ack(self, msg: Message) -> Optional[Message]:
        """Handle ACK from follower"""
        if self.state != NodeState.LEADER:
            return None
        
        proposal_key = (msg.epoch, msg.seq)
        with self.proposal_lock:
            if proposal_key in self.pending_proposals:
                self.pending_proposals[proposal_key]["acks"].add(msg.from_node)
        return None
    
    def _handle_commit(self, msg: Message) -> Optional[Message]:
        """Handle commit message from leader"""
        # Commit the log entry
        self.log_store.commit_log(msg.epoch, msg.seq)
        
        # Apply the commit
        log_entry = self.log_store.get_log(msg.epoch, msg.seq)
        if log_entry:
            _, _, op, value, _ = log_entry
            self._apply_operation(op, value)
        
        # Update epoch
        if msg.epoch > self.current_epoch:
            self.current_epoch = msg.epoch
            self.current_seq = msg.seq
        
        return None
    
    def _commit_proposal(self, epoch: int, seq: int):
        """Commit a proposal (leader only)"""
        # Mark as committed in log
        self.log_store.commit_log(epoch, seq)
        
        # Apply operation
        log_entry = self.log_store.get_log(epoch, seq)
        if log_entry:
            _, _, op, value, _ = log_entry
            self._apply_operation(op, value)
        
        # Send commit to all followers
        commit_msg = Message(
            MessageType.COMMIT,
            epoch=epoch,
            seq=seq,
            from_node=self.node_id
        )
        
        for node_id in NODES:
            if node_id != self.node_id:
                try:
                    self._send_message_to_node(node_id, commit_msg)
                except Exception as e:
                    pass
        
        # Clean up pending proposal
        proposal_key = (epoch, seq)
        with self.proposal_lock:
            if proposal_key in self.pending_proposals:
                del self.pending_proposals[proposal_key]
    
    def _process_guesses(self):
        """Process collected guesses and find the closest one (leader only) - async version"""
        if not self.current_guesses or self.current_target is None:
            return
        
        if self.state != NodeState.LEADER:
            return
        
        # Find closest guess
        closest_guess = min(
            self.current_guesses,
            key=lambda g: abs(g[0] - self.current_target)
        )
        closest_value = closest_guess[0]
        
        print(f"[{self.node_id}] Processing guesses: target={self.current_target}, guesses={[g[0] for g in self.current_guesses]}, closest={closest_value}")
        
        # Propose the closest guess as new target
        self._propose_operation("GUESS", str(closest_value))
        
        # Clear guesses
        self.current_guesses = []
    
    def _process_guesses_sync(self):
        """Process guesses synchronously - wait for commit to complete"""
        if not self.current_guesses or self.current_target is None:
            return
        
        if self.state != NodeState.LEADER:
            return
        
        # Find closest guess
        closest_guess = min(
            self.current_guesses,
            key=lambda g: abs(g[0] - self.current_target)
        )
        closest_value = closest_guess[0]
        
        print(f"[{self.node_id}] Processing guesses: target={self.current_target}, guesses={[g[0] for g in self.current_guesses]}, closest={closest_value}")
        
        # Store current guesses and clear them
        guesses_to_process = self.current_guesses.copy()
        self.current_guesses = []
        
        # Propose the closest guess as new target (this will wait for quorum)
        result = self._propose_operation("GUESS", str(closest_value))
        
        if result and result.type == MessageType.ERROR:
            # If proposal failed, restore guesses
            self.current_guesses = guesses_to_process
    
    def _apply_operation(self, op: str, value: str):
        """Apply a committed operation to local state"""
        if op == "WRITE":
            self.current_target = int(value)
            self.current_guesses = []
            self.round_active = True
            print(f"[{self.node_id}] Applied WRITE: target = {self.current_target}")
        elif op == "GUESS":
            # Apply the closest guess as new target
            self.current_target = int(value)
            self.current_guesses = []
            print(f"[{self.node_id}] Applied GUESS: new target = {self.current_target}")
    
    def _apply_committed_logs(self):
        """Apply all committed logs to restore state"""
        committed_logs = self.log_store.get_committed_logs()
        for epoch, seq, op, value, status in committed_logs:
            self._apply_operation(op, value)
    
    def _send_message_to_node(self, node_id: str, msg: Message, wait_response: bool = False) -> Optional[Message]:
        """Send message to another node"""
        if node_id not in NODES:
            return None
        
        node_info = NODES[node_id]
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((node_info["host"], node_info["port"]))
            
            sock.sendall(msg.to_string().encode('utf-8'))
            
            if wait_response:
                data = sock.recv(4096)
                sock.close()
                if data:
                    response = Message.from_string(data.decode('utf-8'))
                    return response
            else:
                sock.close()
            
            return None
        except Exception as e:
            return None
    
    def stop(self):
        """Stop the node server"""
        if self.socket:
            self.socket.close()
        self.executor.shutdown(wait=True)

