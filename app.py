"""
FLASK WEB UYGULAMASI - SELF-IMPROVEMENT + ARTIFACT SYSTEM + WEB SEARCH + BINANCE WEBSOCKET + AI PREDICTION 🔥
Tam çalışır versiyon - HİÇBİR ÖZELLİK EKSİK DEĞİL!
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from config.settings import Settings, check_settings
from src.api_handler import MultiProviderAPIHandler
from src.conversation import ConversationManager
from src.database import Database
from src.personality import Personality 

# Self-improvement modülleri
from src.self_improver import SelfImprover
from src.learning_engine import LearningEngine
from src.feedback_system import FeedbackSystem
from src.dynamic_personality import DynamicPersonality

# Artifact modülleri
from src.artifact_manager import ArtifactManager
from src.code_executor import CodeExecutor
from src.artifact_detector import ArtifactDetector

# Prediction Engine
from src.prediction_engine import AdvancedPredictionEngine as PredictionEngine

import os
import random
from gtts import gTTS
import uuid
import websocket
import json
import threading
import time
from collections import deque
from datetime import datetime
import re

# Flask uygulaması
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['MAX_CONTENT_LENGTH'] = Settings.MAX_FILE_SIZE
app.config['SECRET_KEY'] = 'nova-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)

# Global değişkenler
db = Database()
active_conversations = {}

# Self-improvement sistemi
learning_engine = LearningEngine()
feedback_system = FeedbackSystem(learning_engine)
dynamic_personality = DynamicPersonality(learning_engine)
self_improver = SelfImprover(auto_apply=False)

# Artifact sistemi
artifact_manager = ArtifactManager()
code_executor = CodeExecutor()

# Prediction Engine
prediction_engine = PredictionEngine()

# ============ BINANCE WEBSOCKET SİSTEMİ + GRAFİK VERİ SAKLAMA ============
binance_ws = None
binance_thread = None

# Her coin için fiyat geçmişi (son 100 veri)
price_history = {}

def normalize_text_stream(text: str) -> str:
    """Streaming metin normalizasyonu - kelime birleşmelerini düzelt"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', text)
    return text

def on_binance_message(ws, message):
    """Binance'den gelen veriyi işle ve frontend'e gönder"""
    try:
        data = json.loads(message)
        stream_name = data.get('stream', 'unknown')
        
        if 'data' in data:
            trade_data = data['data']
            symbol = stream_name.split('@')[0].upper()
            price = float(trade_data['p'])
            quantity = float(trade_data.get('q', 0))
            timestamp = trade_data['T']
            
            # Fiyat geçmişine ekle (grafik için)
            if symbol not in price_history:
                price_history[symbol] = deque(maxlen=100)
            
            price_history[symbol].append({
                'price': price,
                'timestamp': timestamp,
                'time': time.strftime('%H:%M:%S', time.localtime(timestamp/1000))
            })
            
            # Prediction Engine'e veri ekle (volume ile birlikte)
            prediction_engine.add_price_data(
                symbol=symbol, 
                price=price, 
                volume=quantity,
                timestamp=datetime.fromtimestamp(timestamp/1000)
            )
        
        # Frontend'e gönder
        socketio.emit('binance_update', data, namespace='/', to=None)
        socketio.sleep(0)
        
    except Exception as e:
        print(f"❌ Binance mesaj hatası: {e}")

def on_binance_error(ws, error):
    print(f"❌ Binance WebSocket hatası: {error}")

def on_binance_close(ws, close_status_code, close_msg):
    print("🔴 Binance bağlantısı kapandı")

def on_binance_open(ws):
    print("✅ Binance WebSocket bağlantısı kuruldu!")

