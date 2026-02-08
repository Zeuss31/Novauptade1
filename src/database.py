"""
VERİTABANI YÖNETİCİSİ
Sohbetleri veritabanında saklıyoruz
"""

import sqlite3
import json
from datetime import datetime
from config.settings import Settings

class Database:
    """Veritabanı işlemlerini yönetir"""
    
    def __init__(self):
        """Veritabanını başlatır"""
        self.db_path = Settings.DATABASE_PATH
        self._create_tables()
    
    def _get_connection(self):
        """Veritabanı bağlantısı oluşturur"""
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Tabloları oluşturur"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Sohbetler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Mesajlar tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_conversation(self, title="Yeni Sohbet"):
        """Yeni sohbet oluşturur"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return conversation_id
    
    def get_conversations(self):
        """Tüm sohbetleri getirir"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, created_at, updated_at 
            FROM conversations 
            ORDER BY updated_at DESC
        """)
        conversations = cursor.fetchall()
        conn.close()
        return [
            {
                "id": c[0],
                "title": c[1],
                "created_at": c[2],
                "updated_at": c[3]
            }
            for c in conversations
        ]
    
    def get_messages(self, conversation_id):
        """Bir sohbetin mesajlarını getirir"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content, created_at 
            FROM messages 
            WHERE conversation_id = ? 
            ORDER BY created_at ASC
        """, (conversation_id,))
        messages = cursor.fetchall()
        conn.close()
        return [
            {
                "role": m[0],
                "content": m[1],
                "created_at": m[2]
            }
            for m in messages
        ]
    
    def save_message(self, conversation_id, role, content):
        """Mesaj kaydeder"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content) 
            VALUES (?, ?, ?)
        """, (conversation_id, role, content))
        
        # Sohbeti güncelle
        cursor.execute("""
            UPDATE conversations 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (conversation_id,))
        
        conn.commit()
        conn.close()
    
    def delete_conversation(self, conversation_id):
        """Sohbeti siler"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        conn.commit()
        conn.close()
    
    def update_conversation_title(self, conversation_id, title):
        """Sohbet başlığını günceller"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE conversations 
            SET title = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (title, conversation_id))
        conn.commit()
        conn.close()