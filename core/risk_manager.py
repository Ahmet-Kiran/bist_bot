class RiskManager:
    def __init__(self, max_drawdown_limit=0.20, stop_loss_pct=0.05):
        """
        Risk Yöneticisi sınıfı, portföyün aşırı erimesini (drawdown) ve tek bir pozisyondaki zararı sınırlamak için kurallar belirler.
        Parametreler:
        max_drawdown_limit: 0.20 (%20) -> Portföy toplam değeri tarihi zirvesinden %20 aşağı düşerse alarm ver.
        stop_loss_pct: 0.05 (%5) -> Alınan bir hisse, alış fiyatından %5 aşağı düşerse zararı kes (Stop-Loss).
        """
        self.max_drawdown_limit = max_drawdown_limit
        self.stop_loss_pct = stop_loss_pct
        self.peak_portfolio_value = 0.0  # Portföyün gördüğü en yüksek değer (Zirve)

    def check_drawdown(self, current_portfolio_value):
        """
        Her gün portföy değerini kontrol edip güncel Drawdown (erime) oranını hesaplar.
        """
        # Eğer portföy yeni bir zirve yaptıysa, zirveyi güncelle
        if current_portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_portfolio_value
            
        # Zirveden ne kadar düştüğümüzü (Drawdown) hesapla
        if self.peak_portfolio_value == 0:
            return False, 0.0
            
        drawdown = (self.peak_portfolio_value - current_portfolio_value) / self.peak_portfolio_value
        
        # Eğer erime limiti aştıysa Tehlike Sinyali (True) gönder
        is_limit_breached = drawdown >= self.max_drawdown_limit
        
        return is_limit_breached, drawdown

    def check_stop_loss(self, entry_price, current_price):
        """
        Alınan hissenin güncel fiyatı, stop-loss sınırımızı ihlal etti mi kontrol eder.
        """
        if entry_price == 0:
            return False
            
        loss_pct = (entry_price - current_price) / entry_price
        
        # Zarar yüzdesi, belirlediğimiz limiti aştıysa Satış Sinyali (True) gönder
        if loss_pct >= self.stop_loss_pct:
            return True 
            
        return False