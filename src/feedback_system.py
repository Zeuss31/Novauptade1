"""
FEEDBACK SİSTEMİ - GELİŞMİŞ VERSİYON
Kullanıcıdan otomatik ve manuel feedback toplar, analiz eder ve öneriler üretir.
"""

from typing import Dict, List, Optional
from datetime import datetime
import re
from collections import Counter
import math

# Basit sentiment analiz modülü (geliştirilebilir)
class SentimentAnalyzer:
    positive_words = ["teşekkür", "sağol", "eyvallah", "harika", "süper", "mükemmel", "iyi", "anladım", "tamam", "oldu", "çalıştı", "tam istediğim"]
    negative_words = ["anlamadım", "karmaşık", "yanlış", "hatalı", "çalışmadı", "tekrar et", "kötü", "berbat", "yetersiz"]

    @classmethod
    def analyze(cls, text: str) -> Dict:
        text_lower = text.lower()
        score = 0
        for word in cls.positive_words:
            if word in text_lower:
                score += 1
        for word in cls.negative_words:
            if word in text_lower:
                score -= 1
        sentiment = "neutral"
        if score > 0:
            sentiment = "positive"
        elif score < 0:
            sentiment = "negative"
        return {"sentiment": sentiment, "score": score}

class FeedbackSystem:
    """Kullanıcı feedback'lerini toplar ve analiz eder"""
    
    def __init__(self, learning_engine):
        self.learning_engine = learning_engine
        
    def analyze_implicit_feedback(self, user_message: str, 
                                  conversation_history: List[Dict]) -> Dict:
        """Kullanıcının mesajından implicit feedback çıkar"""
        feedback = {
            "sentiment": "neutral",
            "issues": [],
            "positive_signals": [],
            "rating": 3
        }

        # Basit regex tabanlı issue tespiti
        message_lower = user_message.lower()
        negative_patterns = [
            (r"anlamadım|anlamıyorum", "comprehension_issue"),
            (r"daha basit|kompleks|karmaşık", "complexity_issue"),
            (r"yanlış|hatalı|doğru değil", "accuracy_issue"),
            (r"işe yaramadı|çalışmadı", "functionality_issue"),
            (r"tekrar et|yeniden anlat", "clarity_issue"),
            (r"kötü|berbat|yetersiz", "quality_issue"),
        ]
        for pattern, issue_type in negative_patterns:
            if re.search(pattern, message_lower):
                feedback["issues"].append(issue_type)

        # Sentiment analizini ekle
        sentiment_result = SentimentAnalyzer.analyze(user_message)
        feedback["sentiment"] = sentiment_result["sentiment"]
        if sentiment_result["sentiment"] == "negative":
            feedback["rating"] = 2
        elif sentiment_result["sentiment"] == "positive":
            feedback["rating"] = 5

        # Pozitif sinyaller
        positive_patterns = [
            r"teşekkür|sağol|eyvallah",
            r"harika|süper|mükemmel|çok iyi",
            r"anladım|tamam|oldu",
            r"işe yaradı|çalıştı",
            r"tam istediğim",
        ]
        for pattern in positive_patterns:
            if re.search(pattern, message_lower):
                feedback["positive_signals"].append(pattern)

        # Follow-up sorusu = pozitif sinyal (ilgileniyor)
        if any(q in message_lower for q in ["nasıl", "neden", "ne zaman", "nerede"]):
            feedback["positive_signals"].append("follow_up_question")
        
        return feedback
    
    def collect_explicit_feedback(self, conversation_id: int, message_id: int,
                                 rating: int, comment: str = ""):
        """Kullanıcının direkt verdiği feedback'i kaydet"""
        self.learning_engine.record_feedback(
            conversation_id, message_id, "explicit", rating, comment
        )
    
    def analyze_conversation_quality(self, messages: List[Dict]) -> Dict:
        """Sohbet kalitesini analiz et"""
        quality_metrics = {
            "avg_response_length": 0,
            "question_answer_ratio": 0,
            "context_switches": 0,
            "repetition_score": 0,
            "engagement_score": 0,
            "sentiment_trend": "neutral"
        }
        
        ai_messages = [m for m in messages if m["role"] == "assistant"]
        user_messages = [m for m in messages if m["role"] == "user"]
        
        if not ai_messages or not user_messages:
            return quality_metrics
        
        # Ortalama cevap uzunluğu
        total_length = sum(len(m["content"]) for m in ai_messages)
        quality_metrics["avg_response_length"] = total_length / len(ai_messages)
        
        # Soru/cevap oranı
        questions = sum(1 for m in user_messages if "?" in m["content"])
        quality_metrics["question_answer_ratio"] = questions / len(user_messages)
        
        # Tekrar skoru (aynı kelimelerin tekrarı)
        all_ai_text = " ".join(m["content"] for m in ai_messages)
        words = all_ai_text.lower().split()
        unique_words = set(words)
        quality_metrics["repetition_score"] = len(unique_words) / len(words) if words else 0
        
        # Engagement (kullanıcı devam ediyor mu?)
        quality_metrics["engagement_score"] = len(user_messages) / 10  # Normalize

        # Sentiment trend
        sentiment_scores = [SentimentAnalyzer.analyze(m["content"])["score"] for m in ai_messages]
        if sentiment_scores:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            if avg_sentiment > 0:
                quality_metrics["sentiment_trend"] = "positive"
            elif avg_sentiment < 0:
                quality_metrics["sentiment_trend"] = "negative"
            else:
                quality_metrics["sentiment_trend"] = "neutral"
        
        return quality_metrics
    
    def detect_problematic_patterns(self, messages: List[Dict]) -> List[str]:
        """Sorunlu pattern'leri tespit et"""
        problems = []
        ai_messages = [m["content"] for m in messages if m["role"] == "assistant"]
        if not ai_messages:
            return problems
        
        # Tekrarlayan cümleler
        for i in range(len(ai_messages) - 1):
            if ai_messages[i] == ai_messages[i + 1]:
                problems.append("identical_responses")
                break
        
        # Çok kısa veya çok uzun cevaplar
        short_responses = sum(1 for m in ai_messages if len(m) < 50)
        long_responses = sum(1 for m in ai_messages if len(m) > 2000)
        if short_responses / len(ai_messages) > 0.5:
            problems.append("too_short_responses")
        if long_responses / len(ai_messages) > 0.3:
            problems.append("too_long_responses")
        
        # Aynı kalıplar
        common_starts = ["Tabii ki", "Elbette", "Merhaba", "İşte"]
        start_counts = {s: 0 for s in common_starts}
        for msg in ai_messages:
            for start in common_starts:
                if msg.startswith(start):
                    start_counts[start] += 1
        max_repeat = max(start_counts.values())
        if max_repeat / len(ai_messages) > 0.4:
            problems.append("repetitive_openings")
        
        # Çok tekrar eden kelimeler
        word_counts = Counter(" ".join(ai_messages).lower().split())
        repeated_words = [w for w, c in word_counts.items() if c > len(ai_messages) // 2]
        if repeated_words:
            problems.append("overused_words")
        
        return problems
    
    def should_trigger_improvement(self, feedback_history: List[Dict]) -> bool:
        """Iyileştirme tetikleyici koşulları kontrol et"""
        if len(feedback_history) < 10:
            return False
        
        recent = feedback_history[-10:]
        avg_rating = sum(f["rating"] for f in recent) / len(recent)
        negative_count = sum(1 for f in recent if f["sentiment"] == "negative")
        
        return avg_rating < 3.0 or negative_count / len(recent) > 0.5
    
    def generate_feedback_report(self) -> Dict:
        """Feedback raporunu oluştur"""
        stats = self.learning_engine.get_learning_stats()
        
        return {
            "total_feedback": stats.get("total_feedback", 0),
            "avg_rating": stats.get("avg_rating", 0),
            "trends": "improving" if stats.get("avg_rating", 0) >= 4 else "needs_attention",
            "recommendations": self._generate_recommendations(stats)
        }
    
    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """İstatistiklere göre öneriler oluştur"""
        recommendations = []
        avg_rating = stats.get("avg_rating", 0)
        
        if avg_rating < 3.0:
            recommendations.append("personality_adjustment")
            recommendations.append("response_quality_improvement")
        if avg_rating < 4.0:
            recommendations.append("context_awareness_improvement")
            recommendations.append("engagement_boost")
        if avg_rating >= 4.5:
            recommendations.append("maintain_quality")
        
        return recommendations
