"""
ÖĞRENME MOTORU
AI'ın deneyimlerden öğrenmesini sağlar
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import hashlib

class LearningEngine:
    """AI'ın öğrenme sistemini yönetir"""
    
    def __init__(self, db_path="data/learning.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Öğrenme veritabanını oluştur"""
        Path("data").mkdir(exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Feedback tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                message_id INTEGER,
                feedback_type TEXT,
                rating INTEGER,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Pattern tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data TEXT,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_rating REAL DEFAULT 0.0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Improvement önerileri
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                improvement_type TEXT,
                target_file TEXT,
                suggestion TEXT,
                reasoning TEXT,
                status TEXT DEFAULT 'pending',
                tested BOOLEAN DEFAULT 0,
                approved BOOLEAN DEFAULT 0,
                applied BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_at TIMESTAMP
            )
        """)
        
        # Performans metrikleri
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Kod değişiklik geçmişi (rollback için)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                old_content TEXT,
                new_content TEXT,
                change_hash TEXT UNIQUE,
                reason TEXT,
                rollback_available BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_feedback(self, conversation_id: int, message_id: int, 
                        feedback_type: str, rating: int, comment: str = ""):
        """Kullanıcı feedback'i kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (conversation_id, message_id, feedback_type, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (conversation_id, message_id, feedback_type, rating, comment))
        conn.commit()
        conn.close()
        
        # Feedback'e göre öğren
        self._learn_from_feedback(conversation_id, message_id, rating)
    
    def _learn_from_feedback(self, conversation_id: int, message_id: int, rating: int):
        """Feedback'den pattern çıkar"""
        # Bu method conversation'ı analiz edip pattern'leri kaydeder
        pass
    
    def record_pattern(self, pattern_type: str, pattern_data: Dict[str, Any], 
                       success: bool = True):
        """Başarılı/başarısız pattern kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        pattern_json = json.dumps(pattern_data)
        cursor.execute("""
            SELECT id, success_count, failure_count 
            FROM patterns 
            WHERE pattern_type = ? AND pattern_data = ?
        """, (pattern_type, pattern_json))
        existing = cursor.fetchone()
        
        if existing:
            pattern_id, success_count, failure_count = existing
            if success:
                success_count += 1
            else:
                failure_count += 1
            cursor.execute("""
                UPDATE patterns 
                SET success_count = ?, failure_count = ?, last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (success_count, failure_count, pattern_id))
        else:
            cursor.execute("""
                INSERT INTO patterns (pattern_type, pattern_data, success_count, failure_count, last_used)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (pattern_type, pattern_json, 1 if success else 0, 0 if success else 1))
        
        conn.commit()
        conn.close()
    
    def get_best_patterns(self, pattern_type: str, limit: int = 10):
        """En başarılı pattern'leri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pattern_data, success_count, failure_count 
            FROM patterns 
            WHERE pattern_type = ? AND success_count > failure_count
            ORDER BY (success_count * 1.0 / (success_count + failure_count)) DESC
            LIMIT ?
        """, (pattern_type, limit))
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "pattern": json.loads(r[0]),
                "success_count": r[1],
                "failure_count": r[2]
            }
            for r in results
        ]
    
    def suggest_improvement(self, improvement_type: str, target_file: str,
                            suggestion: str, reasoning: str):
        """Yeni iyileştirme önerisi kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO improvements (improvement_type, target_file, suggestion, reasoning)
            VALUES (?, ?, ?, ?)
        """, (improvement_type, target_file, suggestion, reasoning))
        conn.commit()
        conn.close()
    
    def get_pending_improvements(self):
        """Onay bekleyen iyileştirmeleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, improvement_type, target_file, suggestion, reasoning, created_at
            FROM improvements
            WHERE status = 'pending' AND approved = 0
            ORDER BY created_at DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "type": r[1],
                "file": r[2],
                "suggestion": r[3],
                "reasoning": r[4],
                "created_at": r[5]
            }
            for r in results
        ]
    
    def record_metric(self, metric_name: str, value: float, context: str = ""):
        """Performans metriği kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO metrics (metric_name, metric_value, context)
            VALUES (?, ?, ?)
        """, (metric_name, value, context))
        conn.commit()
        conn.close()
    
    def get_metric_trend(self, metric_name: str, limit: int = 100):
        """Metrik trendini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT metric_value, created_at
            FROM metrics
            WHERE metric_name = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (metric_name, limit))
        results = cursor.fetchall()
        conn.close()
        return [{"value": r[0], "timestamp": r[1]} for r in results]
    
    def backup_code(self, file_path: str, old_content: str, 
                    new_content: str, reason: str):
        """Kod değişikliği öncesi backup al"""
        change_hash = hashlib.md5(
            f"{file_path}{old_content}{new_content}".encode()
        ).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO code_history (file_path, old_content, new_content, change_hash, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (file_path, old_content, new_content, change_hash, reason))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def rollback_last_change(self, file_path: str):
        """Son değişikliği geri al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT old_content FROM code_history
            WHERE file_path = ? AND rollback_available = 1
            ORDER BY created_at DESC
            LIMIT 1
        """, (file_path,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return None
    
    def get_learning_stats(self):
        """Öğrenme istatistiklerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM feedback")
        stats['total_feedback'] = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(rating) FROM feedback")
        stats['avg_rating'] = cursor.fetchone()[0] or 0.0
        cursor.execute("SELECT COUNT(*) FROM patterns")
        stats['total_patterns'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM improvements WHERE status = 'pending'")
        stats['pending_improvements'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM improvements WHERE applied = 1")
        stats['applied_improvements'] = cursor.fetchone()[0]
        conn.close()
        return stats
