import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class HybridStrategy(BaseStrategy):
    def __init__(self, rsi_period=14, oversold_threshold=55, overbought_threshold=75, trailing_stop_pct=0.10, ema_period=50, risk_manager=None):
        super().__init__(risk_manager)
        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold # YENİ: Tepe noktası avcısı
        self.trailing_stop_pct = trailing_stop_pct
        self.ema_period = ema_period
        
        self.position_open = False
        self.highest_price = 0.0

    def prepare_indicators(self, data):
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        avg_gain = gain.ewm(alpha=1/self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.rsi_period, adjust=False).mean()
        
        rs = avg_gain / avg_loss.replace(0, np.nan)
        data['RSI'] = 100 - (100 / (1 + rs)) 
        
        data['EMA_50'] = data['Close'].ewm(span=self.ema_period, adjust=False).mean()
        
        self.data = data 
        return data

    def generate_signal(self, current_index, current_row):
        if current_index < self.ema_period:
            return 'HOLD', 0.0
            
        try:
            rsi_degeri = current_row.RSI if hasattr(current_row, 'RSI') else current_row['RSI']
            fiyat = current_row.Close if hasattr(current_row, 'Close') else current_row['Close']
            ema_50 = current_row.EMA_50 if hasattr(current_row, 'EMA_50') else current_row['EMA_50']
        except:
            return 'HOLD', 0.0

        if pd.isna(rsi_degeri) or pd.isna(fiyat) or pd.isna(ema_50):
            return 'HOLD', 0.0
            
        # --- 1. DURUM: EĞER İÇERİDEYSEK (POZİSYON AÇIKSA) ---
        if self.position_open:
            if fiyat > self.highest_price:
                self.highest_price = fiyat
            
            # YENİ KURAL (TEPE AVCISI): Fiyat şiştiyse ve RSI 75'i geçtiyse beklemeden SAT!
            if rsi_degeri >= self.overbought_threshold:
                self.position_open = False
                self.highest_price = 0.0
                return 'SELL', 1.0

            # ESKİ KURAL (GÜVENLİK AĞI): Eğer RSI 75'e vurmadan trend dönerse, zirveden %10 düşünce SAT!
            stop_seviyesi = self.highest_price * (1.0 - self.trailing_stop_pct)
            if fiyat <= stop_seviyesi:
                self.position_open = False
                self.highest_price = 0.0
                return 'SELL', 1.0
                
            return 'HOLD', 0.0

        # --- 2. DURUM: EĞER DIŞARIDAYSAK (NAKİTTEYSEK) ---
        else:
            # Trend yukarıyken (Fiyat > EMA 50) ve ufak bir düzeltme geldiğinde (RSI <= 55) AL!
            if rsi_degeri <= self.oversold_threshold and fiyat > ema_50:
                self.position_open = True
                self.highest_price = fiyat
                return 'BUY', 1.0
            else:
                return 'HOLD', 0.0