import pandas as pd
import os

def find_daily_sales(file_newer, file_older):
    # Tarihleri çıkar
    date_new = os.path.splitext(os.path.basename(file_newer))[0].split("_")[1]
    date_old = os.path.splitext(os.path.basename(file_older))[0].split("_")[1]

    # Dosyaları oku
    df_new = pd.read_csv(file_newer)
    df_old = pd.read_csv(file_older)

    # Sadece ISBN ve TOTAL SALES ile işlem yap
    df_new_subset = df_new[['ISBN', 'TOTAL SALES']].copy()
    df_old_subset = df_old[['ISBN', 'TOTAL SALES']].copy()

    # ISBN üzerinden birleştir (sadece satış farkı için)
    df_result = pd.merge(df_new_subset, df_old_subset, on='ISBN', suffixes=('_new', '_old'))

    # Günlük satış farkını hesapla
    df_result[date_old] = df_result['TOTAL SALES_new'] - df_result['TOTAL SALES_old']

    # Sadece gerekli sütunlar
    df_output = df_result[['ISBN', date_old]]

    # Yeni CSV’ye yaz
    output_file = f"daily_sales_{date_old}.csv"
    df_output.to_csv(output_file, index=False)

    print(f"✅ Günlük satış dosyası oluşturuldu: {output_file}")
    return df_output

# Örnek kullanım:
find_daily_sales("./book_sales_files/g1_20250409.csv", "./book_sales_files/g1_20250408.csv")
