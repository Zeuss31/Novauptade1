"""
API İŞLEYİCİSİ
Tüm AI provider'larla iletişimi burada yönetiyoruz
Gemini API tam entegre edildi!
Web Search (Tavily) eklendi! 🔍
"""

from config.settings import Settings
import requests

class MultiProviderAPIHandler:
    """Çoklu AI provider'ı destekler"""
    
    def __init__(self, provider=None, model=None):
        self.provider = provider or Settings.DEFAULT_PROVIDER
        
        # MODEL SEÇİMİ DÜZELTMESİ
        # Frontend bazen index gönderiyor (0, 1, 2), bazen string gönderiyor
        if model is not None:
            # Eğer sayı (index) gönderilmişse
            if isinstance(model, int) or (isinstance(model, str) and model.isdigit()):
                try:
                    model_index = int(model)
                    available = Settings.AVAILABLE_MODELS.get(self.provider, [])
                    if 0 <= model_index < len(available):
                        model = available[model_index]
                    else:
                        model = None
                except:
                    model = None
        
        # Model hala None ise varsayılanı kullan
        if not model:
            model = Settings.DEFAULT_MODELS.get(self.provider)
        
        self.model = model
        self.client = self._init_client()
    
    def _init_client(self):
        """Provider'a göre client oluştur"""

        if self.provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=Settings.GOOGLE_API_KEY)
            return genai

        elif self.provider == "cerebras":
            from openai import OpenAI
            return OpenAI(
                api_key=Settings.CEREBRAS_API_KEY,
                base_url="https://api.cerebras.ai/v1"
            )

        else:
            raise ValueError(f"Desteklenmeyen provider: {self.provider}")

    
    # ═══════════════════════════════════════════════════════════
    # 🔍 WEB SEARCH - TAVILY API
    # ═══════════════════════════════════════════════════════════
    
    @staticmethod
    def web_search(query):
        """
        Tavily API kullanarak web araması yapar
        
        Args:
            query (str): Arama sorgusu
            
        Returns:
            dict: Arama sonuçları veya hata mesajı
        """
        try:
            # API key kontrolü
            if not Settings.TAVILY_API_KEY:
                return {
                    'success': False,
                    'error': 'Tavily API key tanımlanmamış. .env dosyasına TAVILY_API_KEY ekleyin.'
                }
            
            # Tavily API endpoint
            url = "https://api.tavily.com/search"
            
            # Request payload
            payload = {
                "api_key": Settings.TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",  # "basic" veya "advanced"
                "max_results": Settings.SEARCH_MAX_RESULTS,
                "include_answer": True,  # AI özeti dahil et
                "include_raw_content": False,  # Ham içerik gereksiz
                "include_images": False
            }
            
            # API'ye istek gönder
            response = requests.post(url, json=payload, timeout=10)
            
            # Hata kontrolü
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Tavily API hatası: {response.status_code}',
                    'details': response.text
                }
            
            # Sonuçları parse et
            data = response.json()
            
            # Sonuçları formatla
            results = {
                'success': True,
                'query': query,
                'answer': data.get('answer', ''),  # AI tarafından oluşturulan özet
                'results': []
            }
            
            # Her bir arama sonucunu ekle
            for item in data.get('results', []):
                results['results'].append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'content': item.get('content', ''),
                    'score': item.get('score', 0)
                })
            
            return results
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Arama zaman aşımına uğradı. Lütfen tekrar deneyin.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Bağlantı hatası: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Beklenmeyen hata: {str(e)}'
            }
    
    # ═══════════════════════════════════════════════════════════
    # NORMAL CHAT METODLARI
    # ═══════════════════════════════════════════════════════════
    
    def get_response(self, messages):
        try:
            if self.provider in ["groq", "openai", "deepinfra", "ollama", "cerebras"]:
                return self._get_openai_compatible_response(messages)
            
            elif self.provider == "anthropic":
                return self._get_anthropic_response(messages)
            
            elif self.provider == "google":
                return self._get_google_response(messages)
            
            elif self.provider == "cohere":
                return self._get_cohere_response(messages)
                
        except Exception as e:
            return f"❌ Hata ({self.provider}): {str(e)}"
    
    def get_streaming_response(self, messages):
        try:
            if self.provider in ["groq", "openai", "deepinfra", "ollama", "cerebras"]:
                yield from self._get_openai_compatible_streaming(messages)
            
            elif self.provider == "anthropic":
                yield from self._get_anthropic_streaming(messages)
            
            elif self.provider == "google":
                yield from self._get_google_streaming(messages)
            
            elif self.provider == "cohere":
                yield from self._get_cohere_streaming(messages)
                
        except Exception as e:
            yield f"❌ Hata ({self.provider}): {str(e)}"
    
    # ═══════════════════════════════════════════════════════════
    # GROQ & OPENAI & DEEPINFRA & OLLAMA & CEREBRAS (OpenAI API Uyumlu)
    # ═══════════════════════════════════════════════════════════
    
    def _get_openai_compatible_response(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=Settings.TEMPERATURE,
            max_tokens=Settings.MAX_TOKENS,
            top_p=Settings.TOP_P,
            frequency_penalty=Settings.FREQUENCY_PENALTY,
            presence_penalty=Settings.PRESENCE_PENALTY,
        )
        return response.choices[0].message.content
    
    def _get_openai_compatible_streaming(self, messages):
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=Settings.TEMPERATURE,
            max_tokens=Settings.MAX_TOKENS,
            top_p=Settings.TOP_P,
            frequency_penalty=Settings.FREQUENCY_PENALTY,
            presence_penalty=Settings.PRESENCE_PENALTY,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    # ═══════════════════════════════════════════════════════════
    # ANTHROPIC (Claude)
    # ═══════════════════════════════════════════════════════════
    
    def _get_anthropic_response(self, messages):
        system_msg = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=Settings.MAX_TOKENS,
            temperature=Settings.TEMPERATURE,
            system=system_msg,
            messages=user_messages
        )
        return response.content[0].text
    
    def _get_anthropic_streaming(self, messages):
        system_msg = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        
        with self.client.messages.stream(
            model=self.model,
            max_tokens=Settings.MAX_TOKENS,
            temperature=Settings.TEMPERATURE,
            system=system_msg,
            messages=user_messages
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    # ═══════════════════════════════════════════════════════════
    # GOOGLE (Gemini) - TAM ENTEGRASYONU YENİDEN YAZILDI
    # ═══════════════════════════════════════════════════════════
    
    def _get_google_response(self, messages):
        """Gemini API - Normal yanıt"""
        try:
            # Model oluştur
            model = self.client.GenerativeModel(
                model_name=self.model,
                generation_config={
                    "temperature": Settings.TEMPERATURE,
                    "top_p": Settings.TOP_P,
                    "max_output_tokens": Settings.MAX_TOKENS,
                }
            )
            
            # Mesajları dönüştür
            chat_history, current_prompt = self._convert_messages_for_gemini(messages)
            
            # Chat başlat
            if chat_history:
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(current_prompt)
            else:
                # İlk mesaj
                response = model.generate_content(current_prompt)
            
            # Response'dan text çıkar
            if hasattr(response, "text") and response.text:
                return response.text
            
            if hasattr(response, "candidates"):
                parts = response.candidates[0].content.parts
                return "".join(
                    part.text for part in parts if hasattr(part, "text")
                )
            
            return ""
            
        except Exception as e:
            return f"❌ Gemini Hatası: {str(e)}"
    
    def _get_google_streaming(self, messages):
        """Gemini API - Streaming yanıt"""
        try:
            # Model oluştur
            model = self.client.GenerativeModel(
                model_name=self.model,
                generation_config={
                    "temperature": Settings.TEMPERATURE,
                    "top_p": Settings.TOP_P,
                    "max_output_tokens": Settings.MAX_TOKENS,
                }
            )
            
            # Mesajları dönüştür
            chat_history, current_prompt = self._convert_messages_for_gemini(messages)
            
            # Chat başlat ve stream
            if chat_history:
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(current_prompt, stream=True)
            else:
                # İlk mesaj
                response = model.generate_content(current_prompt, stream=True)
            
            # Stream yanıtı
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"❌ Gemini Hatası: {str(e)}"
    
    def _convert_messages_for_gemini(self, messages):
        """
        OpenAI formatındaki mesajları Gemini formatına çevir
        
        OpenAI format:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
        
        Gemini format:
        history = [
            {"role": "user", "parts": ["..."]},
            {"role": "model", "parts": ["..."]}
        ]
        current_message = "son kullanıcı mesajı"
        """
        
        chat_history = []
        system_instruction = ""
        current_prompt = ""
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            # System mesajını sistem talimatı olarak ekle
            if role == "system":
                system_instruction = content
                continue
            
            # Son mesaj kullanıcıdan ise, onu current_prompt olarak sakla
            if i == len(messages) - 1 and role == "user":
                # Eğer system instruction varsa, başına ekle
                if system_instruction:
                    current_prompt = f"{system_instruction}\n\n{content}"
                else:
                    current_prompt = content
            else:
                # Geçmiş mesajları ekle
                if role == "user":
                    chat_history.append({
                        "role": "user",
                        "parts": [content]
                    })
                elif role == "assistant":
                    chat_history.append({
                        "role": "model",
                        "parts": [content]
                    })
        
        # Eğer current_prompt boşsa (örneğin sadece system mesajı varsa)
        if not current_prompt and messages:
            last_msg = messages[-1]
            if last_msg.get("role") == "user":
                content = last_msg.get("content", "")
                if system_instruction:
                    current_prompt = f"{system_instruction}\n\n{content}"
                else:
                    current_prompt = content
        
        return chat_history, current_prompt
    
    # ═══════════════════════════════════════════════════════════
    # COHERE
    # ═══════════════════════════════════════════════════════════
    
    def _get_cohere_response(self, messages):
        prompt = messages[-1]["content"] if messages else ""
        
        chat_history = []
        for i, msg in enumerate(messages[:-1]):
            if msg["role"] == "system":
                continue
            chat_history.append({
                "role": "USER" if msg["role"] == "user" else "CHATBOT",
                "message": msg["content"]
            })
        
        response = self.client.chat(
            model=self.model,
            message=prompt,
            chat_history=chat_history,
            temperature=Settings.TEMPERATURE,
        )
        return response.text
    
    def _get_cohere_streaming(self, messages):
        prompt = messages[-1]["content"] if messages else ""
        
        chat_history = []
        for msg in messages[:-1]:
            if msg["role"] == "system":
                continue
            chat_history.append({
                "role": "USER" if msg["role"] == "user" else "CHATBOT",
                "message": msg["content"]
            })
        
        response = self.client.chat_stream(
            model=self.model,
            message=prompt,
            chat_history=chat_history,
            temperature=Settings.TEMPERATURE,
        )
        
        for event in response:
            if event.event_type == "text-generation":
                yield event.text


# Eski sınıf adı ile uyumluluk için
GroqAPIHandler = MultiProviderAPIHandler