"""
ARTIFACT MANAGER
Kod, HTML, React component'leri yönetir ve saklar
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class ArtifactManager:
    """Artifact oluşturma, saklama ve versiyon yönetimi"""
    
    def __init__(self, storage_path: str = "data/artifacts"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def create_artifact(
        self, 
        artifact_type: str,
        content: str,
        title: str = "Untitled",
        language: str = None,
        conversation_id: int = None
    ) -> Dict:
        """
        Yeni artifact oluştur
        
        Types:
        - code: Python, JavaScript, etc.
        - html: HTML/CSS/JS
        - react: React component
        - svg: SVG image
        - mermaid: Diagram
        - markdown: Document
        """
        artifact_id = self._generate_id()
        
        artifact = {
            "id": artifact_id,
            "type": artifact_type,
            "title": title,
            "content": content,
            "language": language,
            "conversation_id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1,
            "versions": [
                {
                    "version": 1,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        # Dosyaya kaydet
        self._save_artifact(artifact)
        
        return artifact
    
    def update_artifact(self, artifact_id: str, new_content: str) -> Dict:
        """Artifact'ı güncelle ve versiyonla"""
        artifact = self.get_artifact(artifact_id)
        
        if not artifact:
            raise ValueError(f"Artifact {artifact_id} bulunamadı")
        
        # Yeni versiyon ekle
        artifact["version"] += 1
        artifact["content"] = new_content
        artifact["updated_at"] = datetime.now().isoformat()
        
        artifact["versions"].append({
            "version": artifact["version"],
            "content": new_content,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_artifact(artifact)
        return artifact
    
    def get_artifact(self, artifact_id: str) -> Optional[Dict]:
        """Artifact'ı getir"""
        filepath = os.path.join(self.storage_path, f"{artifact_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_version(self, artifact_id: str, version: int) -> Optional[str]:
        """Belirli bir versiyonu getir"""
        artifact = self.get_artifact(artifact_id)
        
        if not artifact:
            return None
        
        for v in artifact["versions"]:
            if v["version"] == version:
                return v["content"]
        
        return None
    
    def list_artifacts(self, conversation_id: int = None) -> List[Dict]:
        """Tüm artifact'ları listele"""
        artifacts = []
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    artifact = json.load(f)
                    
                    if conversation_id is None or artifact.get("conversation_id") == conversation_id:
                        # Content çok uzunsa kısalt
                        artifact_summary = artifact.copy()
                        if len(artifact_summary.get("content", "")) > 200:
                            artifact_summary["content"] = artifact_summary["content"][:200] + "..."
                        artifacts.append(artifact_summary)
        
        # Tarihe göre sırala (en yeni en üstte)
        artifacts.sort(key=lambda x: x["created_at"], reverse=True)
        return artifacts
    
    def delete_artifact(self, artifact_id: str) -> bool:
        """Artifact'ı sil"""
        filepath = os.path.join(self.storage_path, f"{artifact_id}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        
        return False
    
    def _generate_id(self) -> str:
        """Unique ID üret"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _save_artifact(self, artifact: Dict):
        """Artifact'ı dosyaya kaydet"""
        filepath = os.path.join(self.storage_path, f"{artifact['id']}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
    
    def export_artifact(self, artifact_id: str, output_path: str = None) -> str:
        """Artifact'ı dosya olarak export et"""
        artifact = self.get_artifact(artifact_id)
        
        if not artifact:
            raise ValueError(f"Artifact {artifact_id} bulunamadı")
        
        # Dosya uzantısını belirle
        ext_map = {
            "code": self._get_code_extension(artifact.get("language", "txt")),
            "html": "html",
            "react": "jsx",
            "svg": "svg",
            "markdown": "md",
            "mermaid": "mmd"
        }
        
        ext = ext_map.get(artifact["type"], "txt")
        
        if output_path is None:
            # uploads klasörüne kaydet
            filename = f"{artifact['title'].replace(' ', '_')}_{artifact_id}.{ext}"
            output_path = os.path.join("uploads", filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(artifact["content"])
        
        return output_path
    
    def _get_code_extension(self, language: str) -> str:
        """Dil için dosya uzantısı"""
        ext_map = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "go": "go",
            "rust": "rs",
            "php": "php",
            "ruby": "rb",
            "swift": "swift",
            "kotlin": "kt",
            "sql": "sql",
            "bash": "sh",
            "json": "json",
            "yaml": "yml",
            "css": "css"
        }
        return ext_map.get(language.lower(), "txt")