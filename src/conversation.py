"""
SOHBET YÖNETİCİSİ
Sohbet geçmişini burada saklıyoruz ve yönetiyoruz
"""

from config.settings import Settings
from src.personality import Personality

class ConversationManager:
    """Sohbet geçmişini yönetir"""
    
    def __init__(self):
        """Yeni sohbet başlatır"""
        self.messages = []
        self.message_count = 0
        self._add_system_message()
    
    def _add_system_message(self):
        """Sistem mesajını ekler (yapay zekanın kişiliği)"""
        self.messages.append({
            "role": "system",
            "content": Personality.get_system_prompt()
        })
    
    def add_user_message(self, message):
        """Kullanıcı mesajını ekler"""
        self.messages.append({
            "role": "user",
            "content": message
        })
        self.message_count += 1
        self._manage_context()
    
    def add_assistant_message(self, message):
        """Yapay zeka cevabını ekler"""
        # Kimlik karışıklığı kontrolü
        message = self._fix_identity_confusion(message)
        
        self.messages.append({
            "role": "assistant",
            "content": message
        })
        self._manage_context()
    
    def _fix_identity_confusion(self, message):
        """
        Kimlik karışıklığını düzeltir
        Örnek: "Ben sen Nova" -> "Ben Nova"
        """
        # Yaygın kimlik hatalarını düzelt
        fixes = [
            ("ben sen Nova", "ben Nova"),
            ("Ben sen Nova", "Ben Nova"),
            ("ben sen nova", "ben Nova"),
            ("Ben senin Nova", "Ben Nova"),
            ("sen ben", "ben"),
        ]
        
        for wrong, correct in fixes:
            message = message.replace(wrong, correct)
        
        return message
    
    def _manage_context(self):
        """
        Akıllı bağlam yönetimi
        - System prompt'u her zaman tutar
        - Önemli mesajları önceliklendirir
        - Context window'u optimize eder
        """
        if len(self.messages) > Settings.MAX_HISTORY + 1:
            # System prompt + en son N mesaj
            system_msg = self.messages[0]
            recent_messages = self.messages[-(Settings.MAX_HISTORY):]
            self.messages = [system_msg] + recent_messages
    
    def get_messages(self):
        """Tüm mesajları döndürür"""
        return self.messages
    
    def clear(self):
        """Sohbet geçmişini temizler"""
        self.messages = []
        self.message_count = 0
        self._add_system_message()
    
    def get_message_count(self):
        """Kaç mesaj var (system hariç)"""
        return len(self.messages) - 1
    
    def get_conversation_summary(self):
        """Sohbetin kısa özetini döndürür"""
        if self.message_count == 0:
            return "Yeni Sohbet"
        
        # İlk kullanıcı mesajını al
        for msg in self.messages[1:]:  # System'i atla
            if msg['role'] == 'user':
                # İlk 50 karakteri al
                summary = msg['content'][:50]
                if len(msg['content']) > 50:
                    summary += "..."
                return summary
        
        return "Yeni Sohbet"