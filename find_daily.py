import pandas as pd
import os

def find_daily_sales(file_newer, file_older):
    # Extrahiere das Datum aus den Dateinamen
    date_new = os.path.splitext(os.path.basename(file_newer))[0].split("_")[1]
    date_old = os.path.splitext(os.path.basename(file_older))[0].split("_")[1]

    # Lese die CSV-Dateien ein
    df_new = pd.read_csv(file_newer)
    df_old = pd.read_csv(file_older)

    # Arbeite nur mit ISBN und TOTAL SALES (Gesamtverkäufe)
    df_new_subset = df_new[['ISBN', 'TOTAL SALES']].copy()
    df_old_subset = df_old[['ISBN', 'TOTAL SALES']].copy()

    # Verbinde die beiden Dateien anhand der ISBN (für Verkaufsdifferenz)
    df_result = pd.merge(df_new_subset, df_old_subset, on='ISBN', suffixes=('_new', '_old'))

    # Berechne die Differenz der Verkäufe zwischen den beiden Tagen
    df_result[date_old] = df_result['TOTAL SALES_new'] - df_result['TOTAL SALES_old']

    # Wähle nur die benötigten Spalten aus
    df_output = df_result[['ISBN', date_old]]

    # Speichere die Tagesverkäufe in eine neue CSV-Datei
    output_file = f"daily_sales_{date_old}.csv"
    df_output.to_csv(output_file, index=False)

    print(f"✅ Tagesverkaufsdatei wurde erstellt: {output_file}")
    return df_output

# Beispielhafte Nutzung:
find_daily_sales("./book_sales_files/g1_20250409.csv", "./book_sales_files/g1_20250408.csv")