def start_binance_websocket(symbols):
    """Binance WebSocket'i başlat (Multi-stream) - ÇOK COİN DESTEĞİ"""
    global binance_ws
    
    streams = '/'.join([f"{s}@trade" for s in symbols])
    url = f"wss://stream.binance.com:9443/stream?streams={streams}"
    
    print(f"🔗 Bağlanılan coinler: {', '.join([s.upper() for s in symbols])}")
    
    binance_ws = websocket.WebSocketApp(
        url,
        on_open=on_binance_open,
        on_message=on_binance_message,
        on_error=on_binance_error,
        on_close=on_binance_close
    )
    
    binance_ws.run_forever()

def stop_binance_websocket():
    """Binance WebSocket'i durdur"""
    global binance_ws
    if binance_ws:
        binance_ws.close()
        print("🛑 Binance WebSocket durduruldu")


# ============ SAYFA ROUTE'LARI ============

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/admin')
def admin():
    """Admin Dashboard - Self-Improvement Paneli"""
    return render_template('admin_dashboard.html')


@app.route('/artifact-test')
def artifact_test():
    """Artifact test sayfası"""
    return render_template('artifact_test.html')


# ============ BINANCE API'LERİ ============

@app.route('/api/binance/start', methods=['POST'])
def start_binance():
    """Binance WebSocket'i başlat - ÇOK COİN DESTEĞİ"""
    global binance_thread
    
    data = request.json
    # ⬇️ VARSAYILAN 20+ COİN
    symbols = data.get('symbols', [
        'btcusdt', 'ethusdt', 'bnbusdt', 'solusdt', 'xrpusdt',
        'adausdt', 'dogeusdt', 'maticusdt', 'dotusdt', 'linkusdt',
        'uniusdt', 'ltcusdt', 'avaxusdt', 'atomusdt', 'shibusdt',
        'nearusdt', 'filusdt', 'aptusdt', 'opusdt', 'arbusdt',
        'suiusdt', 'injusdt', 'thetausdt', 'ldousdt', 'ftmusdt'
    ])
    
    if binance_thread and binance_thread.is_alive():
        return jsonify({"error": "Binance zaten çalışıyor"}), 400
    
    binance_thread = threading.Thread(target=start_binance_websocket, args=(symbols,))
    binance_thread.daemon = True
    binance_thread.start()
    
    return jsonify({
        "success": True, 
        "message": f"{len(symbols)} coin için Binance WebSocket başlatıldı", 
        "symbols": symbols
    })


@app.route('/api/binance/stop', methods=['POST'])
def stop_binance():
    """Binance WebSocket'i durdur"""
    stop_binance_websocket()
    return jsonify({"success": True, "message": "Binance WebSocket durduruldu"})


@app.route('/api/binance/status', methods=['GET'])
def binance_status():
    """Binance durumunu kontrol et"""
    is_running = binance_thread and binance_thread.is_alive()
    return jsonify({"running": is_running})


@app.route('/api/binance/history/<symbol>', methods=['GET'])
def get_price_history(symbol):
    """Belirli bir coin'in fiyat geçmişini getir (grafik için)"""
    symbol = symbol.upper()
    
    if symbol not in price_history:
        return jsonify({"error": "Bu coin için veri yok"}), 404
    
    # Deque'yi listeye çevir
    history_list = list(price_history[symbol])
    
    return jsonify({
        "symbol": symbol,
        "data": history_list,
        "count": len(history_list)
    })


# ============ AI PREDICTION API'LERİ 🤖📈 ============

@app.route('/api/prediction/<symbol>', methods=['GET'])
def get_prediction(symbol):
    """Belirli bir coin için AI tahmini"""
    symbol = symbol.upper()
    prediction = prediction_engine.generate_advanced_prediction(symbol)
    return jsonify(prediction)


@app.route('/api/prediction/opportunities', methods=['GET'])
def get_opportunities():
    """En iyi yatırım fırsatları"""
    top_n = request.args.get('limit', default=5, type=int)
    min_confidence = request.args.get('min_confidence', default=65, type=float)
    opportunities = prediction_engine.get_top_opportunities(min_confidence, top_n)
    return jsonify(opportunities)


