import evds
import pandas as pd

class InflationHandler:
    def __init__(self, api_key):
        # Merkez Bankası sistemine bağlanıyoruz
        self.api = evds.evdsAPI(api_key)
        self.cpi_data = None

    def fetch_cpi_data(self, start_year="2010", end_year="2024"):
        print("[*] TCMB EVDS'den Tüketici Fiyat Endeksi (TÜFE) verileri çekiliyor...")
        # TP.FG.J0 -> Merkez Bankası sistemindeki TÜFE endeksinin kodudur
        df = self.api.get_data(['TP.FG.J0'], startdate=f"01-01-{start_year}", enddate=f"31-12-{end_year}")
        
        # Gelen veriyi tarih (Yıl-Ay) formatında indeksliyoruz
        df['Tarih'] = pd.to_datetime(df['Tarih'], format='%Y-%m').dt.to_period('M')
        df.set_index('Tarih', inplace=True)
        
        # 'TP_FG_J0' sütun adını daha anlaşılır yapalım
        self.cpi_data = df['TP_FG_J0']
        print("[+] Enflasyon verisi TCMB'den başarıyla indirildi!")

    def get_inflation_rate(self, start_date, end_date):
        """İki tarih arasındaki gerçek enflasyon (paranın erime) oranını hesaplar"""
        if self.cpi_data is None:
            return 0.0
        
        # Günlük tarihleri SADECE Yıl ve Ay'a yuvarlıyoruz (Çünkü TÜFE aylık açıklanır)
        start_period = pd.to_datetime(start_date).to_period('M')
        end_period = pd.to_datetime(end_date).to_period('M')
        
        try:
            cpi_start = self.cpi_data.loc[start_period]
            cpi_end = self.cpi_data.loc[end_period]
            # (Son Endeks / İlk Endeks) - 1 formülü bize yüzde değişimi verir
            return (cpi_end / cpi_start) - 1.0
        except Exception:
            return 0.0 # Veri bulunamazsa  0 döndür