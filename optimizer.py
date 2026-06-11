import os
import pandas as pd
from core.data_handler import BISTDataHandler
from core.backtest_engine import BacktestEngine
from core.risk_manager import RiskManager
from strategies.trend_following import TrendFollowingStrategy

def run_optimization():
    print("🚀 BIST Algoritmik Optimizasyon Başlatılıyor...\n")
    
    # 1. Klasör Kontrolü (results klasörü yoksa oluştur)
    os.makedirs('results', exist_ok=True)
    
    # 2. Test Edilecek Hisseler ve EMA Kombinasyonları
    tickers = ["THYAO", "TUPRS", "KCHOL", "PGSUS", "BIMAS","LOGO","HEKTS","TCELL","AKBNK","YKBNK"]
    
    # (Kısa EMA, Uzun EMA) Çiftleri
    ema_pairs = [
        (10, 20),  # Çok Hızlı (Agresif)
        (15, 30),  # Orta Hızlı
        (20, 50),  # Klasik (Bizim kullandığımız)
        (50, 100)  # Çok Yavaş (Ağır trendler için)
    ]
    
    data_handler = BISTDataHandler(tickers=tickers, start_date="2015-01-01", end_date="2024-01-01")
    data_handler.fetch_and_save_data()

    all_results = []
    
    print(f"[*] {len(tickers)} Hisse ve {len(ema_pairs)} farklı strateji kombinasyonu test ediliyor...")
    print("⏳ Bu işlem birkaç saniye sürebilir, arka planda binlerce al-sat yapılıyor...\n")

    # 3. Dev Tarama Döngüsü
    for ticker in tickers:
        df = data_handler.load_data(ticker)
        
        for short_ema, long_ema in ema_pairs:
            try:
                risk_manager = RiskManager(max_drawdown_limit=0.30, stop_loss_pct=0.15)
                # Stratejiyi döngüdeki EMA'lar ile başlat
                strategy = TrendFollowingStrategy(short_window=short_ema, long_window=long_ema, risk_manager=risk_manager)
                
                # ÇOK ÖNEMLİ: verbose=False olmalı ki terminal loglarla çökmesin!
                engine = BacktestEngine(data=df, ticker=ticker, initial_balance=100.0, commission_rate=0.002, verbose=False)
                
                trade_history, _, final_value = engine.run(strategy)
                profit_pct = ((final_value - 100.0) / 100.0) * 100
                
                all_results.append({
                    "Hisse": ticker,
                    "Kısa_EMA": short_ema,
                    "Uzun_EMA": long_ema,
                    "İşlem_Sayısı": len(trade_history),
                    "Bitiş_Bakiyesi(TL)": round(final_value, 2),
                    "Net_Kar(%)": round(profit_pct, 2)
                })
            except Exception as e:
                print(f"[!] {ticker} ({short_ema}/{long_ema}) testinde hata: {e}")

    # 4. Sonuçları Tabloya Çevir ve Kaydet
    
    # GÜVENLİK DUVARI: Eğer liste boşsa, programı çökertme, uyarı ver!
    if not all_results:
        print("\n[!] DİKKAT: Hiçbir test başarılı olamadı. Tablo boş!")
        print("Lütfen yukarıdaki kırmızı/uyarı loglarına bakarak asıl hatanın ne olduğunu tespit et.")
        return

    results_df = pd.DataFrame(all_results)
    
    # Sonuçları önce Hisseye, sonra Kâr oranına göre (büyükten küçüğe) sırala
    results_df = results_df.sort_values(by=["Hisse", "Net_Kar(%)"], ascending=[True, False])
    
    # results klasörüne kaydet
    file_path = os.path.join("results", "ema_optimization_results.csv")
    results_df.to_csv(file_path, index=False, encoding='utf-8')
    
    print(f"✅ Optimizasyon Tamamlandı! En iyi sonuçlar '{file_path}' dosyasına kaydedildi.")
    print("\nİşte Tablonun Kısa Bir Özeti (En iyi kombinasyonlar):")
    # Her hissenin sadece en iyi sonucunu (ilk satırını) ekrana bass
    best_results = results_df.groupby("Hisse").head(1)
    print(best_results.to_string(index=False))

if __name__ == "__main__":
    run_optimization()