from strategies.base_strategy import BaseStrategy

class TrendFollowingStrategy(BaseStrategy):
    def __init__(self, short_window=20, long_window=50, risk_manager=None):
        # Üst sınıfın (BaseStrategy) genlerini ve risk_manager'ı alıyoruz
        super().__init__(risk_manager)
        self.short_window = short_window
        self.long_window = long_window
        
        # Stratejinin o anki durumu bilmesi için değişkenler
        self.position_open = False 
        self.entry_price = 0.0

    def prepare_indicators(self, data):
        print(f"[*] İndikatörler Hesaplanıyor (SMA {self.short_window} / SMA {self.long_window})...")
        
        # Pandas ile Kısa (20) ve Uzun (50) Günlük Basit Hareketli Ortalamaları (SMA) hesapla
        data['SMA_Short'] = data['Close'].rolling(window=self.short_window).mean()
        data['SMA_Long'] = data['Close'].rolling(window=self.long_window).mean()
        
        self.data = data # Geriye dönük kontrol için veriyi hafızaya al

    def generate_signal(self, current_index, current_row):
        # Yeterli gün geçmediyse (örn: ilk 50 gün) işlem yapma
        if current_index < self.long_window:
            return 'HOLD', 0.0

        # Kesişimi bulmak için dünün verisine de ihtiyacımız var
        prev_row = self.data.iloc[current_index - 1]
        
        # --- RİSK YÖNETİMİ (Kırmızı Çizgimiz) ---
        # Eğer elimizde hisse varsa ve güncel fiyat stop-loss sınırını vurduysa, acil satış yap!
        if self.position_open and self.risk_manager:
            if self.risk_manager.check_stop_loss(self.entry_price, current_row['Close']):
                self.position_open = False
                return 'SELL', 1.0 # Elimdeki tüm hisseleri (%100) sat (Zarar Kes)

        # --- ALIM SİNYALİ (Golden Cross) ---
        # Dün kısa uzunun altındayken, bugün üstüne çıktıysa (Yukarı Kesti)
        if prev_row['SMA_Short'] <= prev_row['SMA_Long'] and current_row['SMA_Short'] > current_row['SMA_Long']:
            if not self.position_open: # Zaten içeride değilsek al
                self.position_open = True
                self.entry_price = current_row['Close']
                return 'BUY', 1.0 # Paramın %100'ü ile al
        
        # --- SATIŞ SİNYALİ (Death Cross) ---
        # Dün kısa uzunun üstündeyken, bugün altına indiyse (Aşağı Kesti)
        elif prev_row['SMA_Short'] >= prev_row['SMA_Long'] and current_row['SMA_Short'] < current_row['SMA_Long']:
            if self.position_open: # İçerideysek satıp çık
                self.position_open = False
                return 'SELL', 1.0 # Elimdeki hisselerin %100'ünü sat

        return 'HOLD', 0.0