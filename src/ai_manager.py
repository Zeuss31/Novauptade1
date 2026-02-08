"""
AI API KEY ROTATOR - Gemini ve Groq için otomatik key rotasyonu
"""
import time
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path

class AIManager:
    def __init__(self):
        # ==================== BU KISMI DOLDUR ====================
        self.api_keys = {
            'google': [
                'AIzaSyCSYFNdgicjFd1_uzUIGVRHl5GFdQ50WQo',    # 1. Gemini key
                'AIzaSyDScIN1WXXuRR7lXAkoGlGgpcwQoSFPLfc',    # 2. Gemini key
            ],
            'groq': [
                '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',      # 1. Groq key
                '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',      # 2. Groq key
            ]
        }
        # =========================================================
        
        # Cache sistemi
        self.cache_file = 'ai_cache.json'
        self.cache = self.load_cache()
        
        # Rate limit takibi
        self.usage_file = 'usage_log.json'
        self.usage = self.load_usage()
        
        # Hangi key'deyiz
        self.current_provider = 'google'
        self.current_key_idx = 0
        
        # Her API için limitler (ücretsiz tier - GERÇEK LİMİTLER)
        self.limits = {
            'google': {
                'per_key': 250,        # Gemini 2.5 Flash: 250 requests/day
                'per_minute': 10       # 10 RPM
            },
            'groq': {
                'per_key': 14400,      # 14,400 requests/day  
                'per_minute': 30       # 30 RPM (değişken model bazlı)
            }
        }
    
    def load_cache(self):
        if Path(self.cache_file).exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def load_usage(self):
        if Path(self.usage_file).exists():
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        return {'date': datetime.now().strftime('%Y-%m-%d'), 'keys': {}}
    
    def save_usage(self):
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)
    
    def reset_daily_usage(self):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.usage.get('date') != today:
            self.usage = {'date': today, 'keys': {}}
            self.save_usage()
    
    def get_cache_key(self, prompt):
        return hashlib.md5(prompt.strip().lower().encode()).hexdigest()
    
    def get_from_cache(self, prompt):
        key = self.get_cache_key(prompt)
        return self.cache.get(key)
    
    def add_to_cache(self, prompt, response):
        key = self.get_cache_key(prompt)
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        self.save_cache()
    
    def get_key_usage_count(self, provider, key_idx):
        key_id = f"{provider}_{key_idx}"
        return self.usage['keys'].get(key_id, 0)
    
    def increment_key_usage(self, provider, key_idx):
        key_id = f"{provider}_{key_idx}"
        self.usage['keys'][key_id] = self.usage['keys'].get(key_id, 0) + 1
        self.save_usage()
    
    def find_available_key(self):
        """Kullanılabilir key bul, limit dolmamış olanı seç"""
        self.reset_daily_usage()
        
        # Tüm providerları dene
        for provider in self.api_keys.keys():
            keys = self.api_keys[provider]
            limit = self.limits[provider]['per_key']
            
            # Bu providerin tüm keylerini kontrol et
            for idx in range(len(keys)):
                usage = self.get_key_usage_count(provider, idx)
                if usage < limit:
                    return provider, idx, keys[idx]
        
        return None, None, None
    
    def call_google(self, api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 2048,  # Kesilmeyi önlemek için artırıldı
            "temperature": 0.7,
            "topP": 0.8
        }
    }
    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()
    return response.json()['candidates'][0]['content']['parts'][0]['text']
    
    def call_groq(self, api_key, prompt):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def ask(self, prompt, use_cache=True):
        """Ana fonksiyon - AI'ya soru sor"""
        
        # 1. Cache kontrol et
        if use_cache:
            cached = self.get_from_cache(prompt)
            if cached:
                print("✓ Cache'den geldi")
                return cached['response']
        
        # 2. Kullanılabilir key bul
        provider, key_idx, api_key = self.find_available_key()
        
        if not api_key:
            return "❌ Tüm API keylerin günlük limiti doldu! Yarın tekrar dene."
        
        print(f"🔑 Kullanılan: {provider} - Key #{key_idx + 1}")
        
        # 3. Rate limit için bekle
        per_minute = self.limits[provider]['per_minute']
        time.sleep(60 / per_minute)
        
        # 4. API çağrısı yap
        try:
            if provider == 'google':
                response = self.call_google(api_key, prompt)
            elif provider == 'groq':
                response = self.call_groq(api_key, prompt)
            else:
                return f"❌ Bilinmeyen provider: {provider}"
            
            # 5. Cache'e kaydet ve kullanımı logla
            self.add_to_cache(prompt, response)
            self.increment_key_usage(provider, key_idx)
            
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"⚠️  {provider} Key #{key_idx + 1} rate limit yedi, bir sonrakine geçiliyor...")
                # Bu keyi kullanılamaz işaretle (limitini doldur)
                limit = self.limits[provider]['per_key']
                key_id = f"{provider}_{key_idx}"
                self.usage['keys'][key_id] = limit
                self.save_usage()
                # Tekrar dene
                return self.ask(prompt, use_cache=False)
            else:
                return f"❌ API Hatası: {str(e)}"
        except Exception as e:
            return f"❌ Hata: {str(e)}"
    
    def get_stats(self):
        """İstatistikleri göster"""
        self.reset_daily_usage()
        
        stats = "📊 API KEY DURUMU:\n" + "="*50 + "\n"
        
        for provider in self.api_keys.keys():
            keys = self.api_keys[provider]
            limit = self.limits[provider]['per_key']
            
            stats += f"\n🔹 {provider.upper()}:\n"
            for idx in range(len(keys)):
                usage = self.get_key_usage_count(provider, idx)
                percentage = (usage / limit) * 100
                bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
                stats += f"  Key #{idx + 1}: [{bar}] {usage}/{limit} ({percentage:.1f}%)\n"
        
        stats += f"\n💾 Cache: {len(self.cache)} soru kayıtlı\n"
        stats += f"📅 Tarih: {self.usage.get('date')}"
        
        return stats
    
    def clear_cache(self):
        """Cache'i temizle"""
        self.cache = {}
        self.save_cache()
        print("✓ Cache temizlendi")
    
    def reset_usage(self):
        """Kullanım sayaçlarını sıfırla (test için)"""
        self.usage = {'date': datetime.now().strftime('%Y-%m-%d'), 'keys': {}}
        self.save_usage()
        print("✓ Kullanım sayaçları sıfırlandı")


# ==================== KULLANIM ÖRNEĞİ ====================
if __name__ == "__main__":
    # AI Manager'ı başlat
    ai = AIManager()
    
    # İstatistikleri göster
    print(ai.get_stats())
    print("\n")
    
    # Soru sor
    sorular = [
        "Python'da liste nasıl oluşturulur?",
        "JavaScript'te array nasıl döngüye alınır?",
        "React nedir kısaca açıkla",
    ]
    
    for soru in sorular:
        print(f"❓ Soru: {soru}")
        cevap = ai.ask(soru)
        print(f"💬 Cevap: {cevap[:200]}...\n")
        print("-" * 50 + "\n")
    
    # Son durum
    print("\n" + ai.get_stats())