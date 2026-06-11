import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, rsi_period=14, oversold_threshold=30, overbought_threshold=70, risk_manager=None):
        super().__init__(risk_manager)
        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold

    def prepare_indicators(self, data):
        """1. AŞAMA: Motor çalışmadan önce tüm RSI verilerini orijinal tabloya hesaplar."""
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        avg_gain = gain.ewm(alpha=1/self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.rsi_period, adjust=False).mean()
        
        rs = avg_gain / avg_loss.replace(0, np.nan)
        data['RSI'] = 100 - (100 / (1 + rs)) 
        
        self.data = data 
        return data  # Hata veren kısım düzeltildi: df yerine data döndürüyoruz

    def generate_signal(self, current_index, current_row):
        """2. AŞAMA: Motor döngüsü içinde her gün için AL/SAT kararı üretir."""
        if current_index < self.rsi_period:
            return 'HOLD', 0.0
            
        try:
            rsi_degeri = current_row.RSI if hasattr(current_row, 'RSI') else current_row['RSI']
        except:
            return 'HOLD', 0.0

        if pd.isna(rsi_degeri):
            return 'HOLD', 0.0
            
        if rsi_degeri <= self.oversold_threshold:
            return 'BUY', 1.0
            
        elif rsi_degeri >= self.overbought_threshold:
            return 'SELL', 1.0
            
        else:
            return 'HOLD', 0.0