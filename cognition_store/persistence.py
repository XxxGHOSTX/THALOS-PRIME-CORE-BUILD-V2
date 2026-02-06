"""
Memory Persistence with Custom SQLite Backend
Novel temporal indexing and pattern tracking
"""

import sqlite3 as db
import json
import hashlib as hl
from datetime import datetime as dt
import threading as thr


class CognitionVault:
    """Persistent storage with temporal awareness"""
    
    def __init__(self, db_file="cognition.db"):
        self.db_file = db_file
        self.db_lock = thr.Lock()
        self._setup_schema()
        
    def _setup_schema(self):
        """Initialize database tables"""
        with self.db_lock:
            conn = db.connect(self.db_file)
            cur = conn.cursor()
            
            # Exchange history
            cur.execute('''
                CREATE TABLE IF NOT EXISTS exchanges (
                    ex_id TEXT PRIMARY KEY,
                    ts TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    cert_val REAL,
                    ctx_sig TEXT,
                    sess_id TEXT
                )
            ''')
            
            # System snapshots
            cur.execute('''
                CREATE TABLE IF NOT EXISTS snapshots (
                    snap_key TEXT PRIMARY KEY,
                    snap_data TEXT NOT NULL,
                    snap_ts TEXT NOT NULL
                )
            ''')
            
            # Pattern registry
            cur.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    pat_id TEXT PRIMARY KEY,
                    pat_class TEXT NOT NULL,
                    occur_cnt INTEGER DEFAULT 1,
                    last_ts TEXT NOT NULL,
                    pat_meta TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
    def archive_exchange(self, q_txt, r_obj, sess="main"):
        """Store conversation exchange"""
        
        ts = dt.now().isoformat()
        ex_id = hl.sha256(f"{ts}{q_txt}".encode()).hexdigest()
        ctx_sig = hl.md5(q_txt.encode()).hexdigest()
        cert = r_obj.get('certainty', 0.5)
        
        with self.db_lock:
            conn = db.connect(self.db_file)
            cur = conn.cursor()
            
            cur.execute('''
                INSERT INTO exchanges 
                (ex_id, ts, query, response, cert_val, ctx_sig, sess_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ex_id, ts, q_txt, json.dumps(r_obj), cert, ctx_sig, sess))
            
            conn.commit()
            conn.close()
            
        return ex_id
    
    def recall_recent(self, count=10, sess=None):
        """Retrieve recent exchanges"""
        
        with self.db_lock:
            conn = db.connect(self.db_file)
            cur = conn.cursor()
            
            if sess:
                cur.execute('''
                    SELECT ex_id, ts, query, response, cert_val
                    FROM exchanges
                    WHERE sess_id = ?
                    ORDER BY ts DESC
                    LIMIT ?
                ''', (sess, count))
            else:
                cur.execute('''
                    SELECT ex_id, ts, query, response, cert_val
                    FROM exchanges
                    ORDER BY ts DESC
                    LIMIT ?
                ''', (count,))
            
            rows = cur.fetchall()
            conn.close()
            
        exchanges = []
        for r in rows:
            exchanges.append({
                'id': r[0],
                'time': r[1],
                'query': r[2],
                'response': json.loads(r[3]),
                'certainty': r[4]
            })
            
        return exchanges
    
    def search_context(self, search_term, count=5):
        """Search exchanges by context"""
        
        with self.db_lock:
            conn = db.connect(self.db_file)
            cur = conn.cursor()
            
            cur.execute('''
                SELECT ex_id, ts, query, response, cert_val
                FROM exchanges
                WHERE query LIKE ?
                ORDER BY ts DESC
                LIMIT ?
            ''', (f'%{search_term}%', count))
            
            rows = cur.fetchall()
            conn.close()
            
        results = []
        for r in rows:
            results.append({
                'id': r[0],
                'time': r[1],
                'query': r[2],
                'response': json.loads(r[3]),
                'certainty': r[4]
            })
            
        return results
    
    def save_snapshot(self, snap_key, snap_val):
        """Save system snapshot"""
        
        ts = dt.now().isoformat()
        snap_str = json.dumps(snap_val)
        
        with self.db_lock:
            conn = db.connect(self.db_file)
            cur = conn.cursor()
            
            cur.execute('''
                INSERT OR REPLACE INTO snapshots (snap_key, snap_data, snap_ts)
                VALUES (?, ?, ?)
            ''', (snap_key, snap_str, ts))
            
            conn.commit()
            conn.close()
    
    def load_snapshot(self, snap_key):
        """Load system snapshot"""
        
        with self.db_lock:
            conn = db.connect(self.db_file)
            cur = conn.cursor()
            
            cur.execute('''
                SELECT snap_data FROM snapshots WHERE snap_key = ?
            ''', (snap_key,))
            
            r = cur.fetchone()
            conn.close()
            
        if r:
            return json.loads(r[0])
        return None
    
    def log_pattern(self, pat_class, pat_meta=None):
        """Log interaction pattern"""
        
        pat_id = hl.sha256(f"{pat_class}".encode()).hexdigest()
        ts = dt.now().isoformat()
        
        with self.db_lock:
            conn = db.connect(self.db_file)
            cur = conn.cursor()
            
            cur.execute('''
                SELECT occur_cnt FROM patterns WHERE pat_id = ?
            ''', (pat_id,))
            
            exist = cur.fetchone()
            
            if exist:
                new_cnt = exist[0] + 1
                cur.execute('''
                    UPDATE patterns 
                    SET occur_cnt = ?, last_ts = ?, pat_meta = ?
                    WHERE pat_id = ?
                ''', (new_cnt, ts, json.dumps(pat_meta or {}), pat_id))
            else:
                cur.execute('''
                    INSERT INTO patterns 
                    (pat_id, pat_class, occur_cnt, last_ts, pat_meta)
                    VALUES (?, ?, 1, ?, ?)
                ''', (pat_id, pat_class, ts, json.dumps(pat_meta or {})))
            
            conn.commit()
            conn.close()
    
    def vault_metrics(self):
        """Get vault statistics"""
        
        with self.db_lock:
            conn = db.connect(self.db_file)
            cur = conn.cursor()
            
            cur.execute('SELECT COUNT(*) FROM exchanges')
            ex_cnt = cur.fetchone()[0]
            
            cur.execute('SELECT COUNT(*) FROM snapshots')
            snap_cnt = cur.fetchone()[0]
            
            cur.execute('SELECT COUNT(*) FROM patterns')
            pat_cnt = cur.fetchone()[0]
            
            cur.execute('SELECT AVG(cert_val) FROM exchanges')
            avg_cert = cur.fetchone()[0] or 0.0
            
            conn.close()
            
        return {
            'exchanges': ex_cnt,
            'snapshots': snap_cnt,
            'patterns': pat_cnt,
            'avg_certainty': avg_cert,
            'location': self.db_file
        }
