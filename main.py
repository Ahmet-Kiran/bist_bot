from core.data_handler import BISTDataHandler
from core.backtest_engine import BacktestEngine
from core.risk_manager import RiskManager
from strategies.trend_following import TrendFollowingStrategy

def main():
    print("Trade Bot Başlatılıyor...\n")
    
    # 1. VERİ HAZIRLIĞI
    # Daha önce veriyi indirdiğimiz için fetch_and_save_data() yapmamıza gerek yok.
    data_handler = BISTDataHandler(tickers=["THYAO"], start_date="2010-01-01", end_date="2024-01-01")
    try:
        thyao_data = data_handler.load_data("THYAO")
    except FileNotFoundError:
        print("[!] Veri bulunamadı. Önce indiriliyor...")
        data_handler.fetch_and_save_data()
        thyao_data = data_handler.load_data("THYAO")
    
    # 2. RİSK YÖNETİCİSİ (%20 Drawdown, %5 Stop-Loss)
    risk_manager = RiskManager(max_drawdown_limit=0.20, stop_loss_pct=0.05)
    
    # 3. STRATEJİ (Kısa=20, Uzun=50 Günlük Ortalama)
    # Beynimizi oluştururken risk yöneticimizi de onun içine yerleştiriyoruz.
    strategy = TrendFollowingStrategy(short_window=20, long_window=50, risk_manager=risk_manager)
    
    # 4. SİMÜLASYON MOTORU (100 TL Kasa, Binde 2 Komisyon)
    engine = BacktestEngine(data=thyao_data, initial_balance=100.0, commission_rate=0.002)
    
    # 5. MOTORU ATEŞLE!
    trade_history, portfolio_history = engine.run(strategy)
    
    # İşlem Özeti
    print(f"\n📊 Toplam Yapılan İşlem Sayısı: {len(trade_history)}")

if __name__ == "__main__":
    main()