"""
DİNAMİK PERSONALİTY SİSTEMİ
Feedback'lere göre personality'yi otomatik optimize eder
"""

from typing import Dict, List
import json
from pathlib import Path

class DynamicPersonality:
    """Öğrenmeye dayalı dinamik personality yönetimi"""
    
    def __init__(self, learning_engine):
        self.learning_engine = learning_engine
        self.personality_overrides = self._load_overrides()
        
    def _load_overrides(self) -> Dict:
        """Öğrenilmiş personality override'ları yükle"""
        override_file = Path("data/personality_overrides.json")
        
        if override_file.exists():
            with open(override_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "tone_adjustments": {},
            "response_patterns": {},
            "emphasis_areas": [],
            "avoid_patterns": []
        }
    
    def _save_overrides(self):
        """Override'ları kaydet"""
        Path("data").mkdir(exist_ok=True)
        with open("data/personality_overrides.json", 'w', encoding='utf-8') as f:
            json.dump(self.personality_overrides, f, indent=2, ensure_ascii=False)
    
    def get_enhanced_system_prompt(self, base_prompt: str) -> str:
        """
        Base personality prompt'a öğrenilmiş iyileştirmeleri ekle
        """
        enhancements = []
        
        # Tone ayarlamaları
        if self.personality_overrides.get("tone_adjustments"):
            tone_section = "\n🎯 ÖĞRENME TABANLI TON AYARLAMALARI:\n"
            for area, adjustment in self.personality_overrides["tone_adjustments"].items():
                tone_section += f"- {area}: {adjustment}\n"
            enhancements.append(tone_section)
        
        # Emphasis alanları
        if self.personality_overrides.get("emphasis_areas"):
            emphasis_section = "\n⚡ ÖNCELİKLENDİRİLMİŞ ALANLAR (Kullanıcı feedback'ine göre):\n"
            for emphasis in self.personality_overrides["emphasis_areas"]:
                emphasis_section += f"- {emphasis}\n"
            enhancements.append(emphasis_section)
        
        # Kaçınılacak pattern'ler
        if self.personality_overrides.get("avoid_patterns"):
            avoid_section = "\n🚫 KAÇINILACAK PATTERN'LER (Negatif feedback alındı):\n"
            for pattern in self.personality_overrides["avoid_patterns"]:
                avoid_section += f"- {pattern}\n"
            enhancements.append(avoid_section)
        
        # Response pattern'leri
        if self.personality_overrides.get("response_patterns"):
            pattern_section = "\n✅ BAŞARILI PATTERN'LER:\n"
            for context, pattern in self.personality_overrides["response_patterns"].items():
                pattern_section += f"- {context}: {pattern}\n"
            enhancements.append(pattern_section)
        
        # Enhanced prompt oluştur
        if enhancements:
            enhanced = base_prompt + "\n\n" + "="*50 + "\n"
            enhanced += "🤖 OTOMATİK ÖĞRENME İYİLEŞTİRMELERİ\n"
            enhanced += "="*50 + "\n"
            enhanced += "".join(enhancements)
            return enhanced
        
        return base_prompt
    
    def learn_from_feedback(self, feedback_data: List[Dict]):
        """Feedback'lerden öğren ve personality'yi güncelle"""
        
        # Negatif feedback pattern'lerini analiz et
        negative_patterns = self._analyze_negative_patterns(feedback_data)
        
        # Pozitif feedback pattern'lerini analiz et
        positive_patterns = self._analyze_positive_patterns(feedback_data)
        
        # Override'ları güncelle
        self._update_overrides(negative_patterns, positive_patterns)
        
        # Kaydet
        self._save_overrides()
    
    def _analyze_negative_patterns(self, feedback_data: List[Dict]) -> Dict:
        """Negatif feedback'lerdeki pattern'leri bul"""
        issues = {}
        
        for feedback in feedback_data:
            if feedback.get("sentiment") == "negative":
                for issue in feedback.get("issues", []):
                    issues[issue] = issues.get(issue, 0) + 1
        
        return issues
    
    def _analyze_positive_patterns(self, feedback_data: List[Dict]) -> Dict:
        """Pozitif feedback'lerdeki pattern'leri bul"""
        signals = {}
        
        for feedback in feedback_data:
            if feedback.get("sentiment") == "positive":
                for signal in feedback.get("positive_signals", []):
                    signals[signal] = signals.get(signal, 0) + 1
        
        return signals
    
    def _update_overrides(self, negative_patterns: Dict, positive_patterns: Dict):
        """Override'ları güncelle"""
        
        # Sık görülen negatif pattern'ler için ayarlamalar
        if negative_patterns.get("complexity_issue", 0) > 5:
            self.personality_overrides["tone_adjustments"]["simplicity"] = \
                "Her zaman basit dille başla, gerekirse sonra detaylandır"
            self.personality_overrides["emphasis_areas"].append(
                "Açıklamaları step-by-step yap"
            )
        
        if negative_patterns.get("clarity_issue", 0) > 5:
            self.personality_overrides["emphasis_areas"].append(
                "Örneklerle açıkla, analogiler kullan"
            )
        
        if negative_patterns.get("too_long", 0) > 3:
            self.personality_overrides["avoid_patterns"].append(
                "Çok uzun paragraflar yazma, kısa ve öz tut"
            )
        
        # Başarılı pattern'leri kaydet
        if positive_patterns.get("follow_up_question", 0) > 10:
            self.personality_overrides["response_patterns"]["engagement"] = \
                "Kullanıcı follow-up sorular soruyor - devam et bu tarzda"
    
    def get_adaptive_instructions(self, conversation_context: Dict) -> str:
        """
        Conversation context'e göre adaptif talimatlar
        """
        instructions = []
        
        # Eğer kullanıcı teknik sorular soruyorsa
        if conversation_context.get("technical_level") == "high":
            instructions.append("Teknik detaylara gir, basitleştirmeye gerek yok")
        
        # Eğer kullanıcı başlangıç seviyesindeyse
        if conversation_context.get("technical_level") == "beginner":
            instructions.append("Çok basit anlat, jargon kullanma")
        
        # Eğer kullanıcı negatif feedback vermişse
        if conversation_context.get("recent_negative_feedback"):
            instructions.append("Daha dikkatli ol, önceki hatayı tekrarlama")
        
        return "\n".join(instructions) if instructions else ""
    
    def suggest_personality_improvement(self) -> List[str]:
        """Personality için iyileştirme önerileri"""
        suggestions = []
        
        # Override'lara göre öneriler
        if len(self.personality_overrides.get("avoid_patterns", [])) > 5:
            suggestions.append(
                "Çok fazla kaçınılacak pattern var. Base personality'yi yeniden gözden geçir."
            )
        
        if not self.personality_overrides.get("response_patterns"):
            suggestions.append(
                "Henüz başarılı pattern öğrenilmemiş. Daha fazla pozitif feedback gerekli."
            )
        
        return suggestions