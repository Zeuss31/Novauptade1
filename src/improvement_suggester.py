"""
İYİLEŞTİRME ÖNERİCİSİ
AI'ın kendi kodunu analiz edip iyileştirme önerileri üretir
⚠️ UYARI: Bu kod çok dikkatli kullanılmalıdır
"""

import ast
import re
from typing import Dict, List, Optional
from pathlib import Path

class ImprovementSuggester:
    """Kod iyileştirme önerileri üretir"""
    
    # Kritik dosyalar - ASLA değiştirilmemeli
    PROTECTED_FILES = [
        "config/settings.py",
        "__init__.py",
        "requirements.txt"
    ]
    
    # Değiştirilebilir dosyalar
    ALLOWED_FILES = [
        "src/personality.py",
        "src/conversation.py",
        "src/utils.py"
    ]
    
    def __init__(self, learning_engine):
        self.learning_engine = learning_engine
        
    def analyze_code_quality(self, file_path: str) -> Dict:
        """Kod kalitesini analiz et"""
        if not Path(file_path).exists():
            return {"error": "File not found"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        issues = []
        
        # Temel kod kalitesi kontrolleri
        try:
            tree = ast.parse(code)
            
            # Fonksiyon uzunluğu kontrolü
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:
                        issues.append({
                            "type": "long_function",
                            "name": node.name,
                            "lines": func_length
                        })
            
            # Docstring kontrolü
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append({
                            "type": "missing_docstring",
                            "name": node.name
                        })
        
        except SyntaxError as e:
            issues.append({"type": "syntax_error", "message": str(e)})
        
        return {
            "file": file_path,
            "issues": issues,
            "score": self._calculate_quality_score(issues)
        }
    
    def _calculate_quality_score(self, issues: List[Dict]) -> float:
        """Kalite skoru hesapla (0-100)"""
        score = 100.0
        
        for issue in issues:
            if issue["type"] == "syntax_error":
                score -= 50
            elif issue["type"] == "long_function":
                score -= 5
            elif issue["type"] == "missing_docstring":
                score -= 2
        
        return max(0, score)
    
    def suggest_personality_improvements(self, feedback_data: List[Dict]) -> List[Dict]:
        """
        Feedback'lere göre personality iyileştirmeleri öner
        Bu en güvenli iyileştirme türüdür
        """
        suggestions = []
        
        # Negatif feedback'leri analiz et
        negative_issues = {}
        for fb in feedback_data:
            for issue in fb.get("issues", []):
                negative_issues[issue] = negative_issues.get(issue, 0) + 1
        
        # En sık görülen sorunlar için öneriler
        if negative_issues.get("complexity_issue", 0) > 5:
            suggestions.append({
                "type": "personality_adjustment",
                "target": "system_prompt",
                "suggestion": "Add emphasis on simplicity: 'Explain concepts in simple terms first, then add complexity if needed.'",
                "reason": f"Users reported complexity issues {negative_issues['complexity_issue']} times",
                "priority": "high"
            })
        
        if negative_issues.get("clarity_issue", 0) > 5:
            suggestions.append({
                "type": "personality_adjustment",
                "target": "system_prompt",
                "suggestion": "Add clarity guidelines: 'Use examples and analogies. Structure responses with clear headings.'",
                "reason": f"Users reported clarity issues {negative_issues['clarity_issue']} times",
                "priority": "high"
            })
        
        if negative_issues.get("repetition", 0) > 3:
            suggestions.append({
                "type": "personality_adjustment",
                "target": "response_generation",
                "suggestion": "Add variation instruction: 'Never start consecutive responses with the same phrase.'",
                "reason": "Detected repetitive response patterns",
                "priority": "medium"
            })
        
        return suggestions
    
    def suggest_conversation_improvements(self, conversation_metrics: Dict) -> List[Dict]:
        """Conversation management iyileştirmeleri öner"""
        suggestions = []
        
        # Context management
        if conversation_metrics.get("context_switches", 0) > 10:
            suggestions.append({
                "type": "context_improvement",
                "target": "src/conversation.py",
                "suggestion": "Implement smarter context management with importance scoring",
                "reason": "High number of context switches detected",
                "priority": "medium"
            })
        
        # Repetition issues
        if conversation_metrics.get("repetition_score", 1.0) < 0.5:
            suggestions.append({
                "type": "diversity_improvement",
                "target": "src/personality.py",
                "suggestion": "Add response diversity checker to avoid repetitive phrases",
                "reason": f"Low diversity score: {conversation_metrics['repetition_score']:.2f}",
                "priority": "high"
            })
        
        return suggestions
    
    def generate_code_improvement(self, issue_type: str, target_file: str) -> Optional[str]:
        """
        Belirli bir sorun için kod iyileştirmesi üret
        ⚠️ Bu method gerçek kod değişikliği önerir - dikkatli olun
        """
        if target_file in self.PROTECTED_FILES:
            return None
        
        if target_file not in self.ALLOWED_FILES:
            return None
        
        # Güvenli iyileştirme örnekleri
        improvements = {
            "add_diversity_check": """
# Response diversity checker
def check_response_diversity(self, new_response: str, history: List[str]) -> bool:
    '''Check if response is too similar to recent responses'''
    if not history:
        return True
    
    recent = history[-3:]  # Check last 3 responses
    for old_response in recent:
        # Simple similarity check
        new_words = set(new_response.lower().split())
        old_words = set(old_response.lower().split())
        
        if len(new_words & old_words) / len(new_words) > 0.7:
            return False  # Too similar
    
    return True
""",
            "add_response_quality_check": """
def check_response_quality(self, response: str) -> Dict[str, Any]:
    '''Check basic response quality metrics'''
    return {
        'length': len(response),
        'has_examples': '例' in response or 'örnek' in response.lower(),
        'has_structure': any(h in response for h in ['##', '**', '1.', '2.']),
        'is_too_short': len(response) < 50,
        'is_too_long': len(response) > 3000
    }
"""
        }
        
        return improvements.get(issue_type)
    
    def validate_improvement(self, suggestion: str) -> bool:
        """
        İyileştirme önerisini validate et
        Tehlikeli kod içerip içermediğini kontrol et
        """
        # Tehlikeli keyword'ler
        dangerous_keywords = [
            "os.system", "exec(", "eval(",
            "__import__", "compile(",
            "open(", "write(",  # Dosya yazma
            "subprocess", "shell=True",
            "rm -rf", "del ", "remove(",
            "DROP TABLE", "DELETE FROM"
        ]
        
        for keyword in dangerous_keywords:
            if keyword in suggestion:
                return False
        
        # Syntax kontrolü
        try:
            ast.parse(suggestion)
            return True
        except SyntaxError:
            return False
    
    def prioritize_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Önerileri önceliğe göre sırala"""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        
        return sorted(
            suggestions,
            key=lambda s: priority_order.get(s.get("priority", "low"), 2)
        )