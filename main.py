from core.data_handler import BISTDataHandler




def main():
    # İzlenecek hisseler listemiz
    tickers = ["THYAO", "TUPRS", "KCHOL", "YEOTK", "ASTOR", "HEKTS", "BIMAS", "TCELL", "AKBNK", "YKBNK"]
    
    # Veri yöneticisini başlatıyoruz (2022'den bugüne örnek bir test)
    handler = BISTDataHandler(
        tickers=tickers, 
        start_date="2022-01-01", 
        end_date="2024-01-01"
    )
    
    # 1. Aşama: Verileri internetten çek ve CSV olarak 'data' klasörüne kaydet
    handler.fetch_and_save_data()
    
    # 2. Aşama: Çektiğimiz verilerden birini test amaçlı okuyalım
    try:
        print("\n[*] Test: THYAO verisi sistemden okunuyor...")
        thyao_df = handler.load_data("THYAO")
        print(thyao_df.head()) # İlk 5 satırı yazdır
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    main()