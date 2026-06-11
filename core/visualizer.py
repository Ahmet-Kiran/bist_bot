import matplotlib.pyplot as plt

class Visualizer:
    @staticmethod
    def plot_results(ticker, df, trade_history):
        # 1. Stratejiyi Kokla: Veride RSI var mı?
        has_rsi = 'RSI' in df.columns
        
        # RSI varsa 2 katlı grafik (fiyat + rsi) aç, yoksa tek katlı aç
        fig_rows = 2 if has_rsi else 1
        fig, axes = plt.subplots(fig_rows, 1, figsize=(14, 8 if has_rsi else 6), gridspec_kw={'height_ratios': [3, 1] if has_rsi else [1]})
        
        # Ana fiyat grafiği eksenini belirle
        ax_main = axes[0] if has_rsi else axes
        
        # --- ANA GRAFİK (Fiyat ve Al/Sat Noktaları) ---
        ax_main.plot(df.index, df['Close'], label='Kapanış Fiyatı', color='black', alpha=0.6)
        
        # Eğer Trend Stratejisiyse EMA'ları çiz
        if 'EMA_Short' in df.columns:
            ax_main.plot(df.index, df['EMA_Short'], label='EMA Kısa', color='blue', linestyle='--')
        if 'EMA_Long' in df.columns:
            ax_main.plot(df.index, df['EMA_Long'], label='EMA Uzun', color='orange', linestyle='--')
            
        # İşlem geçmişinden Al/Sat noktalarını ayrıştır ve grafiğe iğnele
        buy_dates, buy_prices, sell_dates, sell_prices = [], [], [], []
        
        for trade in trade_history:
            # Motorun sözlükte hangi kelimeyi kullandığını tahmin edip yakalıyoruz
            action = trade.get('Type') or trade.get('Action') or trade.get('type') or trade.get('action') or trade.get('İşlem')
            date = trade.get('Date') or trade.get('date') or trade.get('Tarih')
            price = trade.get('Price') or trade.get('price') or trade.get('Fiyat')
            
            if action in ['BUY', 'buy', 'AL', 'ALIM']:
                buy_dates.append(date)
                buy_prices.append(price)
            elif action in ['SELL', 'sell', 'SAT', 'SATIM']:
                sell_dates.append(date)
                sell_prices.append(price)
        
        ax_main.scatter(buy_dates, buy_prices, marker='^', color='green', s=120, label='AL', zorder=5)
        ax_main.scatter(sell_dates, sell_prices, marker='v', color='red', s=120, label='SAT', zorder=5)
        
        ax_main.set_title(f"{ticker} - Otomatik Strateji Analizi")
        ax_main.set_ylabel("Fiyat (TL)")
        ax_main.legend()
        ax_main.grid(True, alpha=0.3)
        
        # --- ALT GRAFİK (Eğer Hibrit/RSI Stratejisiyse) ---
        if has_rsi:
            ax_rsi = axes[1]
            ax_rsi.plot(df.index, df['RSI'], label='RSI', color='purple')
            
            # Aşırı Alım / Satım Eşikleri
            ax_rsi.axhline(70, color='red', linestyle='--', alpha=0.5)
            ax_rsi.axhline(30, color='green', linestyle='--', alpha=0.5)
            
            # Hibrit stratejinin esnek sınırları (40-60)
            ax_rsi.axhline(60, color='orange', linestyle=':', alpha=0.5)
            ax_rsi.axhline(40, color='lime', linestyle=':', alpha=0.5)
            
            ax_rsi.set_ylabel("RSI")
            ax_rsi.legend(loc="upper left")
            ax_rsi.grid(True, alpha=0.3)
            
        plt.tight_layout()
        plt.show()