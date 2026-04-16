import matplotlib.pyplot as plt
import pandas as pd

class Visualizer:
    @staticmethod
    def plot_results(ticker, df, trade_history):
        # Grafik penceremizi oluşturuyoruz (Ana fiyat + 2 Alt Panel)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
        
        # 1. ANA PANEL: Fiyat ve EMA'lar
        ax1.plot(df.index, df['Close'], label='Fiyat', alpha=0.5)
        ax1.plot(df.index, df['EMA_Short'], label='EMA 20', linestyle='--')
        ax1.plot(df.index, df['EMA_Long'], label='EMA 50', linestyle='--')
        
        # Alım ve Satım Noktalarını İşaretle
        for trade in trade_history:
            color = 'green' if trade['action'] == 'BUY' else 'red'
            marker = '^' if trade['action'] == 'BUY' else 'v'
            ax1.scatter(trade['date'], trade['price'], color=color, marker=marker, s=100, edgecolors='black', zorder=5)

        ax1.set_title(f"{ticker} - Trend Takibi Stratejisi Görsel Raporu")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. ALT PANEL: ADX (Trend Gücü)
        ax2.plot(df.index, df['ADX'], color='purple', label='ADX (Güç)')
        ax2.axhline(25, color='black', linestyle=':', alpha=0.5) # 25 Güç sınırı
        ax2.fill_between(df.index, 25, df['ADX'], where=(df['ADX'] >= 25), color='purple', alpha=0.1)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show() # Grafiği ekrana basar