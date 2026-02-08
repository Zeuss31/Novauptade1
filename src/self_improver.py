"""
SELF-IMPROVEMENT SYSTEM
AI'ın kendini geliştirme ana sistemi
⚠️ KRİTİK UYARI: Bu sistem çok dikkatli kullanılmalıdır
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json 

from src.learning_engine import LearningEngine
from src.feedback_system import FeedbackSystem
from src.improvement_suggester import ImprovementSuggester
from src.sandbox_tester import SandboxTester 
from typing import Dict, List, Optional, Tuple

class SelfImprover:
    """
    AI'ın kendini geliştirme ana kontrol sistemi
    """
    
    # KILL SWITCH - Acil durdurma
    KILL_SWITCH_FILE = "data/KILL_SWITCH.txt"
    
    # Maksimum değişiklik limitleri
    MAX_DAILY_CHANGES = 3
    MAX_FILE_CHANGES_PER_RUN = 1
    MIN_TEST_SUCCESS_RATE = 0.95  # %95 başarı oranı
    
    def __init__(self, auto_apply: bool = False):
        """
        Args:
            auto_apply: Otomatik uygulama (ÇOK TEHLİKELİ - varsayılan False)
        """
        self.auto_apply = auto_apply
        self.learning_engine = LearningEngine()
        self.feedback_system = FeedbackSystem(self.learning_engine)
        self.suggester = ImprovementSuggester(self.learning_engine)
        self.sandbox = SandboxTester()
        
        self.changes_today = self._count_todays_changes()
        
    def _count_todays_changes(self) -> int:
        """Bugün yapılan değişiklikleri say"""
        # Learning engine'den bugünün değişikliklerini al
        return 0  # TODO: Implement
    
    def is_kill_switch_active(self) -> bool:
        """Kill switch aktif mi kontrol et"""
        return Path(self.KILL_SWITCH_FILE).exists()
    
    def activate_kill_switch(self, reason: str = "Manual activation"):
        """Kill switch'i aktif et - tüm self-improvement'ı durdur"""
        Path("data").mkdir(exist_ok=True)
        with open(self.KILL_SWITCH_FILE, 'w') as f:
            f.write(f"ACTIVATED: {datetime.now()}\nREASON: {reason}\n")
        
        print("🛑 KILL SWITCH ACTIVATED - Self-improvement STOPPED")
    
    def deactivate_kill_switch(self):
        """Kill switch'i deaktif et"""
        if Path(self.KILL_SWITCH_FILE).exists():
            os.remove(self.KILL_SWITCH_FILE)
    
    def check_safety_limits(self) -> Tuple[bool, str]:
        """Güvenlik limitlerini kontrol et"""
        # Kill switch
        if self.is_kill_switch_active():
            return False, "Kill switch is active"
        
        # Günlük limit
        if self.changes_today >= self.MAX_DAILY_CHANGES:
            return False, f"Daily change limit reached ({self.MAX_DAILY_CHANGES})"
        
        # Sistem sağlık kontrolü
        stats = self.learning_engine.get_learning_stats()
        avg_rating = stats.get('avg_rating', 0)
        
        if avg_rating < 2.0:
            return False, "System health too low (avg rating < 2.0)"
        
        return True, "Safety checks passed"
    
    def analyze_and_suggest(self) -> List[Dict]:
        """
        Sistemi analiz et ve iyileştirme önerileri üret
        """
        suggestions = []
        
        # 1. Feedback analizi
        stats = self.learning_engine.get_learning_stats()
        
        # 2. Personality iyileştirmeleri
        # TODO: Gerçek feedback verilerini al
        feedback_data = []  # self.learning_engine.get_recent_feedback(limit=50)
        personality_suggestions = self.suggester.suggest_personality_improvements(feedback_data)
        suggestions.extend(personality_suggestions)
        
        # 3. Conversation management iyileştirmeleri
        # TODO: Gerçek metrikleri al
        conv_metrics = {}
        conv_suggestions = self.suggester.suggest_conversation_improvements(conv_metrics)
        suggestions.extend(conv_suggestions)
        
        # 4. Önerileri önceliklendir
        suggestions = self.suggester.prioritize_suggestions(suggestions)
        
        # 5. Learning engine'e kaydet
        for suggestion in suggestions:
            self.learning_engine.suggest_improvement(
                improvement_type=suggestion['type'],
                target_file=suggestion.get('target', 'unknown'),
                suggestion=suggestion['suggestion'],
                reasoning=suggestion['reason']
            )
        
        return suggestions
    
    def test_improvement(self, improvement_id: int) -> Tuple[bool, str]:
        """
        Bir iyileştirme önerisini sandbox'ta test et
        """
        # TODO: Learning engine'den improvement'ı al
        # Şimdilik basit versiyon
        
        # 1. Güvenlik kontrolü
        safe, reason = self.check_safety_limits()
        if not safe:
            return False, f"Safety check failed: {reason}"
        
        # 2. Improvement bilgilerini al
        # improvement = self.learning_engine.get_improvement(improvement_id)
        
        # 3. Kod değişikliğini oluştur
        # new_code = self._apply_suggestion_to_code(improvement)
        
        # 4. Güvenlik kontrolü
        # is_safe, warnings = self.sandbox.security_check(new_code)
        # if not is_safe:
        #     return False, f"Security check failed: {warnings}"
        
        # 5. Sandbox test
        # success, message = self.sandbox.test_code_change(
        #     improvement['target_file'], 
        #     new_code
        # )
        
        # 6. Sonucu kaydet
        # self._record_test_result(improvement_id, success, message)
        
        return True, "Test placeholder - implement full version"
    
    def apply_improvement(self, improvement_id: int, force: bool = False) -> Tuple[bool, str]:
        """
        Test edilmiş bir iyileştirmeyi gerçek sisteme uygula
        ⚠️ UYARI: Bu method gerçek kod değiştirir
        """
        if not force:
            # Güvenlik kontrolleri
            safe, reason = self.check_safety_limits()
            if not safe:
                return False, f"Cannot apply: {reason}"
        
        try:
            # TODO: Implement
            # 1. Improvement bilgilerini al
            # 2. Mevcut kodu yedekle
            # 3. Yeni kodu uygula
            # 4. Verification
            # 5. Başarısızsa rollback
            
            return False, "Not implemented yet - safety feature"
        
        except Exception as e:
            return False, f"Error applying improvement: {str(e)}"
    
    def rollback_last_change(self, file_path: str) -> Tuple[bool, str]:
        """Son değişikliği geri al"""
        old_content = self.learning_engine.rollback_last_change(file_path)
        
        if old_content is None:
            return False, "No rollback available"
        
        try:
            # Dosyayı geri yükle
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(old_content)
            
            return True, f"Rolled back {file_path}"
        
        except Exception as e:
            return False, f"Rollback failed: {str(e)}"
    
    def run_improvement_cycle(self):
        """
        Tam bir iyileştirme döngüsü çalıştır
        1. Analiz
        2. Öneri
        3. Test
        4. (Opsiyonel) Uygula
        """
        print("🔄 Starting improvement cycle...")
        
        # Güvenlik kontrolü
        safe, reason = self.check_safety_limits()
        if not safe:
            print(f"❌ Safety check failed: {reason}")
            return
        
        # 1. Analiz ve öneri
        print("📊 Analyzing system...")
        suggestions = self.analyze_and_suggest()
        
        if not suggestions:
            print("✅ No improvements needed")
            return
        
        print(f"💡 Found {len(suggestions)} improvement suggestions")
        
        # 2. Her öneri için
        for i, suggestion in enumerate(suggestions[:self.MAX_FILE_CHANGES_PER_RUN]):
            print(f"\n--- Suggestion {i+1}/{len(suggestions)} ---")
            print(f"Type: {suggestion['type']}")
            print(f"Target: {suggestion.get('target', 'N/A')}")
            print(f"Reason: {suggestion['reason']}")
            
            if not self.auto_apply:
                print("⏸️  Auto-apply is disabled. Suggestion saved for manual review.")
                continue
            
            # 3. Test (eğer auto_apply aktifse)
            print("🧪 Testing in sandbox...")
            # test_success, test_msg = self.test_improvement(suggestion_id)
            
            # 4. Uygula (eğer başarılıysa ve auto_apply aktifse)
            # if test_success and self.auto_apply:
            #     print("✅ Test passed, applying...")
            #     apply_success, apply_msg = self.apply_improvement(suggestion_id)
        
        print("\n🏁 Improvement cycle completed")
    
    def get_dashboard_stats(self) -> Dict:
        """Dashboard için istatistikler"""
        stats = self.learning_engine.get_learning_stats()
        
        return {
            "kill_switch_active": self.is_kill_switch_active(),
            "auto_apply_enabled": self.auto_apply,
            "changes_today": self.changes_today,
            "max_daily_changes": self.MAX_DAILY_CHANGES,
            "total_feedback": stats.get("total_feedback", 0),
            "avg_rating": stats.get("avg_rating", 0),
            "pending_improvements": stats.get("pending_improvements", 0),
            "applied_improvements": stats.get("applied_improvements", 0),
            "system_health": self._calculate_system_health(stats)
        }
    
    def _calculate_system_health(self, stats: Dict) -> str:
        """Sistem sağlığını hesapla"""
        avg_rating = stats.get("avg_rating", 0)
        
        if avg_rating >= 4.5:
            return "excellent"
        elif avg_rating >= 4.0:
            return "good"
        elif avg_rating >= 3.0:
            return "fair"
        else:
            return "poor"