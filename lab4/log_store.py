"""Log Store for persistent logging of proposals and commits"""

import sqlite3
import json
import os
from typing import List, Tuple, Optional
from enum import Enum


class LogStatus(Enum):
    PROPOSED = "PROPOSED"
    COMMITTED = "COMMITTED"


class LogStore:
    """Persistent log store using SQLite"""
    
    def __init__(self, node_id: str, db_path: str = None):
        self.node_id = node_id
        self.db_path = db_path or f"logs_{node_id}.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                epoch INTEGER,
                seq INTEGER,
                op TEXT,
                value TEXT,
                status TEXT,
                PRIMARY KEY (epoch, seq)
            )
        ''')
        conn.commit()
        conn.close()
    
    def append_proposal(self, epoch: int, seq: int, op: str, value: str):
        """Append a proposed log entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO logs (epoch, seq, op, value, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (epoch, seq, op, value, LogStatus.PROPOSED.value))
        conn.commit()
        conn.close()
    
    def commit_log(self, epoch: int, seq: int):
        """Mark a log entry as committed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE logs
            SET status = ?
            WHERE epoch = ? AND seq = ?
        ''', (LogStatus.COMMITTED.value, epoch, seq))
        conn.commit()
        conn.close()
    
    def get_log(self, epoch: int, seq: int) -> Optional[Tuple]:
        """Get a specific log entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT epoch, seq, op, value, status
            FROM logs
            WHERE epoch = ? AND seq = ?
        ''', (epoch, seq))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_all_logs(self) -> List[Tuple]:
        """Get all log entries ordered by epoch, seq"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT epoch, seq, op, value, status
            FROM logs
            ORDER BY epoch, seq
        ''')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_committed_logs(self) -> List[Tuple]:
        """Get all committed log entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT epoch, seq, op, value, status
            FROM logs
            WHERE status = ?
            ORDER BY epoch, seq
        ''', (LogStatus.COMMITTED.value,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_latest_epoch_seq(self) -> Tuple[int, int]:
        """Get the latest (epoch, seq) from committed logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT epoch, seq
            FROM logs
            WHERE status = ?
            ORDER BY epoch DESC, seq DESC
            LIMIT 1
        ''', (LogStatus.COMMITTED.value,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return (result[0], result[1])
        return (0, 0)
    
    def clear_db(self):
        """Clear all logs (for testing)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM logs')
        conn.commit()
        conn.close()

