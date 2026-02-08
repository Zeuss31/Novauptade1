"""
CODE EXECUTOR
Güvenli Python kod çalıştırıcı (sandbox)
"""

import sys
import io
import contextlib
import traceback
import signal
import ast
from typing import Dict, Tuple

class CodeExecutor:
    """Güvenli kod çalıştırma sistemi"""
    
    # Yasaklı modüller (güvenlik için)
    BLOCKED_MODULES = {
        'os', 'subprocess', 'sys', 'importlib', '__import__',
        'open', 'eval', 'exec', 'compile', 'file', 'input'
    }
    
    # İzin verilen modüller
    ALLOWED_MODULES = {
        'math', 'random', 'datetime', 'json', 'collections',
        'itertools', 're', 'string', 'time'
    }
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
    
    def execute(self, code: str) -> Dict:
        """
        Kodu çalıştır ve sonucu döndür
        
        Returns:
            {
                'success': bool,
                'output': str,
                'error': str,
                'execution_time': float
            }
        """
        # Güvenlik kontrolü
        if not self._is_safe(code):
            return {
                'success': False,
                'output': '',
                'error': 'Güvenlik hatası: Yasaklı kod kullanımı tespit edildi',
                'execution_time': 0
            }
        
        # Output'u yakala
        stdout = io.StringIO()
        stderr = io.StringIO()
        
        try:
            import time
            start_time = time.time()
            
            # Kodu çalıştır (timeout ile)
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                # Güvenli namespace
                safe_globals = {
                    '__builtins__': {
                        'print': print,
                        'len': len,
                        'range': range,
                        'str': str,
                        'int': int,
                        'float': float,
                        'bool': bool,
                        'list': list,
                        'dict': dict,
                        'set': set,
                        'tuple': tuple,
                        'abs': abs,
                        'sum': sum,
                        'min': min,
                        'max': max,
                        'sorted': sorted,
                        'enumerate': enumerate,
                        'zip': zip,
                        'map': map,
                        'filter': filter,
                        'type': type,
                        'isinstance': isinstance,
                        'hasattr': hasattr,
                        'getattr': getattr,
                    }
                }
                
                # İzinli modülleri ekle
                for module_name in self.ALLOWED_MODULES:
                    try:
                        safe_globals[module_name] = __import__(module_name)
                    except:
                        pass
                
                # Timeout handler
                def timeout_handler(signum, frame):
                    raise TimeoutError("Kod çalıştırma süresi aşıldı")
                
                # Timeout ayarla (sadece Unix sistemlerde çalışır)
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(self.timeout)
                except:
                    pass  # Windows'da signal yok
                
                # Kodu çalıştır
                exec(code, safe_globals)
                
                # Timeout'u iptal et
                try:
                    signal.alarm(0)
                except:
                    pass
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'output': stdout.getvalue(),
                'error': stderr.getvalue(),
                'execution_time': execution_time
            }
        
        except TimeoutError as e:
            return {
                'success': False,
                'output': stdout.getvalue(),
                'error': f"Timeout: {str(e)}",
                'execution_time': self.timeout
            }
        
        except Exception as e:
            return {
                'success': False,
                'output': stdout.getvalue(),
                'error': f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                'execution_time': 0
            }
    
    def _is_safe(self, code: str) -> bool:
        """Kod güvenli mi kontrol et"""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Import kontrolü
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.BLOCKED_MODULES:
                            return False
                        if alias.name not in self.ALLOWED_MODULES:
                            return False
                
                if isinstance(node, ast.ImportFrom):
                    if node.module in self.BLOCKED_MODULES:
                        return False
                    if node.module not in self.ALLOWED_MODULES:
                        return False
                
                # Tehlikeli fonksiyon çağrıları
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', 'compile', '__import__']:
                            return False
                
                # File işlemleri
                if isinstance(node, ast.Name):
                    if node.id in ['open', 'file']:
                        return False
            
            return True
        
        except SyntaxError:
            return False
    
    def validate_syntax(self, code: str) -> Tuple[bool, str]:
        """Syntax kontrolü yap"""
        try:
            ast.parse(code)
            return True, "Syntax geçerli"
        except SyntaxError as e:
            return False, f"Syntax hatası: {str(e)}"