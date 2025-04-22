import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind
import os

# Pfad zur CSV-Datei (anpassen, falls nötig)
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed/Load_history.csv'))

# Schritt 1: Violinplot erstellen
# # --- 1. Daten einlesen ---
df = pd.read_csv(csv_path, parse_dates=['timestamp'])

#%%
# --- 2. Nur eine Zone auswählen ---
zone_id = 1  # hier Eure gewünschte Zone
zone = df[df['zone_id'] == zone_id].copy()

# --- 3. Wochentag extrahieren und auf Deutsch mappen ---
zone['weekday_num'] = zone['timestamp'].dt.dayofweek  # Montag=0 … Sonntag=6
weekday_map = {
    0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 
    3: 'Donnerstag', 4: 'Freitag', 5: 'Samstag', 6: 'Sonntag'
}
zone['Tag'] = zone['weekday_num'].map(weekday_map)

# --- 4. Reihenfolge der Achsenkategorien festlegen ---
order = ['Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag','Sonntag']

# --- 5. Palette definieren: Werktage blau, Sa/So orange ---
palette = {day: ('orange' if day in ['Samstag','Sonntag'] else 'blue') 
           for day in order}

# --- 6. Violin-Plot mit seaborn ---
plt.figure(figsize=(12,6))
sns.violinplot(
    x='Tag', 
    y='value', 
    data=zone, 
    order=order, 
    palette=palette,
    inner='quartile',   # zeigt Median & Quartile
    scale='width'       # gleiche Breite aller Violinen
)
plt.title(f'Netzlast-Verteilung nach Wochentag – Zone {zone_id}')
plt.xlabel('Wochentag')
plt.ylabel('Netzlast (MW)')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


#%%
# --- Feiertags‑Daten einlesen ---
csv_path2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed/holiday_list.csv'))
holidays = pd.read_csv(csv_path2, parse_dates=['date'])
holiday_dates = set(holidays['date'].dt.date)

# --- Für Schritt 2: Zone-DataFrame (aus Schritt 1) nutzen ---
# zone enthält bereits eure Spalten 'timestamp', 'value' und 'Tag' ohne Feiertags-Markierung

# Datum extrahieren
zone['date_only'] = zone['timestamp'].dt.date

# Zwei Gruppen definieren:
# 1) Werktage (Mo–Fr): dayofweek 0–4 und NICHT Feiertag
weekday_mask = zone['timestamp'].dt.dayofweek.isin(range(0,5)) & ~zone['date_only'].isin(holiday_dates)
weekday_load = zone.loc[weekday_mask, 'value']

# 2) Sonn‑/Feiertage: entweder Sa/So (dayofweek 5–6) ODER in holiday_dates
weekend_holiday_mask = zone['timestamp'].dt.dayofweek.isin([5,6]) | zone['date_only'].isin(holiday_dates)
weekend_holiday_load = zone.loc[weekend_holiday_mask, 'value']


##Clean up 
# --- 1) Diagnose: NaNs & Varianz prüfen ---
n_nan_wd = weekday_load.isna().sum()
n_nan_we = weekend_holiday_load.isna().sum()
print(f"NaNs Werktage:   {n_nan_wd}")
print(f"NaNs Wochenend: {n_nan_we}")

# Beschreibende Statistik
print("Werktage describe():")
print(weekday_load.describe(), "\n")
print("Wochenend/Feiertag describe():")
print(weekend_holiday_load.describe(), "\n")

# Varianzen
print(f"Var Werktage:   {weekday_load.var():.3f}")
print(f"Var Wochenend: {weekend_holiday_load.var():.3f}\n")

# --- 2) Cleanup: NaNs rauswerfen ---
weekday_clean = weekday_load.dropna()
weekend_clean = weekend_holiday_load.dropna()



t_statistic, p_value = ttest_ind(
    weekday_clean,
    weekend_clean,
    equal_var=False
)

print(f"Anzahl Werktags‑Stichproben: {len(weekday_load)}")
print(f"Anzahl Sonn-/Feiertags‑Stichproben: {len(weekend_holiday_load)}")
print(f"t‑Statistik: {t_statistic:.3f}")
print(f"p‑Wert: {p_value:.3f}")

# Entscheidung bei alpha = 0.05
alpha = 0.05
if p_value < alpha:
    print("H₀ wird verworfen: Signifikanter Unterschied der Mittelwerte.")
else:
    print("H₀ kann nicht verworfen werden: Kein signifikanter Unterschied.")