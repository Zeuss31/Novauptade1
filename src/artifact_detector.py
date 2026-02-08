"""
ARTIFACT DETECTOR
AI'ın yanıtında artifact olup olmadığını tespit eder
"""

import re
from typing import Dict, Optional, List

class ArtifactDetector:
    """AI yanıtlarından artifact çıkar"""
    
    # Artifact türleri ve belirteçleri
    MARKERS = {
        'python': ['```python', '```py'],
        'javascript': ['```javascript', '```js'],
        'html': ['```html', '<!DOCTYPE', '<html'],
        'react': ['```jsx', '```react', 'import React'],
        'css': ['```css'],
        'sql': ['```sql'],
        'bash': ['```bash', '```sh'],
        'json': ['```json'],
        'yaml': ['```yaml', '```yml'],
        'markdown': ['```markdown', '```md'],
        'svg': ['```svg', '<svg']
    }
    
    @staticmethod
    def detect(text: str) -> List[Dict]:
        """
        Metinden tüm artifact'ları çıkar
        
        Returns:
            [{
                'type': 'code/html/react',
                'language': 'python/javascript/etc',
                'content': 'kod içeriği',
                'title': 'başlık (opsiyonel)'
            }]
        """
        artifacts = []
        
        # 1. Code block'ları bul (```...```)
        code_blocks = ArtifactDetector._extract_code_blocks(text)
        
        for block in code_blocks:
            language = block['language']
            content = block['content']
            
            # Artifact türünü belirle
            artifact_type = ArtifactDetector._determine_type(language, content)
            
            # Minimum uzunluk kontrolü (çok kısa kodları artifact yapma)
            if len(content.strip()) < 50 and artifact_type == 'code':
                continue
            
            artifacts.append({
                'type': artifact_type,
                'language': language,
                'content': content,
                'title': ArtifactDetector._extract_title(content, language)
            })
        
        # 2. HTML/SVG gibi açık etiketleri bul (``` olmadan)
        inline_artifacts = ArtifactDetector._extract_inline_artifacts(text)
        artifacts.extend(inline_artifacts)
        
        return artifacts
    
    @staticmethod
    def _extract_code_blocks(text: str) -> List[Dict]:
        """```...``` formatındaki kod bloklarını çıkar"""
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        blocks = []
        for match in matches:
            language = match.group(1) or 'text'
            content = match.group(2).strip()
            
            blocks.append({
                'language': language.lower(),
                'content': content
            })
        
        return blocks
    
    @staticmethod
    def _extract_inline_artifacts(text: str) -> List[Dict]:
        """``` olmadan direkt HTML/SVG gibi artifact'ları bul"""
        artifacts = []
        
        # HTML
        html_pattern = r'(<html[\s\S]*?</html>|<!DOCTYPE html>[\s\S]*?</html>)'
        html_matches = re.finditer(html_pattern, text, re.IGNORECASE)
        
        for match in html_matches:
            content = match.group(1).strip()
            if len(content) > 100:  # Minimum uzunluk
                artifacts.append({
                    'type': 'html',
                    'language': 'html',
                    'content': content,
                    'title': 'HTML Document'
                })
        
        # SVG
        svg_pattern = r'(<svg[\s\S]*?</svg>)'
        svg_matches = re.finditer(svg_pattern, text, re.IGNORECASE)
        
        for match in svg_matches:
            content = match.group(1).strip()
            if len(content) > 50:
                artifacts.append({
                    'type': 'svg',
                    'language': 'svg',
                    'content': content,
                    'title': 'SVG Image'
                })
        
        return artifacts
    
    @staticmethod
    def _determine_type(language: str, content: str) -> str:
        """İçeriğe göre artifact türünü belirle"""
        # HTML içeriği var mı?
        if 'html' in language or '<html' in content.lower() or '<!doctype' in content.lower():
            # React component mı?
            if 'import react' in content.lower() or 'jsx' in language:
                return 'react'
            return 'html'
        
        # SVG
        if 'svg' in language or '<svg' in content.lower():
            return 'svg'
        
        # Markdown
        if language in ['markdown', 'md'] or content.startswith('#'):
            return 'markdown'
        
        # Diğer herşey kod
        return 'code'
    
    @staticmethod
    def _extract_title(content: str, language: str) -> str:
        """İçerikten başlık çıkar"""
        # Python: fonksiyon/class adı
        if language == 'python':
            func_match = re.search(r'def\s+(\w+)', content)
            if func_match:
                return f"Function: {func_match.group(1)}"
            
            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                return f"Class: {class_match.group(1)}"
        
        # HTML: title tag
        if language == 'html':
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                return title_match.group(1)
        
        # İlk satırdaki yorum
        comment_match = re.search(r'^(?:#|//|/\*)\s*(.+?)(?:\*/)?$', content.split('\n')[0])
        if comment_match:
            return comment_match.group(1).strip()
        
        return f"{language.title()} Code"
    
    @staticmethod
    def should_create_artifact(text: str) -> bool:
        """Bu yanıt için artifact oluşturulmalı mı?"""
        artifacts = ArtifactDetector.detect(text)
        
        # En az bir geçerli artifact varsa
        return len(artifacts) > 0
    
    @staticmethod
    def remove_code_blocks(text: str) -> str:
        """Metinden kod bloklarını çıkar (sadece açıklama kalır)"""
        # ``` kod bloklarını kaldır
        text = re.sub(r'```\w*\n.*?```', '', text, flags=re.DOTALL)
        
        # Inline HTML/SVG'yi kaldır
        text = re.sub(r'<html[\s\S]*?</html>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<!DOCTYPE html>[\s\S]*?</html>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<svg[\s\S]*?</svg>', '', text, flags=re.IGNORECASE)
        
        return text.strip()