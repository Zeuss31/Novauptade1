"""
SANDBOX TEST ORTAMI
Kod değişikliklerini güvenli ortamda test eder
⚠️ KRİTİK: Tüm değişiklikler burada test edilmeden uygulanmamalı
"""
from typing import Tuple, List
import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple
import traceback

class SandboxTester:
    """Kod değişikliklerini izole ortamda test eder"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.sandbox_dir = None
        
    def create_sandbox(self) -> Path:
        """İzole test ortamı oluştur"""
        self.sandbox_dir = Path(tempfile.mkdtemp(prefix="nova_sandbox_"))
        
        # Projeyi sandbox'a kopyala
        essential_files = [
            "src/",
            "config/",
            "templates/",
            "static/",
            "requirements.txt"
        ]
        
        for item in essential_files:
            src = self.project_root / item
            dst = self.sandbox_dir / item
            
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
        
        return self.sandbox_dir
    
    def cleanup_sandbox(self):
        """Sandbox'ı temizle"""
        if self.sandbox_dir and self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir)
            self.sandbox_dir = None
    
    def test_code_change(self, file_path: str, new_content: str) -> Tuple[bool, str]:
        """
        Kod değişikliğini test et
        Returns: (success, message)
        """
        try:
            # Sandbox oluştur
            sandbox = self.create_sandbox()
            
            # Değişikliği uygula
            target_file = sandbox / file_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Syntax kontrolü
            syntax_valid, syntax_msg = self._check_syntax(target_file)
            if not syntax_valid:
                return False, f"Syntax error: {syntax_msg}"
            
            # Import kontrolü
            import_valid, import_msg = self._check_imports(target_file)
            if not import_valid:
                return False, f"Import error: {import_msg}"
            
            # Basit runtime test
            runtime_valid, runtime_msg = self._run_basic_test(sandbox)
            if not runtime_valid:
                return False, f"Runtime error: {runtime_msg}"
            
            return True, "All tests passed"
            
        except Exception as e:
            return False, f"Test error: {str(e)}"
        
        finally:
            self.cleanup_sandbox()
    
    def _check_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Python syntax kontrolü"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            compile(code, str(file_path), 'exec')
            return True, "Syntax OK"
        
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
    
    def _check_imports(self, file_path: Path) -> Tuple[bool, str]:
        """Import'ların çalışıp çalışmadığını kontrol et"""
        try:
            # Sandbox'ı Python path'e ekle
            sandbox_root = file_path.parent
            while sandbox_root.name != "nova_sandbox_" and sandbox_root.parent != sandbox_root:
                sandbox_root = sandbox_root.parent
            
            sys.path.insert(0, str(sandbox_root))
            
            # Modülü import etmeyi dene
            module_name = str(file_path.relative_to(sandbox_root)).replace('/', '.').replace('.py', '')
            __import__(module_name)
            
            return True, "Imports OK"
        
        except ImportError as e:
            return False, str(e)
        
        finally:
            if str(sandbox_root) in sys.path:
                sys.path.remove(str(sandbox_root))
    
    def _run_basic_test(self, sandbox_dir: Path) -> Tuple[bool, str]:
        """Temel çalışma testi"""
        try:
            # Basit bir test scripti çalıştır
            test_script = sandbox_dir / "test_runner.py"
            
            with open(test_script, 'w') as f:
                f.write("""
import sys
sys.path.insert(0, '.')

try:
    # Temel import'ları test et
    from src.personality import Personality
    from src.conversation import ConversationManager
    from src.api_handler import MultiProviderAPIHandler
    
    # Basit instance oluştur
    conv = ConversationManager()
    print("Basic tests passed")
    sys.exit(0)
    
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
""")
            
            # Test scriptini çalıştır (timeout ile)
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=sandbox_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "Runtime tests passed"
            else:
                return False, result.stderr
        
        except subprocess.TimeoutExpired:
            return False, "Test timeout"
        except Exception as e:
            return False, str(e)
    
    def run_integration_test(self, sandbox_dir: Path) -> Tuple[bool, str]:
        """Entegrasyon testi - tüm sistem birlikte çalışıyor mu?"""
        try:
            test_script = sandbox_dir / "integration_test.py"
            
            with open(test_script, 'w') as f:
                f.write("""
import sys
sys.path.insert(0, '.')

try:
    from src.personality import Personality
    from src.conversation import ConversationManager
    
    # Conversation test
    conv = ConversationManager()
    conv.add_user_message("Test message")
    
    # Personality test
    system_prompt = Personality.get_system_prompt()
    assert len(system_prompt) > 0
    
    print("Integration tests passed")
    sys.exit(0)
    
except Exception as e:
    print(f"Integration test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
""")
            
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=sandbox_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return result.returncode == 0, result.stdout + result.stderr
        
        except Exception as e:
            return False, str(e)
    
    def compare_outputs(self, old_code: str, new_code: str, test_inputs: list) -> Dict:
        """
        Eski ve yeni kodun çıktılarını karşılaştır
        Değişikliğin davranışı bozup bozmadığını kontrol et
        """
        results = {
            "old_outputs": [],
            "new_outputs": [],
            "differences": [],
            "compatible": True
        }
        
        # Bu method daha kompleks test senaryoları için
        # Şimdilik basit versiyon
        
        return results
    
    def security_check(self, code: str) -> Tuple[bool, List[str]]:
        """
        Güvenlik kontrolü - tehlikeli kod var mı?
        """
        warnings = []
        
        dangerous_patterns = {
            r"os\.system": "System command execution",
            r"subprocess\..*shell=True": "Shell command with shell=True",
            r"exec\(": "Dynamic code execution",
            r"eval\(": "Eval usage",
            r"__import__": "Dynamic import",
            r"open\(.*['\"]w": "File write operation",
            r"shutil\.rmtree": "Directory deletion",
            r"os\.remove": "File deletion",
            r"sqlite3\.execute.*DROP": "Database DROP operation",
            r"requests\.get.*verify=False": "SSL verification disabled"
        }
        
        import re
        for pattern, description in dangerous_patterns.items():
            if re.search(pattern, code):
                warnings.append(description)
        
        is_safe = len(warnings) == 0
        return is_safe, warnings
    
    def performance_test(self, sandbox_dir: Path) -> Dict:
        """Performans testi - değişiklik yavaşlatıyor mu?"""
        # Basit performans metrikleri
        return {
            "startup_time": 0.0,
            "response_time": 0.0,
            "memory_usage": 0
        }