import pandas as pd
import os

#%%
# CSV-Datei einlesen
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/raw/temperature_history.csv'))
df = pd.read_csv(file_path)
print(df)
#%%
# DataFrame "schmelzen": Spalten h1-h24 in Zeilen transformieren
df_melted = df.melt(id_vars=["station_id", "year", "month", "day"], 
                    var_name="hour", 
                    value_name="value")

# Aus "h1", "h2", ... "h24" die Stunde extrahieren und in 0-23 umwandeln
df_melted["hour"] = df_melted["hour"].str.extract("(\d+)").astype(int) - 1

# Timestamp erstellen: Datum + Stunden-Timedelta
df_melted["timestamp"] = pd.to_datetime(df_melted[["year", "month", "day"]]) + \
                         pd.to_timedelta(df_melted["hour"], unit="h")

# DataFrame sortieren und Hilfsspalten entfernen
df_melted = df_melted.sort_values(by=["timestamp"]).drop(columns=["year", "month", "day", "hour"])

# Spaltenreihenfolge anpassen (Timestamp, station_id, value)
df_melted = df_melted[["timestamp", "station_id", "value"]]

# 'value' als float casten
df_melted["value"] = df_melted["value"].astype(str).str.replace(',', '.').astype(float)

# Ergebnis ausgeben
print(df_melted)
#%%
# Ergebnis in CSV-Datei speichern
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed/temperature_history.csv'))
df_melted.to_csv(output_path, index=False)