@app.route('/api/prediction/alerts', methods=['GET'])
def get_risk_alerts():
    """Risk uyarıları"""
    alerts = prediction_engine.get_risk_alerts()
    return jsonify(alerts)


@app.route('/api/prediction/market-summary', methods=['GET'])
def get_market_summary():
    """Piyasa özeti"""
    summary = prediction_engine.generate_market_summary()
    if not summary:
        return jsonify({"error": "Henüz veri yok"}), 404
    return jsonify(summary)


@app.route('/api/prediction/statistics/<symbol>', methods=['GET'])
def get_symbol_statistics(symbol):
    """Coin istatistikleri"""
    symbol = symbol.upper()
    stats = prediction_engine.get_symbol_statistics(symbol)
    if not stats:
        return jsonify({"error": "Veri yok"}), 404
    return jsonify(stats)


# ============ PROVIDER & MODEL API'LERİ ============

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Mevcut provider'ları ve modellerini getir"""
    return jsonify({
        "providers": list(Settings.AVAILABLE_MODELS.keys()),
        "models": Settings.AVAILABLE_MODELS,
        "default_provider": Settings.DEFAULT_PROVIDER,
        "default_models": Settings.DEFAULT_MODELS
    })


# ============ WEB SEARCH API 🔍 ============

@app.route('/api/search', methods=['POST'])
def web_search():
    """Web'de arama yap"""
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({"error": "Arama sorgusu boş"}), 400
    
    results = MultiProviderAPIHandler.web_search(query)
    return jsonify(results)


# ============ CONVERSATION API'LERİ ============

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Tüm sohbetleri getir"""
    conversations = db.get_conversations()
    return jsonify(conversations)


@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Yeni sohbet oluştur"""
    data = request.json
    title = data.get('title', 'Yeni Sohbet')
    conv_id = db.create_conversation(title)
    return jsonify({"id": conv_id, "title": title})


@app.route('/api/conversations/<int:conv_id>', methods=['DELETE'])
def delete_conversation(conv_id):
    """Sohbet sil"""
    db.delete_conversation(conv_id)
    if conv_id in active_conversations:
        del active_conversations[conv_id]
    return jsonify({"success": True})


