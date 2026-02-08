"""
GELİŞTİRİLMİŞ YATIRIM TAHMİN MOTORU 🤖📈
Binance verilerinden AI destekli gelişmiş tahminler üretir
"""

import numpy as np
from collections import deque
from datetime import datetime, timedelta
import statistics
from typing import Dict, List, Optional, Tuple

class AdvancedPredictionEngine:
    def __init__(self, history_size: int = 200):
        self.price_data = {}  # Her coin için fiyat geçmişi
        self.volume_data = {}  # Hacim verileri
        self.predictions = {}  # Aktif tahminler
        self.prediction_history = {}  # Tahmin geçmişi (başarı oranı için)
        self.history_size = history_size
        self.alert_thresholds = {
            'volatility': 0.1,
            'rapid_decline': -5,
            'rapid_increase': 5,
            'rsi_overbought': 75,
            'rsi_oversold': 25
        }
        
    def add_price_data(self, symbol: str, price: float, volume: float = 0, timestamp: datetime = None):
        """Fiyat ve hacim verisi ekle"""
        if timestamp is None:
            timestamp = datetime.now()
            
        if symbol not in self.price_data:
            self.price_data[symbol] = deque(maxlen=self.history_size)
            self.volume_data[symbol] = deque(maxlen=self.history_size)
        
        self.price_data[symbol].append({
            'price': float(price),
            'timestamp': timestamp
        })
        
        self.volume_data[symbol].append({
            'volume': float(volume),
            'timestamp': timestamp
        })
    
    def calculate_advanced_indicators(self, symbol: str) -> Optional[Dict]:
        """Gelişmiş teknik göstergeleri hesapla"""
        if symbol not in self.price_data or len(self.price_data[symbol]) < 20:
            return None
        
        prices = [d['price'] for d in self.price_data[symbol]]
        volumes = [d['volume'] for d in self.volume_data[symbol]] if symbol in self.volume_data else [0] * len(prices)
        
        current_price = prices[-1]
        
        # Değişim yüzdeleri (farklı zaman dilimleri)
        changes = {
            '1m': self._calculate_change(prices, -2),
            '5m': self._calculate_change(prices, -6),
            '15m': self._calculate_change(prices, -16),
            '30m': self._calculate_change(prices, -31),
            '1h': self._calculate_change(prices, -61),
        }
        
        # Hareketli ortalamalar
        ma_5 = self._moving_average(prices, 5)
        ma_10 = self._moving_average(prices, 10)
        ma_20 = self._moving_average(prices, 20)
        ma_50 = self._moving_average(prices, 50)
        
        # EMA (Exponential Moving Average)
        ema_12 = self._exponential_moving_average(prices, 12)
        ema_26 = self._exponential_moving_average(prices, 26)
        
        # MACD
        macd_line = ema_12 - ema_26
        macd_signal = self._exponential_moving_average([macd_line] * 9, 9)
        macd_histogram = macd_line - macd_signal
        
        # RSI
        rsi = self._calculate_rsi(prices, period=14)
        
        # Stochastic RSI
        stoch_rsi = self._calculate_stochastic_rsi(prices)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(prices)
        bb_position = ((current_price - bb_lower) / (bb_upper - bb_lower)) * 100 if bb_upper != bb_lower else 50
        
        # Volatilite (ATR - Average True Range)
        atr = self._calculate_atr(prices)
        volatility_percent = (atr / current_price) * 100
        
        # Hacim analizi
        volume_ma = statistics.mean(volumes[-20:]) if len(volumes) >= 20 else sum(volumes) / len(volumes) if volumes else 0
        volume_ratio = (volumes[-1] / volume_ma) if volume_ma > 0 else 1
        
        # Trend gücü (ADX benzeri)
        trend_strength = self._calculate_trend_strength(prices)
        
        # Momentum göstergeleri
        momentum = self._calculate_momentum(prices, 10)
        roc = self._calculate_rate_of_change(prices, 10)
        
        # Destek/Direnç seviyeleri (pivot points)
        support_levels, resistance_levels = self._calculate_support_resistance(prices)
        
        # Trend belirleme (geliştirilmiş)
        trend = self._determine_trend(ma_5, ma_10, ma_20, ma_50, prices)
        
        # Fibonacci seviyeleri
        fib_levels = self._calculate_fibonacci_levels(prices)
        
        return {
            'current_price': current_price,
            'changes': changes,
            'ma': {'5': ma_5, '10': ma_10, '20': ma_20, '50': ma_50},
            'ema': {'12': ema_12, '26': ema_26},
            'macd': {
                'line': round(macd_line, 4),
                'signal': round(macd_signal, 4),
                'histogram': round(macd_histogram, 4)
            },
            'rsi': round(rsi, 2),
            'stoch_rsi': round(stoch_rsi, 2),
            'bollinger_bands': {
                'upper': round(bb_upper, 2),
                'middle': round(bb_middle, 2),
                'lower': round(bb_lower, 2),
                'position': round(bb_position, 2)
            },
            'atr': round(atr, 4),
            'volatility_percent': round(volatility_percent, 2),
            'volume_ratio': round(volume_ratio, 2),
            'trend': trend,
            'trend_strength': round(trend_strength, 2),
            'momentum': round(momentum, 4),
            'roc': round(roc, 2),
            'support_levels': [round(s, 2) for s in support_levels],
            'resistance_levels': [round(r, 2) for r in resistance_levels],
            'fibonacci': fib_levels
        }
    
    def _calculate_change(self, prices: List[float], index: int) -> float:
        """Fiyat değişimi hesapla"""
        if len(prices) >= abs(index):
            return ((prices[-1] - prices[index]) / prices[index] * 100)
        return 0
    
    def _moving_average(self, prices: List[float], period: int) -> float:
        """Basit hareketli ortalama"""
        if len(prices) >= period:
            return statistics.mean(prices[-period:])
        return statistics.mean(prices) if prices else 0
    
    def _exponential_moving_average(self, prices: List[float], period: int) -> float:
        """Exponential Moving Average (EMA)"""
        if len(prices) < period:
            return statistics.mean(prices) if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = statistics.mean(prices[:period])
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """RSI hesapla (geliştirilmiş)"""
        if len(prices) < period + 1:
            return 50
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = statistics.mean(gains[-period:])
        avg_loss = statistics.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_stochastic_rsi(self, prices: List[float], period: int = 14) -> float:
        """Stochastic RSI hesapla"""
        if len(prices) < period * 2:
            return 50
        
        rsi_values = []
        for i in range(period, len(prices)):
            rsi = self._calculate_rsi(prices[:i+1], period)
            rsi_values.append(rsi)
        
        if len(rsi_values) < period:
            return 50
        
        recent_rsi = rsi_values[-period:]
        min_rsi = min(recent_rsi)
        max_rsi = max(recent_rsi)
        
        if max_rsi == min_rsi:
            return 50
        
        stoch_rsi = ((rsi_values[-1] - min_rsi) / (max_rsi - min_rsi)) * 100
        return stoch_rsi
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Tuple[float, float, float]:
        """Bollinger Bands hesapla"""
        if len(prices) < period:
            avg = statistics.mean(prices)
            return avg, avg, avg
        
        recent_prices = prices[-period:]
        middle = statistics.mean(recent_prices)
        std = statistics.stdev(recent_prices)
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        return upper, middle, lower
    
    def _calculate_atr(self, prices: List[float], period: int = 14) -> float:
        """Average True Range (ATR) hesapla"""
        if len(prices) < period + 1:
            return statistics.stdev(prices) if len(prices) > 1 else 0
        
        true_ranges = []
        for i in range(1, len(prices)):
            high_low = abs(prices[i] - prices[i-1])
            true_ranges.append(high_low)
        
        return statistics.mean(true_ranges[-period:])
    
    def _calculate_trend_strength(self, prices: List[float], period: int = 14) -> float:
        """Trend gücü hesapla (ADX benzeri basitleştirilmiş)"""
        if len(prices) < period + 1:
            return 50
        
        positive_moves = 0
        negative_moves = 0
        
        for i in range(-period, -1):
            change = prices[i] - prices[i-1]
            if change > 0:
                positive_moves += abs(change)
            else:
                negative_moves += abs(change)
        
        total_movement = positive_moves + negative_moves
        if total_movement == 0:
            return 50
        
        directional_strength = abs(positive_moves - negative_moves) / total_movement * 100
        return directional_strength
    
    def _calculate_momentum(self, prices: List[float], period: int = 10) -> float:
        """Momentum hesapla"""
        if len(prices) <= period:
            return 0
        return prices[-1] - prices[-period-1]
    
    def _calculate_rate_of_change(self, prices: List[float], period: int = 10) -> float:
        """Rate of Change (ROC) hesapla"""
        if len(prices) <= period:
            return 0
        return ((prices[-1] - prices[-period-1]) / prices[-period-1]) * 100
    
    def _calculate_support_resistance(self, prices: List[float]) -> Tuple[List[float], List[float]]:
        """Destek ve direnç seviyelerini hesapla"""
        if len(prices) < 20:
            return [min(prices)], [max(prices)]
        
        recent_prices = prices[-50:] if len(prices) >= 50 else prices
        
        # Local min/max bul
        support_levels = []
        resistance_levels = []
        
        for i in range(2, len(recent_prices) - 2):
            # Local minimum (destek)
            if recent_prices[i] < recent_prices[i-1] and recent_prices[i] < recent_prices[i+1]:
                if recent_prices[i] < recent_prices[i-2] and recent_prices[i] < recent_prices[i+2]:
                    support_levels.append(recent_prices[i])
            
            # Local maximum (direnç)
            if recent_prices[i] > recent_prices[i-1] and recent_prices[i] > recent_prices[i+1]:
                if recent_prices[i] > recent_prices[i-2] and recent_prices[i] > recent_prices[i+2]:
                    resistance_levels.append(recent_prices[i])
        
        # En yakın 3 seviyeyi al
        current_price = prices[-1]
        support_levels = sorted([s for s in support_levels if s < current_price])[-3:] if support_levels else [min(recent_prices)]
        resistance_levels = sorted([r for r in resistance_levels if r > current_price])[:3] if resistance_levels else [max(recent_prices)]
        
        return support_levels, resistance_levels
    
    def _determine_trend(self, ma_5: float, ma_10: float, ma_20: float, ma_50: float, prices: List[float]) -> str:
        """Geliştirilmiş trend belirleme"""
        current_price = prices[-1]
        
        # Güçlü yükseliş
        if ma_5 > ma_10 > ma_20 > ma_50 and current_price > ma_5:
            return "GÜÇLÜ YÜKSELİŞ 🚀"
        # Orta yükseliş
        elif ma_5 > ma_10 > ma_20:
            return "YÜKSELİŞ 📈"
        # Zayıf yükseliş
        elif ma_5 > ma_10:
            return "HAFIF YÜKSELİŞ ↗️"
        # Güçlü düşüş
        elif ma_5 < ma_10 < ma_20 < ma_50 and current_price < ma_5:
            return "GÜÇLÜ DÜŞÜŞ 📉"
        # Orta düşüş
        elif ma_5 < ma_10 < ma_20:
            return "DÜŞÜŞ ↘️"
        # Zayıf düşüş
        elif ma_5 < ma_10:
            return "HAFIF DÜŞÜŞ ↘️"
        else:
            return "YATAY ↔️"
    
    def _calculate_fibonacci_levels(self, prices: List[float]) -> Dict[str, float]:
        """Fibonacci retracement seviyeleri"""
        if len(prices) < 20:
            return {}
        
        recent_prices = prices[-50:] if len(prices) >= 50 else prices
        high = max(recent_prices)
        low = min(recent_prices)
        diff = high - low
        
        return {
            '0%': round(high, 2),
            '23.6%': round(high - diff * 0.236, 2),
            '38.2%': round(high - diff * 0.382, 2),
            '50%': round(high - diff * 0.5, 2),
            '61.8%': round(high - diff * 0.618, 2),
            '100%': round(low, 2)
        }
    
    def generate_advanced_prediction(self, symbol: str) -> Dict:
        """Gelişmiş AI destekli tahmin üret"""
        indicators = self.calculate_advanced_indicators(symbol)
        
        if not indicators:
            return {
                'symbol': symbol,
                'status': 'insufficient_data',
                'message': '⏳ Yeterli veri bekleniyor... (minimum 20 veri noktası gerekli)',
                'confidence': 0
            }
        
        # Sinyal puanlama sistemi
        signals = []
        scores = []
        weights = []  # Her sinyale ağırlık
        
        # 1. RSI Analizi (Ağırlık: 1.2)
        rsi_score, rsi_signal = self._analyze_rsi(indicators['rsi'], indicators['stoch_rsi'])
        scores.append(rsi_score)
        weights.append(1.2)
        signals.append(rsi_signal)
        
        # 2. MACD Analizi (Ağırlık: 1.5)
        macd_score, macd_signal = self._analyze_macd(indicators['macd'])
        scores.append(macd_score)
        weights.append(1.5)
        signals.append(macd_signal)
        
        # 3. Trend Analizi (Ağırlık: 1.3)
        trend_score, trend_signal = self._analyze_trend(indicators['trend'], indicators['trend_strength'])
        scores.append(trend_score)
        weights.append(1.3)
        signals.append(trend_signal)
        
        # 4. MA Cross Analizi (Ağırlık: 1.0)
        ma_score, ma_signal = self._analyze_moving_averages(indicators['ma'], indicators['current_price'])
        scores.append(ma_score)
        weights.append(1.0)
        signals.append(ma_signal)
        
        # 5. Bollinger Bands (Ağırlık: 1.1)
        bb_score, bb_signal = self._analyze_bollinger_bands(indicators['bollinger_bands'], indicators['current_price'])
        scores.append(bb_score)
        weights.append(1.1)
        signals.append(bb_signal)
        
        # 6. Momentum ve ROC (Ağırlık: 0.9)
        momentum_score, momentum_signal = self._analyze_momentum(indicators['momentum'], indicators['roc'])
        scores.append(momentum_score)
        weights.append(0.9)
        signals.append(momentum_signal)
        
        # 7. Volume Analizi (Ağırlık: 0.8)
        volume_score, volume_signal = self._analyze_volume(indicators['volume_ratio'])
        scores.append(volume_score)
        weights.append(0.8)
        signals.append(volume_signal)
        
        # 8. Support/Resistance (Ağırlık: 1.0)
        sr_score, sr_signal = self._analyze_support_resistance(
            indicators['current_price'],
            indicators['support_levels'],
            indicators['resistance_levels']
        )
        scores.append(sr_score)
        weights.append(1.0)
        signals.append(sr_signal)
        
        # Ağırlıklı skor hesapla
        weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        confidence = min(abs(weighted_score) * 15 + 50, 95)  # 50-95 arası
        
        # Risk skoru hesapla
        risk_score = self._calculate_risk_score(indicators)
        
        # Karar ver
        decision = self._make_decision(weighted_score, confidence, risk_score)
        
        # Hedef fiyatlar (daha akıllı)
        targets = self._calculate_smart_targets(indicators, decision['action_type'])
        
        return {
            'symbol': symbol,
            'action': decision['action'],
            'action_type': decision['action_type'],
            'recommendation': decision['recommendation'],
            'confidence': round(confidence, 1),
            'risk_score': round(risk_score, 1),
            'color': decision['color'],
            'emoji': decision['emoji'],
            'explanation': decision['explanation'],
            'signals': signals,
            'indicators': indicators,
            'targets': targets,
            'weighted_score': round(weighted_score, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_rsi(self, rsi: float, stoch_rsi: float) -> Tuple[float, str]:
        """RSI analizi"""
        if rsi < 25:
            return 1.5, f"🟢 RSI çok düşük ({rsi:.1f}) - Güçlü AL sinyali"
        elif rsi < 35:
            return 1.0, f"🟢 RSI aşırı satım yakın ({rsi:.1f}) - AL sinyali"
        elif rsi > 75:
            return -1.5, f"🔴 RSI çok yüksek ({rsi:.1f}) - Güçlü SAT sinyali"
        elif rsi > 65:
            return -1.0, f"🔴 RSI aşırı alım yakın ({rsi:.1f}) - SAT sinyali"
        elif rsi > 50:
            return 0.3, f"🟡 RSI pozitif bölgede ({rsi:.1f})"
        else:
            return -0.3, f"🟡 RSI negatif bölgede ({rsi:.1f})"
    
    def _analyze_macd(self, macd: Dict) -> Tuple[float, str]:
        """MACD analizi"""
        histogram = macd['histogram']
        
        if histogram > 0 and macd['line'] > macd['signal']:
            return 1.2, f"🟢 MACD pozitif kesişim (Histogram: {histogram:.4f})"
        elif histogram < 0 and macd['line'] < macd['signal']:
            return -1.2, f"🔴 MACD negatif kesişim (Histogram: {histogram:.4f})"
        elif histogram > 0:
            return 0.5, f"🟡 MACD pozitif momentumda"
        else:
            return -0.5, f"🟡 MACD negatif momentumda"
    
    def _analyze_trend(self, trend: str, strength: float) -> Tuple[float, str]:
        """Trend analizi"""
        if "GÜÇLÜ YÜKSELİŞ" in trend:
            return 1.5, f"🚀 {trend} - Güç: {strength:.1f}"
        elif "YÜKSELİŞ" in trend:
            return 1.0, f"📈 {trend} - Güç: {strength:.1f}"
        elif "GÜÇLÜ DÜŞÜŞ" in trend:
            return -1.5, f"📉 {trend} - Güç: {strength:.1f}"
        elif "DÜŞÜŞ" in trend:
            return -1.0, f"↘️ {trend} - Güç: {strength:.1f}"
        else:
            return 0, f"↔️ {trend}"
    
    def _analyze_moving_averages(self, ma: Dict, current_price: float) -> Tuple[float, str]:
        """Hareketli ortalama analizi"""
        if current_price > ma['5'] > ma['10'] > ma['20']:
            return 1.0, "✅ Tüm MA'lar yukarı yönlü dizilimde"
        elif current_price < ma['5'] < ma['10'] < ma['20']:
            return -1.0, "❌ Tüm MA'lar aşağı yönlü dizilimde"
        elif current_price > ma['5'] > ma['10']:
            return 0.5, "🟡 Kısa vadeli MA'lar pozitif"
        elif current_price < ma['5'] < ma['10']:
            return -0.5, "🟡 Kısa vadeli MA'lar negatif"
        else:
            return 0, "⚠️ Karışık MA sinyalleri"
    
    def _analyze_bollinger_bands(self, bb: Dict, current_price: float) -> Tuple[float, str]:
        """Bollinger Bands analizi"""
        position = bb['position']
        
        if position < 20:
            return 1.0, f"🟢 Alt Bollinger Band yakınında (%{position:.1f}) - AL bölgesi"
        elif position > 80:
            return -1.0, f"🔴 Üst Bollinger Band yakınında (%{position:.1f}) - SAT bölgesi"
        elif position > 60:
            return -0.3, f"🟡 BB üst bölgesinde (%{position:.1f})"
        elif position < 40:
            return 0.3, f"🟡 BB alt bölgesinde (%{position:.1f})"
        else:
            return 0, f"↔️ BB ortasında (%{position:.1f})"
    
    def _analyze_momentum(self, momentum: float, roc: float) -> Tuple[float, str]:
        """Momentum analizi"""
        if roc > 3:
            return 1.0, f"🚀 Güçlü pozitif momentum (ROC: {roc:.2f}%)"
        elif roc < -3:
            return -1.0, f"⚠️ Güçlü negatif momentum (ROC: {roc:.2f}%)"
        elif roc > 1:
            return 0.5, f"📊 Pozitif momentum (ROC: {roc:.2f}%)"
        elif roc < -1:
            return -0.5, f"📊 Negatif momentum (ROC: {roc:.2f}%)"
        else:
            return 0, f"↔️ Nötr momentum (ROC: {roc:.2f}%)"
    
    def _analyze_volume(self, volume_ratio: float) -> Tuple[float, str]:
        """Hacim analizi"""
        if volume_ratio > 2.0:
            return 0.7, f"📊 Çok yüksek hacim (x{volume_ratio:.1f}) - Güçlü hareket"
        elif volume_ratio > 1.5:
            return 0.5, f"📊 Yüksek hacim (x{volume_ratio:.1f})"
        elif volume_ratio < 0.5:
            return -0.3, f"⚠️ Düşük hacim (x{volume_ratio:.1f}) - Zayıf hareket"
        else:
            return 0, f"📊 Normal hacim (x{volume_ratio:.1f})"
    
    def _analyze_support_resistance(self, price: float, supports: List[float], resistances: List[float]) -> Tuple[float, str]:
        """Destek/Direnç analizi"""
        if not supports or not resistances:
            return 0, "📍 Destek/Direnç hesaplanıyor..."
        
        nearest_support = max(supports) if supports else price * 0.95
        nearest_resistance = min(resistances) if resistances else price * 1.05
        
        distance_to_support = ((price - nearest_support) / price) * 100
        distance_to_resistance = ((nearest_resistance - price) / price) * 100
        
        if distance_to_support < 1:
            return 1.0, f"💪 Güçlü destek seviyesinde (${nearest_support:.2f})"
        elif distance_to_support < 2:
            return 0.5, f"📍 Destek yakınında (${nearest_support:.2f})"
        elif distance_to_resistance < 1:
            return -1.0, f"⚠️ Güçlü direnç seviyesinde (${nearest_resistance:.2f})"
        elif distance_to_resistance < 2:
            return -0.5, f"📍 Direnç yakınında (${nearest_resistance:.2f})"
        else:
            return 0, f"📍 Destek: ${nearest_support:.2f} | Direnç: ${nearest_resistance:.2f}"
    
    def _calculate_risk_score(self, indicators: Dict) -> float:
        """Risk skoru hesapla (0-100, yüksek = riskli)"""
        risk_factors = []
        
        # Volatilite riski
        volatility_risk = min(indicators['volatility_percent'] * 10, 30)
        risk_factors.append(volatility_risk)
        
        # Trend belirsizliği
        if "YATAY" in indicators['trend']:
            risk_factors.append(20)
        elif "HAFIF" in indicators['trend']:
            risk_factors.append(10)
        
        # Aşırı alım/satım riski
        rsi = indicators['rsi']
        if rsi > 70 or rsi < 30:
            risk_factors.append(15)
        
        # Bollinger Band pozisyonu
        bb_pos = indicators['bollinger_bands']['position']
        if bb_pos > 80 or bb_pos < 20:
            risk_factors.append(10)
        
        return min(sum(risk_factors), 100)
    
    def _make_decision(self, weighted_score: float, confidence: float, risk_score: float) -> Dict:
        """Nihai karar ver"""
        if weighted_score >= 0.8 and risk_score < 60:
            return {
                'action': "GÜÇLÜ AL 🟢🟢",
                'action_type': 'BUY',
                'recommendation': "Güçlü AL sinyali - Pozisyon açılabilir",
                'color': 'success',
                'emoji': '🚀',
                'explanation': 'Tüm göstergeler güçlü yükseliş işaret ediyor!'
            }
        elif weighted_score >= 0.4:
            return {
                'action': "AL 🟢",
                'action_type': 'BUY',
                'recommendation': "AL sinyali - Küçük pozisyon düşünülebilir",
                'color': 'success',
                'emoji': '📈',
                'explanation': 'Göstergeler yükseliş tarafında, ancak dikkatli ol.'
            }
        elif weighted_score <= -0.8 and risk_score < 60:
            return {
                'action': "GÜÇLÜ SAT 🔴🔴",
                'action_type': 'SELL',
                'recommendation': "Güçlü SAT sinyali - Pozisyon kapat/kısalt",
                'color': 'danger',
                'emoji': '📉',
                'explanation': 'Güçlü düşüş sinyalleri mevcut!'
            }
        elif weighted_score <= -0.4:
            return {
                'action': "SAT 🔴",
                'action_type': 'SELL',
                'recommendation': "SAT sinyali - Dikkatli ol",
                'color': 'danger',
                'emoji': '⚠️',
                'explanation': 'Düşüş riskleri artıyor.'
            }
        else:
            return {
                'action': "BEKLE 🟡",
                'action_type': 'HOLD',
                'recommendation': "BEKLEMEYİ DÜŞÜN - Net sinyal yok",
                'color': 'warning',
                'emoji': '⏳',
                'explanation': 'Karışık sinyaller, daha net fırsat bekle.'
            }
    
    def _calculate_smart_targets(self, indicators: Dict, action_type: str) -> Dict:
        """Akıllı hedef fiyatlar hesapla"""
        current = indicators['current_price']
        atr = indicators['atr']
        volatility = indicators['volatility_percent']
        
        # ATR bazlı hedefler (daha gerçekçi)
        if action_type == 'BUY':
            # Yükseliş hedefleri
            target_1 = current + (atr * 1.5)  # Konservatif
            target_2 = current + (atr * 2.5)  # Orta
            target_3 = current + (atr * 4)    # Agresif
            stop_loss = current - (atr * 2)   # Stop loss
            
            risk_reward = ((target_1 - current) / (current - stop_loss)) if (current - stop_loss) > 0 else 0
            
        elif action_type == 'SELL':
            # Düşüş hedefleri
            target_1 = current - (atr * 1.5)
            target_2 = current - (atr * 2.5)
            target_3 = current - (atr * 4)
            stop_loss = current + (atr * 2)
            
            risk_reward = ((current - target_1) / (stop_loss - current)) if (stop_loss - current) > 0 else 0
            
        else:  # HOLD
            # Mevcut seviyeler
            support = indicators['support_levels'][-1] if indicators['support_levels'] else current * 0.97
            resistance = indicators['resistance_levels'][0] if indicators['resistance_levels'] else current * 1.03
            target_1 = resistance
            target_2 = resistance * 1.02
            target_3 = resistance * 1.05
            stop_loss = support
            risk_reward = 0
        
        return {
            'current': round(current, 6),
            'target_1': round(target_1, 6),
            'target_2': round(target_2, 6),
            'target_3': round(target_3, 6),
            'stop_loss': round(stop_loss, 6),
            'risk_reward_ratio': round(risk_reward, 2),
            'atr': round(atr, 6)
        }
    
    def get_top_opportunities(self, min_confidence: float = 65, top_n: int = 5) -> List[Dict]:
        """En iyi fırsatları listele"""
        opportunities = []
        
        for symbol in self.price_data.keys():
            prediction = self.generate_advanced_prediction(symbol)
            
            if (prediction.get('confidence', 0) >= min_confidence and 
                prediction.get('action_type') == 'BUY' and
                prediction.get('risk_score', 100) < 70):
                opportunities.append(prediction)
        
        # Güven skoruna göre sırala
        opportunities.sort(key=lambda x: (x['confidence'], -x['risk_score']), reverse=True)
        
        return opportunities[:top_n]
    
    def get_risk_alerts(self) -> List[Dict]:
        """Gelişmiş risk uyarıları"""
        alerts = []
        
        for symbol in self.price_data.keys():
            indicators = self.calculate_advanced_indicators(symbol)
            if not indicators:
                continue
            
            # Aşırı volatilite
            if indicators['volatility_percent'] > self.alert_thresholds['volatility'] * 100:
                alerts.append({
                    'symbol': symbol,
                    'type': 'HIGH_VOLATILITY',
                    'message': f"⚠️ {symbol} çok yüksek volatilitede! (%{indicators['volatility_percent']:.2f})",
                    'severity': 'warning',
                    'value': indicators['volatility_percent']
                })
            
            # Hızlı düşüş
            if indicators['changes']['5m'] < self.alert_thresholds['rapid_decline']:
                alerts.append({
                    'symbol': symbol,
                    'type': 'RAPID_DECLINE',
                    'message': f"🚨 {symbol} hızlı düşüşte! ({indicators['changes']['5m']:.2f}%)",
                    'severity': 'danger',
                    'value': indicators['changes']['5m']
                })
            
            # Hızlı yükseliş
            if indicators['changes']['5m'] > self.alert_thresholds['rapid_increase']:
                alerts.append({
                    'symbol': symbol,
                    'type': 'RAPID_INCREASE',
                    'message': f"🚀 {symbol} hızlı yükselişte! (+{indicators['changes']['5m']:.2f}%)",
                    'severity': 'info',
                    'value': indicators['changes']['5m']
                })
            
            # Aşırı alım
            if indicators['rsi'] > self.alert_thresholds['rsi_overbought']:
                alerts.append({
                    'symbol': symbol,
                    'type': 'OVERBOUGHT',
                    'message': f"📊 {symbol} aşırı alım bölgesinde! (RSI: {indicators['rsi']:.1f})",
                    'severity': 'warning',
                    'value': indicators['rsi']
                })
            
            # Aşırı satım
            if indicators['rsi'] < self.alert_thresholds['rsi_oversold']:
                alerts.append({
                    'symbol': symbol,
                    'type': 'OVERSOLD',
                    'message': f"💰 {symbol} aşırı satım bölgesinde! (RSI: {indicators['rsi']:.1f})",
                    'severity': 'success',
                    'value': indicators['rsi']
                })
            
            # MACD kesişim
            macd = indicators['macd']
            if abs(macd['histogram']) < 0.0001 and macd['line'] > 0:
                alerts.append({
                    'symbol': symbol,
                    'type': 'MACD_BULLISH_CROSS',
                    'message': f"✅ {symbol} MACD yükseliş kesişimi yakın!",
                    'severity': 'success',
                    'value': macd['histogram']
                })
            
            # Destek kırılımı
            if indicators['support_levels']:
                nearest_support = max(indicators['support_levels'])
                distance = ((indicators['current_price'] - nearest_support) / indicators['current_price']) * 100
                if distance < 1:
                    alerts.append({
                        'symbol': symbol,
                        'type': 'NEAR_SUPPORT',
                        'message': f"💪 {symbol} destek seviyesinde! (${nearest_support:.2f})",
                        'severity': 'info',
                        'value': nearest_support
                    })
            
            # Direnç yakınında
            if indicators['resistance_levels']:
                nearest_resistance = min(indicators['resistance_levels'])
                distance = ((nearest_resistance - indicators['current_price']) / indicators['current_price']) * 100
                if distance < 1:
                    alerts.append({
                        'symbol': symbol,
                        'type': 'NEAR_RESISTANCE',
                        'message': f"⚠️ {symbol} direnç seviyesinde! (${nearest_resistance:.2f})",
                        'severity': 'warning',
                        'value': nearest_resistance
                    })
        
        # Önem sırasına göre sırala
        severity_order = {'danger': 0, 'warning': 1, 'info': 2, 'success': 3}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        return alerts
    
    def generate_market_summary(self) -> Optional[Dict]:
        """Gelişmiş piyasa özeti"""
        if not self.price_data:
            return None
        
        total_coins = len(self.price_data)
        strong_rising = 0
        rising = 0
        falling = 0
        strong_falling = 0
        neutral = 0
        
        total_volume_change = 0
        volume_count = 0
        
        avg_rsi = []
        high_volatility_count = 0
        
        for symbol in self.price_data.keys():
            indicators = self.calculate_advanced_indicators(symbol)
            if not indicators:
                continue
            
            change_5m = indicators['changes']['5m']
            
            # Trend kategorileri
            if change_5m > 3:
                strong_rising += 1
            elif change_5m > 1:
                rising += 1
            elif change_5m < -3:
                strong_falling += 1
            elif change_5m < -1:
                falling += 1
            else:
                neutral += 1
            
            # RSI ortalaması
            avg_rsi.append(indicators['rsi'])
            
            # Volatilite
            if indicators['volatility_percent'] > 5:
                high_volatility_count += 1
            
            # Hacim
            if indicators['volume_ratio'] > 0:
                total_volume_change += indicators['volume_ratio']
                volume_count += 1
        
        # Piyasa duygusu hesapla
        bullish_score = strong_rising * 2 + rising
        bearish_score = strong_falling * 2 + falling
        
        if bullish_score > bearish_score * 1.5:
            sentiment = "ÇOK POZİTİF 🟢🟢"
            sentiment_emoji = "🚀"
            sentiment_score = 85
        elif bullish_score > bearish_score:
            sentiment = "POZİTİF 🟢"
            sentiment_emoji = "📈"
            sentiment_score = 65
        elif bearish_score > bullish_score * 1.5:
            sentiment = "ÇOK NEGATİF 🔴🔴"
            sentiment_emoji = "📉"
            sentiment_score = 15
        elif bearish_score > bullish_score:
            sentiment = "NEGATİF 🔴"
            sentiment_emoji = "↘️"
            sentiment_score = 35
        else:
            sentiment = "NÖTR 🟡"
            sentiment_emoji = "↔️"
            sentiment_score = 50
        
        market_rsi = statistics.mean(avg_rsi) if avg_rsi else 50
        avg_volume_ratio = total_volume_change / volume_count if volume_count > 0 else 1
        
        # Piyasa fazı
        if market_rsi > 65 and sentiment_score > 70:
            market_phase = "AŞIRI ALIM - DİKKATLİ"
        elif market_rsi < 35 and sentiment_score < 30:
            market_phase = "AŞIRI SATIM - FIRSAT"
        elif sentiment_score > 60:
            market_phase = "YÜKSELİŞ TRENDI"
        elif sentiment_score < 40:
            market_phase = "DÜŞÜŞ TRENDI"
        else:
            market_phase = "KONSOLIDASYON"
        
        return {
            'total_coins': total_coins,
            'strong_rising': strong_rising,
            'rising': rising,
            'neutral': neutral,
            'falling': falling,
            'strong_falling': strong_falling,
            'sentiment': sentiment,
            'sentiment_emoji': sentiment_emoji,
            'sentiment_score': sentiment_score,
            'market_phase': market_phase,
            'market_rsi': round(market_rsi, 1),
            'avg_volume_ratio': round(avg_volume_ratio, 2),
            'high_volatility_count': high_volatility_count,
            'volatility_percentage': round((high_volatility_count / total_coins * 100), 1) if total_coins > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_symbol_statistics(self, symbol: str) -> Optional[Dict]:
        """Coin için detaylı istatistikler"""
        if symbol not in self.price_data or len(self.price_data[symbol]) < 20:
            return None
        
        prices = [d['price'] for d in self.price_data[symbol]]
        
        return {
            'symbol': symbol,
            'data_points': len(prices),
            'price_range': {
                'min': round(min(prices), 6),
                'max': round(max(prices), 6),
                'range': round(max(prices) - min(prices), 6)
            },
            'average_price': round(statistics.mean(prices), 6),
            'median_price': round(statistics.median(prices), 6),
            'std_deviation': round(statistics.stdev(prices), 6),
            'coefficient_of_variation': round((statistics.stdev(prices) / statistics.mean(prices)) * 100, 2),
            'price_trend': 'UP' if prices[-1] > prices[0] else 'DOWN',
            'total_change_percent': round(((prices[-1] - prices[0]) / prices[0]) * 100, 2)
        }
    
    def backtest_prediction(self, symbol: str, prediction: Dict, actual_outcome: str) -> None:
        """Tahmin başarısını kaydet (gelecekte accuracy hesaplamak için)"""
        if symbol not in self.prediction_history:
            self.prediction_history[symbol] = []
        
        self.prediction_history[symbol].append({
            'prediction': prediction,
            'actual_outcome': actual_outcome,
            'timestamp': datetime.now().isoformat()
        })
        
        # Son 100 tahmini tut
        if len(self.prediction_history[symbol]) > 100:
            self.prediction_history[symbol] = self.prediction_history[symbol][-100:]
    
    def get_prediction_accuracy(self, symbol: str = None) -> Dict:
        """Tahmin doğruluk oranını hesapla"""
        if symbol:
            history = self.prediction_history.get(symbol, [])
        else:
            history = [item for sublist in self.prediction_history.values() for item in sublist]
        
        if not history:
            return {
                'total_predictions': 0,
                'accuracy': 0,
                'message': 'Henüz tahmin geçmişi yok'
            }
        
        correct = sum(1 for h in history if h['prediction']['action_type'] == h['actual_outcome'])
        total = len(history)
        accuracy = (correct / total) * 100
        
        return {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy': round(accuracy, 2),
            'symbol': symbol
        }
    
    def export_analysis(self, symbol: str) -> Optional[Dict]:
        """Tam analiz raporu (JSON export için)"""
        prediction = self.generate_advanced_prediction(symbol)
        statistics = self.get_symbol_statistics(symbol)
        
        if not prediction or prediction.get('status') == 'insufficient_data':
            return None
        
        return {
            'report_date': datetime.now().isoformat(),
            'symbol': symbol,
            'prediction': prediction,
            'statistics': statistics,
            'market_summary': self.generate_market_summary()
        }