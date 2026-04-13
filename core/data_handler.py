import yfinance as yf
import pandas as pd
import os

#Bu dosya bizim verileri çektiğimiz ve test ettiğimiz dosya olacak.

class BISTDataHandler:
    def __init__(self, tickers, start_date, end_date, data_dir="data"):
        # Yahoo Finance BIST hisseleri için sonuna .IS ister
        self.tickers = [f"{ticker}.IS" if not ticker.endswith(".IS") else ticker for ticker in tickers]
        self.start_date = start_date
        self.end_date = end_date
        self.data_dir = data_dir
        
        # Data klasörünün var olduğundan emin olalım
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_and_save_data(self):
        """Hisse verilerini çeker ve data/ klasörüne CSV olarak kaydeder."""
        print(f"[*] Veriler indiriliyor: {self.start_date} - {self.end_date}")
        
        for ticker in self.tickers:
            print(f"    -> {ticker} verisi çekiliyor...")
            df = yf.download(ticker, start=self.start_date, end=self.end_date, progress=False)
            
            if df.empty:
                print(f"[!] UYARI: {ticker} için veri bulunamadı!")
                continue
            
            # --- YENİ EKLENEN HATA ÇÖZÜMÜ ---
            # yfinance'in yeni sürümüyle gelen çift başlık (MultiIndex) sorununu düzeltiyoruz.
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            # --------------------------------
                
            # '.IS' takısını atıp temiz isimle kaydedelim (Örn: THYAO.csv)
            clean_ticker = ticker.replace('.IS', '')
            file_path = os.path.join(self.data_dir, f"{clean_ticker}.csv")
            
            df.to_csv(file_path)
            print(f"    [+] Başarılı: {file_path} kaydedildi.")
            
    def load_data(self, ticker):
        """Kaydedilen CSV dosyasını okur ve Pandas DataFrame olarak döndürür."""
        file_path = os.path.join(self.data_dir, f"{ticker}.csv")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} bulunamadı. Önce fetch_and_save_data() çalıştırın.")
        
        # Tarih sütununu index (zaman serisi) olarak ayarla
        df = pd.read_csv(file_path, index_col="Date", parse_dates=True)
        return df