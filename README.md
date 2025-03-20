# ChargeME Analyzer

Eine interaktive Streamlit-Anwendung zur Analyse und Visualisierung von Elektrofahrzeug-Ladedaten im ChargeME-Format.

![ChargeME Analyzer Dashboard](https://via.placeholder.com/800x450.png?text=ChargeME+Analyzer+Dashboard)

## Features

- **Umfassende Verbrauchsanalyse:** Visualisierung und Berechnung des Stromverbrauchs und der Kosten
- **Zeitliche Auswertung:** Monatliche, tägliche und stündliche Analysen der Ladedaten
- **Standortbezogene Auswertung:** Identifikation der meistgenutzten Ladestationen
- **Kostenübersicht:** Berechnung aller Kosten basierend auf dem konfigurierbaren kWh-Preis (Standard: 0,49 €/kWh)
- **Ladeeffizienz-Analyse:** Auswertung der durchschnittlichen Ladeleistung und -geschwindigkeit
- **Export-Funktionen:** Download von gefilterten Daten und Auswertungen im CSV-Format

## Voraussetzungen

- Python 3.7 oder höher
- Pip (Python Package Manager)

## Installation

1. Klone das Repository:
   ```bash
   git clone https://github.com/dkd-dobberkauå/chargeme-analyzer.git
   cd chargeme-analyzer
   ```

2. Installiere die erforderlichen Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```

## Verwendung

1. Starte die Streamlit-App:
   ```bash
   streamlit run app.py
   ```

2. Die App wird im Browser geöffnet (standardmäßig unter http://localhost:8501).

3. Stelle sicher, dass die `ChargeMEtransactions.csv`-Datei im gleichen Verzeichnis wie die App-Datei liegt oder nutze die Datei-Upload-Funktion.

## Datenformat

Die App erwartet eine CSV-Datei im ChargeME-Format mit folgenden wichtigen Spalten:
- `Ladevorgangs-ID`: Eindeutige ID des Ladevorgangs
- `Gestartet`: Startzeit des Ladevorgangs
- `Beendet`: Endzeit des Ladevorgangs
- `meterValueStart (kWh)`: Zählerstand zu Beginn
- `meterValueStop (kWh)`: Zählerstand am Ende
- `Ladepunkt-ID`: ID des Ladepunkts
- `Standort`: Bezeichnung der Ladestation
- `Ladedauer (in Minuten)`: Dauer des Ladevorgangs
- `Verbrauch (kWh)`: Verbrauchte Energiemenge

Das CSV verwendet Semikolons (`;`) als Trennzeichen und Kommas (`,`) als Dezimaltrennzeichen.

## Projektstruktur

```
chargeme-analyzer/
├── app.py                  # Hauptanwendungsdatei
├── requirements.txt        # Abhängigkeiten
├── README.md               # Dokumentation
└── .gitignore              # Git-Ignorierungsdatei
```

## Anpassungen

### Strompreis ändern

Für einen anderen Strompreis als 0,49 €/kWh ändere die folgende Zeile in `app.py`:

```python
# Ändere den Strompreis (€/kWh)
cost_per_kwh = 0.49  # Hier deinen eigenen Wert einfügen
```

### Eigene Farbschemen

Die Farbschemen für Diagramme können in den entsprechenden Plotly-Funktionen angepasst werden:

```python
# Beispiel zur Änderung des Farbschemas
fig = px.bar(
    data_frame, 
    x='x_values', 
    y='y_values',
    color_continuous_scale='Viridis'  # Andere Optionen: 'Blues', 'Reds', etc.
)
```

## Fehlerbehebung

### Dateipfad-Probleme

Wenn die App die CSV-Datei nicht finden kann:

1. Überprüfe, ob die Datei im gleichen Verzeichnis wie `app.py` liegt
2. Nutze einen absoluten Pfad in der `load_data`-Funktion:
   ```python
   df = pd.read_csv('/vollständiger/pfad/zu/ChargeMEtransactions.csv', delimiter=';', decimal=',')
   ```

### Encoding-Probleme

Bei Problemen mit Sonderzeichen:

```python
df = pd.read_csv('ChargeMEtransactions.csv', delimiter=';', decimal=',', encoding='utf-8-sig')
```

## Beitragen

Beiträge sind willkommen! Bitte folge diesen Schritten:

1. Forke das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Pushe zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE)-Datei für Details.

## Kontakt

Projekt-Link: [https://github.com/dkd-dobberkau/chargeme-analyzer](https://github.com/dein-username/chargeme-analyzer)

## Danksagung

- [Streamlit](https://streamlit.io/) - Für das fantastische Web-App-Framework
- [Plotly](https://plotly.com/) - Für die interaktiven Visualisierungen
- [Pandas](https://pandas.pydata.org/) - Für die Datenverarbeitung