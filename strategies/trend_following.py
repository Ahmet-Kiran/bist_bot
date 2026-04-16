import pandas_ta as ta
from strategies.base_strategy import BaseStrategy

class TrendFollowingStrategy(BaseStrategy):
    def __init__(self, short_window=20, long_window=50, risk_manager=None):
        super().__init__(risk_manager)
        self.short_window = short_window
        self.long_window = long_window
        
        # Strateji Hafızası
        self.position_open = False 
        self.entry_price = 0.0
        self.dynamic_stop_loss = 0.0 # ATR tabanlı hareketli stop kalkanımız

    def prepare_indicators(self, data):
        print("[*] Trend Takibi İndikatörleri Yüklendi...")
        
        # 1. Yön: EMA (Hareketli Ortalamalar)
        data['EMA_Short'] = ta.ema(data['Close'], length=self.short_window)
        data['EMA_Long'] = ta.ema(data['Close'], length=self.long_window)
        
        # 2. Güç: ADX (Piyasada trend var mı?)
        adx_df = ta.adx(data['High'], data['Low'], data['Close'], length=14)
        data['ADX'] = adx_df['ADX_14']
        
        # 3. İvme: MACD (Momentum Histogramı)
        macd_df = ta.macd(data['Close'], fast=12, slow=26, signal=9)
        data['MACD_Hist'] = macd_df['MACDh_12_26_9']
        
        # 4. Volatilite/Risk: ATR (Günlük oynaklık)
        data['ATR'] = ta.atr(data['High'], data['Low'], data['Close'], length=14)
        
        # 5. Hacim: SMA_Volume
        data['SMA_Volume'] = ta.sma(data['Volume'], length=20)
        
        self.data = data

    def generate_signal(self, current_index, current_row):
        # Yeterli veri birikene kadar (En uzun periyot 50) motoru beklet
        if current_index < self.long_window:
            return 'HOLD', 0.0

        prev_row = self.data.iloc[current_index - 1]
        
        # --- ATR İLE AKILLI STOP-LOSS KONTROLÜ ---
        if self.position_open:
            # Fiyat, ATR kalkanımızı aşağı kırarsa hemen sat!
            if current_row['Close'] < self.dynamic_stop_loss:
                self.position_open = False
                return 'SELL', 1.0 # Acil Çıkış (%100 Sat)

        # --- ALIM ŞARTLARI ---
        # 1. Yön kesişimi yukarı mı?
        ema_cross_up = prev_row['EMA_Short'] <= prev_row['EMA_Long'] and current_row['EMA_Short'] > current_row['EMA_Long']
        
        # 2. Trend gücü (ESNETİLDİ: 25 yerine 20'yi geçmesi yeterli)
        adx_strong = current_row['ADX'] > 20
        
        # 3. Momentum pozitif mi? (Aynı kaldı)
        macd_positive = current_row['MACD_Hist'] > 0
        
        # 4. Kurumsal hacim var mı? (ESNETİLDİ: 1.5 katı yerine sadece ortalamanın üstü olması yeterli)
        volume_high = current_row['Volume'] > current_row['SMA_Volume']

        # Tüm şartlar sağlandıysa tetiğe bas!
        if ema_cross_up and adx_strong and macd_positive and volume_high:
            if not self.position_open:
                self.position_open = True
                self.entry_price = current_row['Close']
                self.dynamic_stop_loss = self.entry_price - (current_row['ATR'] * 2)
                return 'BUY', 1.0
        
        # --- SATIŞ ŞARTLARI (Trendin Bitişi) ---
        # Yön aşağı kestiyse VEYA ADX 20'nin altına inip "Trend Öldü" dediyse kârı al ve çık
        ema_cross_down = prev_row['EMA_Short'] >= prev_row['EMA_Long'] and current_row['EMA_Short'] < current_row['EMA_Long']
        trend_dead = current_row['ADX'] < 20

        if self.position_open and (ema_cross_down or trend_dead):
            self.position_open = False
            return 'SELL', 1.0

        return 'HOLD', 0.0

        