@app.route('/api/conversations/delete-all', methods=['DELETE'])
def delete_all_conversations():
    """Tüm sohbetleri sil - YENİ!"""
    try:
        conversations = db.get_conversations()
        deleted_count = 0
        
        for conv in conversations:
            db.delete_conversation(conv['id'])
            if conv['id'] in active_conversations:
                del active_conversations[conv['id']]
            deleted_count += 1
        
        return jsonify({
            "success": True, 
            "message": f"{deleted_count} sohbet silindi",
            "deleted_count": deleted_count
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/conversations/<int:conv_id>/messages', methods=['GET'])
def get_messages(conv_id):
    """Sohbet mesajlarını getir"""
    messages = db.get_messages(conv_id)
    return jsonify(messages)


# ============ CHAT API (STREAMING + MARKET ANALYSIS) ============

@app.route('/api/chat', methods=['POST'])
def chat():
    """Mesaj gönder ve cevap al (Streaming + Artifact Detection + Market Analysis)"""
    data = request.json
    conv_id = data.get('conversation_id')
    message = data.get('message')
    provider = data.get('provider', Settings.DEFAULT_PROVIDER)
    model = data.get('model')
    
    if not conv_id or not message:
        return jsonify({"error": "Eksik parametreler"}), 400
    
    # Conversation Manager'ı hazırla
    if conv_id not in active_conversations:
        conv_manager = ConversationManager()
        api_handler = MultiProviderAPIHandler(provider, model)
        active_conversations[conv_id] = (conv_manager, api_handler)
        
        # Eski mesajları yükle
        old_messages = db.get_messages(conv_id)
        for msg in old_messages:
            if msg['role'] == 'user':
                conv_manager.add_user_message(msg['content'])
            elif msg['role'] == 'assistant':
                conv_manager.add_assistant_message(msg['content'])
    else:
        conv_manager, api_handler = active_conversations[conv_id]
        
        # Model değiştiyse yeni handler oluştur
        if provider != api_handler.provider or (model and model != api_handler.model):
            api_handler = MultiProviderAPIHandler(provider, model)
            active_conversations[conv_id] = (conv_manager, api_handler)
    
    # LEARNING: Implicit feedback analizi
    implicit_feedback = feedback_system.analyze_implicit_feedback(
        message, 
        conv_manager.get_messages()
    )
    
    # Kullanıcı mesajını kaydet
    conv_manager.add_user_message(message)
    db.save_message(conv_id, 'user', message)
    
    # PİYASA ANALİZİ KONTROLÜ - Anahtar kelimeler
    market_keywords = [
        'btc', 'eth', 'bnb', 'crypto', 'coin', 'piyasa', 'market', 
        'fiyat', 'price', 'analiz', 'analysis', 'tahmin', 'prediction',
        'al', 'sat', 'buy', 'sell', 'yükseliş', 'düşüş', 'trend',
        'rsi', 'macd', 'trading', 'yatırım', 'investment', 'kripto',
        'usdt', 'sol', 'xrp', 'ada', 'doge', 'matic', 'dot', 'link'
    ]
    
    message_lower = message.lower()
    is_market_query = any(keyword in message_lower for keyword in market_keywords)
    
    # DYNAMIC PERSONALITY + MARKET CONTEXT: System prompt'u zenginleştir
    messages = conv_manager.get_messages()
    if messages and messages[0]['role'] == 'system':
        base_prompt = messages[0]['content']
        enhanced_prompt = dynamic_personality.get_enhanced_system_prompt(base_prompt)
        
        # Eğer piyasa sorusu ise market context ekle
        if is_market_query:
            try:
                # Mesajdan coin sembolü çıkarmaya çalış
                detected_symbol = None
                for word in message_lower.split():
                    word_clean = word.strip('.,!?')
                    if word_clean.upper() in [s.upper() for s in price_history.keys()]:
                        detected_symbol = word_clean.upper()
                        break
                
                # Eğer sembol bulunamazsa, en aktif coin'leri kontrol et
                if not detected_symbol and price_history:
                    # BTC'yi varsayılan olarak al
                    if 'BTCUSDT' in price_history:
                        detected_symbol = 'BTCUSDT'
                    else:
                        detected_symbol = list(price_history.keys())[0]
                
                # Prediction ve market summary'yi al
                prediction_data = None
                if detected_symbol:
                    prediction_data = prediction_engine.generate_advanced_prediction(detected_symbol)
                
                market_summary = prediction_engine.generate_market_summary()
                
                # Market context'i ekle
                if prediction_data or market_summary:
                    market_context = Personality.get_market_analysis_context(
                        prediction_data=prediction_data,
                        market_summary=market_summary
                    )
                    enhanced_prompt += market_context
                    
            except Exception as e:
                print(f"⚠️ Market context oluşturma hatası: {e}")
        
        messages[0]['content'] = enhanced_prompt
    
    def generate():
        """Streaming response generator"""
        full_response = ""
        try:
            # API'den streaming yanıt al
            for chunk in api_handler.get_streaming_response(messages):
                fixed = normalize_text_stream(chunk)
                full_response += fixed
                yield f"data: {fixed}\n\n"
            
            # Yanıtı kaydet
            conv_manager.add_assistant_message(full_response)
            db.save_message(conv_id, 'assistant', full_response)
            
            # LEARNING: Konuşma kalitesi metriklerini kaydet
            quality_metrics = feedback_system.analyze_conversation_quality(
                conv_manager.get_messages()
            )
            
            for metric_name, metric_value in quality_metrics.items():
                learning_engine.record_metric(metric_name, metric_value, f"conv_{conv_id}")
            
            # Implicit feedback'i kaydet
            if implicit_feedback['sentiment'] != 'neutral':
                learning_engine.record_feedback(
                    conv_id, 
                    len(conv_manager.get_messages()), 
                    'implicit',
                    implicit_feedback['rating'],
                    str(implicit_feedback)
                )
            
            # ARTIFACT TESPİT ET VE OLUŞTUR
            if ArtifactDetector.should_create_artifact(full_response):
                detected_artifacts = ArtifactDetector.detect(full_response)
                
                for art in detected_artifacts:
                    artifact = artifact_manager.create_artifact(
                        artifact_type=art['type'],
                        content=art['content'],
                        title=art['title'],
                        language=art.get('language'),
                        conversation_id=conv_id
                    )
                    
                    # Frontend'e artifact bilgisini gönder
                    yield f"data: [ARTIFACT:{artifact['id']}]\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: ❌ Hata: {str(e)}\n\n"
            yield "data: [DONE]\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


# ============ FEEDBACK API ============

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Kullanıcı feedback'i kaydet"""
    data = request.json
    conv_id = data.get('conversation_id')
    message_id = data.get('message_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not all([conv_id, message_id, rating]):
        return jsonify({"error": "Eksik parametreler"}), 400
    
    feedback_system.collect_explicit_feedback(conv_id, message_id, rating, comment)
    
    return jsonify({"success": True, "message": "Feedback kaydedildi"})


# ============ ARTIFACT API'LERİ ============

@app.route('/api/artifacts', methods=['GET'])
def list_artifacts():
    """Tüm artifact'ları listele"""
    conv_id = request.args.get('conversation_id', type=int)
    artifacts = artifact_manager.list_artifacts(conv_id)
    return jsonify(artifacts)


@app.route('/api/artifacts', methods=['POST'])
def create_artifact_route():
    """Yeni artifact oluştur"""
    data = request.json
    
    artifact = artifact_manager.create_artifact(
        artifact_type=data.get('type', 'code'),
        content=data.get('content', ''),
        title=data.get('title', 'Untitled'),
        language=data.get('language'),
        conversation_id=data.get('conversation_id')
    )
    
    return jsonify(artifact)


@app.route('/api/artifacts/<artifact_id>', methods=['GET'])
def get_artifact(artifact_id):
    """Artifact detayını getir"""
    artifact = artifact_manager.get_artifact(artifact_id)
    
    if not artifact:
        return jsonify({"error": "Artifact bulunamadı"}), 404
    
    return jsonify(artifact)


@app.route('/api/artifacts/<artifact_id>', methods=['PUT'])
def update_artifact(artifact_id):
    """Artifact'ı güncelle"""
    data = request.json
    new_content = data.get('content')
    
    if not new_content:
        return jsonify({"error": "content gerekli"}), 400
    
    try:
        artifact = artifact_manager.update_artifact(artifact_id, new_content)
        return jsonify(artifact)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@app.route('/api/artifacts/<artifact_id>', methods=['DELETE'])
def delete_artifact(artifact_id):
    """Artifact'ı sil"""
    success = artifact_manager.delete_artifact(artifact_id)
    
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Artifact bulunamadı"}), 404


@app.route('/api/artifacts/<artifact_id>/versions/<int:version>', methods=['GET'])
def get_artifact_version(artifact_id, version):
    """Artifact'ın belirli versiyonunu getir"""
    content = artifact_manager.get_version(artifact_id, version)
    
    if content is None:
        return jsonify({"error": "Versiyon bulunamadı"}), 404
    
    return jsonify({"version": version, "content": content})


@app.route('/api/artifacts/<artifact_id>/export', methods=['GET'])
def export_artifact(artifact_id):
    """Artifact'ı dosya olarak export et"""
    try:
        filepath = artifact_manager.export_artifact(artifact_id)
        return jsonify({"success": True, "filepath": filepath})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@app.route('/api/code/execute', methods=['POST'])
def execute_code():
    """Python kodunu güvenli şekilde çalıştır"""
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({"error": "Kod boş"}), 400
    
    result = code_executor.execute(code)
    return jsonify(result)


@app.route('/api/code/validate', methods=['POST'])
def validate_code():
    """Kod syntax'ını kontrol et"""
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({"error": "Kod boş"}), 400
    
    is_valid, message = code_executor.validate_syntax(code)
    return jsonify({"valid": is_valid, "message": message})


@app.route('/api/artifacts/detect', methods=['POST'])
def detect_artifacts():
    """Metinde artifact var mı tespit et"""
    data = request.json
    text = data.get('text', '')
    
    artifacts = ArtifactDetector.detect(text)
    should_create = ArtifactDetector.should_create_artifact(text)
    
    return jsonify({
        "should_create": should_create,
        "artifacts": artifacts,
        "count": len(artifacts)
    })


# ============ ADMIN API'LERİ (SELF-IMPROVEMENT) ============

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Dashboard stats"""
    stats = self_improver.get_dashboard_stats()
    return jsonify(stats)


@app.route('/api/admin/suggestions', methods=['GET'])
def get_suggestions():
    """Bekleyen öneriler"""
    suggestions = learning_engine.get_pending_improvements()
    return jsonify(suggestions)


@app.route('/api/admin/analyze', methods=['POST'])
def trigger_analysis():
    """Analiz tetikle"""
    suggestions = self_improver.analyze_and_suggest()
    return jsonify({
        "success": True,
        "suggestions_count": len(suggestions),
        "suggestions": suggestions
    })


@app.route('/api/admin/test/<int:improvement_id>', methods=['POST'])
def test_improvement(improvement_id):
    """Öneriyi test et"""
    success, message = self_improver.test_improvement(improvement_id)
    return jsonify({"success": success, "message": message})


@app.route('/api/admin/apply/<int:improvement_id>', methods=['POST'])
def apply_improvement(improvement_id):
    """Öneriyi uygula"""
    data = request.json
    force = data.get('force', False)
    confirmation = data.get('confirmation', '')
    
    if confirmation != "I UNDERSTAND THE RISKS":
        return jsonify({"success": False, "message": "Confirmation required"}), 400
    
    success, message = self_improver.apply_improvement(improvement_id, force)
    return jsonify({"success": success, "message": message})


@app.route('/api/admin/rollback', methods=['POST'])
def rollback_change():
    """Değişikliği geri al"""
    data = request.json
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({"error": "file_path gerekli"}), 400
    
    success, message = self_improver.rollback_last_change(file_path)
    return jsonify({"success": success, "message": message})


@app.route('/api/admin/kill-switch', methods=['POST'])
def toggle_kill_switch():
    """Kill switch aç/kapat"""
    data = request.json
    action = data.get('action')
    reason = data.get('reason', 'Manual toggle')
    
    if action == 'activate':
        self_improver.activate_kill_switch(reason)
        return jsonify({"success": True, "message": "Kill switch activated"})
    elif action == 'deactivate':
        self_improver.deactivate_kill_switch()
        return jsonify({"success": True, "message": "Kill switch deactivated"})
    else:
        return jsonify({"error": "Invalid action"}), 400


@app.route('/api/admin/learning-stats', methods=['GET'])
def learning_stats():
    """İstatistikler"""
    stats = learning_engine.get_learning_stats()
    return jsonify(stats)


# ============ TEST API'LERİ ============

@app.route('/api/admin/add-test-data', methods=['POST'])
def add_test_data():
    """Test verisi ekle"""
    data = request.json or {}
    count = data.get('count', 50)
    
    feedback_types = [
        {"rating": 5, "comment": "Harika"},
        {"rating": 4, "comment": "İyi"},
        {"rating": 3, "comment": "İdare eder"},
        {"rating": 2, "comment": "Çok karmaşık"},
        {"rating": 1, "comment": "Yanlış"},
    ]
    
    for i in range(count):
        feedback = random.choice(feedback_types)
        learning_engine.record_feedback(
            conversation_id=1,
            message_id=i,
            feedback_type="test",
            rating=feedback["rating"],
            comment=feedback["comment"]
        )
    
    stats = learning_engine.get_learning_stats()
    return jsonify({
        "success": True,
        "message": f"{count} test feedback eklendi",
        "stats": stats
    })


# ============ YARDIMCI API'LER ============

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Text to Speech"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "Metin boş"}), 400
    
    try:
        filename = f"static/audio/{uuid.uuid4()}.mp3"
        tts = gTTS(text=text, lang='tr')
        tts.save(filename)
        return jsonify({"audio_url": f"/{filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Dosya yükle"""
    if 'file' not in request.files:
        return jsonify({"error": "Dosya yok"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Dosya seçilmedi"}), 400
    
    if '.' not in file.filename:
        return jsonify({"error": "Geçersiz dosya"}), 400
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in Settings.ALLOWED_EXTENSIONS:
        return jsonify({"error": "Desteklenmeyen dosya türü"}), 400
    
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(Settings.UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"content": content, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": f"Dosya okunamadı: {str(e)}"}), 400


# ============ UYGULAMA BAŞLATMA ============

if __name__ == '__main__':
    if not check_settings():
        exit(1)
    
    # Mevcut provider'ları listele
    available = []
    if Settings.GROQ_API_KEY:
        available.append("Groq")
    if Settings.OPENAI_API_KEY:
        available.append("OpenAI")
    if Settings.ANTHROPIC_API_KEY:
        available.append("Anthropic/Claude")
    if Settings.GOOGLE_API_KEY:
        available.append("Google/Gemini")
    if Settings.COHERE_API_KEY:
        available.append("Cohere")
    
    # Web Search durumu
    search_status = "ENABLED ✅" if Settings.SEARCH_ENABLED and Settings.TAVILY_API_KEY else "DISABLED ❌"
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║   🚀 Nova AI - Full Stack + Binance + AI PREDICTION + 🗑️      ║
╚═══════════════════════════════════════════════════════════════╝

🌐 Ana sayfa: http://localhost:{Settings.FLASK_PORT}
🎛️  Admin Panel: http://localhost:{Settings.FLASK_PORT}/admin
🎨 Artifact Test: http://localhost:{Settings.FLASK_PORT}/artifact-test

🤖 Provider: {Settings.DEFAULT_PROVIDER.upper()}
📡 Model: {Settings.DEFAULT_MODELS.get(Settings.DEFAULT_PROVIDER, 'N/A')}

🧠 Self-Improvement: ENABLED (Safe Mode)
🎨 Artifact System: ENABLED
🔍 Web Search: {search_status}
📊 Binance WebSocket: READY (25+ Coin)
📈 Chart System: ENABLED (TradingView)
🤖 AI Prediction: ENABLED (Technical Analysis)
💬 Market Analysis: ENABLED (Piyasa yorumlama aktif)
🗑️  Delete All: ENABLED (Tümünü sil butonu aktif!)
🟢 Kill Switch: {"ACTIVE" if self_improver.is_kill_switch_active() else "Inactive"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ YENİ ÖZELLİKLER:
   • Kullanıcı kripto hakkında soru sorduğunda otomatik piyasa analizi
   • Teknik gösterge yorumlama (RSI, MACD, MA, Bollinger Bands)
   • Risk değerlendirmesi ve uyarılar
   • Profesyonel ve tarafsız piyasa yorumları
   • Emoji kullanımı minimize edildi (daha profesyonel ton)
   • 🗑️ TÜMÜNÜ SİL BUTONU - Sidebar'da aktif!
   • ✅ STREAMING DÜZELTİLDİ - Kelime birleşmeleri giderildi!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛑 Durdurmak için: CTRL+C
""")
    
    # Socket.IO test eventi
    @socketio.on('connect')
    def handle_connect():
        print('✅ Client bağlandı!')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('❌ Client ayrıldı!')
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=Settings.FLASK_PORT,
        debug=False,
        allow_unsafe_werkzeug=True
    )