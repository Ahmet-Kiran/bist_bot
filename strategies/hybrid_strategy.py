import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class HybridStrategy(BaseStrategy):
    def __init__(self, rsi_period=14, oversold_threshold=40, trailing_stop_pct=0.08, risk_manager=None):
        super().__init__(risk_manager)
        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.trailing_stop_pct = trailing_stop_pct # Zirveden % kaç düşerse satacağız? (Örn: 0.08 = %8)
        
        # Strateji Hafızası (Durum Takibi)
        self.position_open = False
        self.highest_price = 0.0

    def prepare_indicators(self, data):
        """Sadece RSI hesaplıyoruz, aşırı alım (overbought) sınırlarını çöpe attık."""
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        avg_gain = gain.ewm(alpha=1/self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.rsi_period, adjust=False).mean()
        
        rs = avg_gain / avg_loss.replace(0, np.nan)
        data['RSI'] = 100 - (100 / (1 + rs)) 
        
        self.data = data 
        return data

    def generate_signal(self, current_index, current_row):
        """Motor döngüsü içinde her gün için AL/SAT kararı üretir."""
        if current_index < self.rsi_period:
            return 'HOLD', 0.0
            
        try:
            rsi_degeri = current_row.RSI if hasattr(current_row, 'RSI') else current_row['RSI']
            fiyat = current_row.Close if hasattr(current_row, 'Close') else current_row['Close']
        except:
            return 'HOLD', 0.0

        if pd.isna(rsi_degeri) or pd.isna(fiyat):
            return 'HOLD', 0.0
            
        # --- 1. DURUM: EĞER İÇERİDEYSEK (POZİSYON AÇIKSA) ---
        if self.position_open:
            # Hisse yükseldikçe en yüksek fiyatı (zirveyi) güncelle
            if fiyat > self.highest_price:
                self.highest_price = fiyat
            
            # Dinamik Stop Seviyemizi hesapla (Zirvenin %8 altı)
            stop_seviyesi = self.highest_price * (1.0 - self.trailing_stop_pct)
            
            # Fiyat stop seviyesini aşağı kırdı mı? (Trend bitti mi?)
            if fiyat <= stop_seviyesi:
                self.position_open = False  # Pozisyonu kapat
                self.highest_price = 0.0    # Hafızayı sıfırla
                return 'SELL', 1.0          # Kârı al ve çık!
            else:
                return 'HOLD', 0.0          # Trend devam ediyor, kârı koşturmaya devam et.

        # --- 2. DURUM: EĞER DIŞARIDAYSAK (NAKİTTEYSEK) ---
        else:
            # Sadece RSI aşırı satım bölgesine indiğinde AL
            if rsi_degeri <= self.oversold_threshold:
                self.position_open = True
                self.highest_price = fiyat  # İlk aldığımız gün, en yüksek fiyat maliyetimizdir
                return 'BUY', 1.0
            else:
                return 'HOLD', 0.0