"""
AYARLAR DOSYASI
Tüm konfigürasyonlar burada
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Settings:
    """Uygulama ayarları"""

    # ═══════════════════════════════════════════════════════════
    # AI PROVIDER API KEY'LERİ
    # ═══════════════════════════════════════════════════════════

    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    COHERE_API_KEY = os.getenv('COHERE_API_KEY', '')
    DEEPINFRA_API_KEY = os.getenv('DEEPINFRA_API_KEY', '')
    OLLAMA_BASE_URL = "http://localhost:11434/v1"
    CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY', '')

    # WEB SEARCH API KEY
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')

    # ═══════════════════════════════════════════════════════════
    # MODEL AYARLARI
    # ═══════════════════════════════════════════════════════════

    # Varsayılan provider
    DEFAULT_PROVIDER = "cerebras"

    # Her provider için kullanılabilir modeller
    AVAILABLE_MODELS = {
        "google": [
            "gemini-2.5-flash",
            "gemini-2.0-flash-exp"
        ],
        "cerebras": [
            "llama-3.3-70b",
            
        ]   
    }

    DEFAULT_MODELS = {
        "google": "gemini-2.5-flash",
        "cerebras": "llama3.3-70b"
        
    }

    # ═══════════════════════════════════════════════════════════
    # GENERATION PARAMETRELERI
    # ═══════════════════════════════════════════════════════════

    TEMPERATURE = 0.7
    MAX_TOKENS = 8192
    TOP_P = 0.9
    FREQUENCY_PENALTY = 0.0
    PRESENCE_PENALTY = 0.0

    # ═══════════════════════════════════════════════════════════
    # WEB SEARCH AYARLARI
    # ═══════════════════════════════════════════════════════════

    SEARCH_MAX_RESULTS = 5
    SEARCH_ENABLED = True

    # ═══════════════════════════════════════════════════════════
    # CONVERSATION AYARLARI
    # ═══════════════════════════════════════════════════════════

    AI_NAME = "Nova"
    MAX_HISTORY = 20

    # ═══════════════════════════════════════════════════════════
    # DATABASE AYARLARI
    # ═══════════════════════════════════════════════════════════

    DATABASE_PATH = "data/conversations.db"

    # ═══════════════════════════════════════════════════════════
    # FLASK WEB SERVER AYARLARI
    # ═══════════════════════════════════════════════════════════

    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5000
    FLASK_DEBUG = True

    # ═══════════════════════════════════════════════════════════
    # DOSYA YÜKLEME AYARLARI
    # ═══════════════════════════════════════════════════════════

    UPLOAD_FOLDER = "uploads"
    MAX_FILE_SIZE = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'js', 'json', 'csv'}


def check_settings():
    """Ayarları kontrol et"""

    has_api_key = any([
        Settings.GROQ_API_KEY,
        Settings.OPENAI_API_KEY,
        Settings.ANTHROPIC_API_KEY,
        Settings.GOOGLE_API_KEY,
        Settings.COHERE_API_KEY,
        Settings.DEEPINFRA_API_KEY,
        True  # Ollama her zaman mevcut (local)
    ])

    if not has_api_key:
        print("""
╔════════════════════════════════════════════════════════════╗
║                    ⚠️  UYARI: API KEY YOK                  ║
╚════════════════════════════════════════════════════════════╝

Ollama local çalışır (rate limit yok) ama diğer provider'lar için API key gerekir.
""")

    # Web Search kontrolü
    if Settings.SEARCH_ENABLED and not Settings.TAVILY_API_KEY:
        print("""
╔════════════════════════════════════════════════════════════╗
║                🔍 Web Search aktif ama API key yok!        ║
╚════════════════════════════════════════════════════════════╝

Tavily API key eklemek için: https://tavily.com
""")

    Path("data").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)
    Path("static/audio").mkdir(parents=True, exist_ok=True)

    return True