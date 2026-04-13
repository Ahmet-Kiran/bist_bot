class BaseStrategy:
    def __init__(self, risk_manager=None):
        """
        Tüm stratejilerin ortak özelliklerini barındıran temel sınıf.
        risk_manager: Adım 4'te yazdığımız, kasayı koruyan kalkanımız.
        """
        self.risk_manager = risk_manager

    def prepare_indicators(self, data):
        """
        RSI, MACD, Hareketli Ortalamalar gibi verilerin hesaplandığı yer.
        Her strateji bu metodu kendi formülüne göre ezecek (override edecek).
        """
        raise NotImplementedError("Bu metod alt sınıfta doldurulmalıdır!")

    def generate_signal(self, current_index, current_row):
        """
        Simülasyon her gün çalıştığında Al/Sat kararı üreten metod.
        Çıktı Formatı: ('BUY' veya 'SELL' veya 'HOLD', İşlem_Miktarı_Oranı)
        """
        raise NotImplementedError("Bu metod alt sınıfta doldurulmalıdır!")