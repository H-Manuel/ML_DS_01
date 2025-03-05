import pandas as pd
import os


#%%
# CSV-Datei einlesen
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/raw/Load_history.csv'))
df = pd.read_csv(file_path)
print(df)
#%%
df_melted = df.melt(id_vars=[ "year", "month", "day","zone_id"], var_name="hour", value_name="value")

# Die Stunde aus "h1", "h2", ..., "h24" extrahieren
df_melted["hour"] = df_melted["hour"].str.extract("(\d+)").astype(int) - 1  # -1 für 0-23 Stundenformat

# Timestamp erstellen
df_melted["timestamp"] = pd.to_datetime(df_melted[["year", "month", "day"]]) + pd.to_timedelta(df_melted["hour"], unit="h")

# Sortierung: zuerst nach Stunde, dann nach Datum
df_melted = df_melted.sort_values(by=["timestamp"]).drop(columns=["year", "month", "day", "hour"])

# Spaltenreihenfolge anpassen (Timestamp zuerst)
df_melted = df_melted[[ "timestamp","zone_id", "value" ]]

# 'value' als float casten
df_melted["value"] = df_melted["value"].str.replace(',', '.').astype(float)

# Ergebnis ausgeben
print(df_melted)
#%%
df_melted.to_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed/Load_history.csv')), index=False)