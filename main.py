import pandas as pd
from core.data_handler import BISTDataHandler
from core.backtest_engine import BacktestEngine
from core.risk_manager import RiskManager
from strategies.trend_following import TrendFollowingStrategy
from core.visualizer import Visualizer
from core.inflation_handler import InflationHandler

def main():
    inflation_handler_obj = InflationHandler(api_key="3rqExAJgJg")
    inflation_handler_obj.fetch_cpi_data(start_year="2015", end_year="2024")
    # 2015 başından 2024 başına kümülatif enflasyonu hesapla
    cum_inflation = inflation_handler_obj.get_inflation_rate("2015-01-01", "2024-01-01")
    print(f"\n[*] 9 Yıllık Toplam Gerçek Enflasyon: %{cum_inflation*100:.2f}\n")
    # ---------------------------

    print("🚀 BIST_Bot Başlatılıyor...\n")
    
    tickers = ["THYAO", "TUPRS", "KCHOL", "PGSUS", "BIMAS","LOGO","HEKTS","TCELL","AKBNK","YKBNK"]
    start_date = "2015-01-01"
    end_date = "2024-01-01"
    
    data_handler = BISTDataHandler(tickers=tickers, start_date=start_date, end_date=end_date)
    print("[*] Veriler kontrol ediliyor...\n")
    data_handler.fetch_and_save_data()

    results = []

    for ticker in tickers:
        try:
            df = data_handler.load_data(ticker)
            
            # Terminalde bu hissenin işlemlerinin başlayacağını belirten ayırıcı bir başlık
            print("-" * 80)
            print(f"[*] {ticker} İŞLEMLERİ BAŞLIYOR (2015-2024)")
            print("-" * 80)
            
            risk_manager = RiskManager(max_drawdown_limit=0.20, stop_loss_pct=0.05)
            strategy = TrendFollowingStrategy(short_window=20, long_window=50 ,risk_manager=risk_manager)
            
            # Motoru hisse ismi (ticker) ile başlatıyoruz
            engine = BacktestEngine(data=df, ticker=ticker, initial_balance=100.0, commission_rate=0.002, verbose=True, inflation_handler=inflation_handler_obj)
            
            trade_history, portfolio_history, final_value = engine.run(strategy)

            print(f"[*] {ticker} grafiği hazırlanıyor...")
            Visualizer.plot_results(ticker, df, trade_history)
            nominal_kar_yuzde = ((final_value - 100.0) / 100.0) * 100
            reel_kar_yuzde = (((1 + (nominal_kar_yuzde / 100.0)) / (1 + cum_inflation)) - 1.0) * 100
            
            results.append({
                "Hisse": ticker,
                "İşlem Sayısı": len(trade_history),
                "Bitiş (TL)": round(final_value, 2),
                "Enflasyon (%)": round(cum_inflation * 100, 2), # O dönemin toplam enflasyonu
                "Nominal Kâr (%)": round(nominal_kar_yuzde, 2),
                "Reel Kâr (%)": round(reel_kar_yuzde, 2)
            })
            
        except Exception as e:
            print(f"[!] {ticker} test edilirken hata oluştu: {e}")

    # Karnemizi basalım
    print("\n\n🎯 --- ÇOKLU HİSSE TEST SONUÇLARI (2015 - 2024) ---")
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by= "Reel Kâr (%)" , ascending=False).reset_index(drop=True)
    
    print(results_df.to_string())
    print("-" * 55)

if __name__ == "__main__":
    main()