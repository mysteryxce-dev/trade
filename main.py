import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from flask import Flask, request # Notwendig für Web-Endpunkt

# --- 1. Strategie-Parameter ---
# Hier können Sie Ihre Ticker und Parameter anpassen
ETF_LISTE = ['VUSA.DE', 'SWRD.L', 'VWCE.DE', 'IS3N.DE']
PERFORMANCE_MONATE = 3 
TOP_N = 3

# --- 2. Flask-Anwendung erstellen ---
# Dies muss hier erfolgen, damit Gunicorn (main:app) es findet
app = Flask(__name__) 

# --- 3. Hauptlogik zur Berechnung des Momentums ---
def berechne_momentum_ranking(etf_liste, monate):
    """Führt die Momentum-Berechnung für eine Liste von Tickersymbolen durch."""
    heute = datetime.now().date()
    # Berechne das Startdatum (ungefähr 31 Tage pro Monat)
    start_datum = heute - timedelta(days=monate * 31)

    performance_daten = {}
    protokoll = []

    protokoll.append(f"Starte Momentum-Analyse ({monate} Monate) am {heute.strftime('%Y-%m-%d')}")

    for ticker in etf_liste:
        try:
            # Daten von Yahoo Finance abrufen
            daten = yf.download(ticker, start=start_datum, end=heute, progress=False)
            
            if daten.empty:
                protokoll.append(f"WARNUNG: Keine Daten für {ticker} gefunden.")
                continue

            # Berechnung der Rendite
            if 'Adj Close' in daten.columns:
    schlusskurse = daten['Adj Close']
else:
    schlusskurse = daten['Close']
            start_kurs = schlusskurse.iloc[0]
            end_kurs = schlusskurse.iloc[-1]

            rendite = (end_kurs / start_kurs - 1) * 100
            performance_daten[ticker] = rendite
            
            protokoll.append(f"[{ticker}]: Rendite: {rendite:.2f}%")

        except Exception as e:
            protokoll.append(f"FEHLER beim Abrufen der Daten für {ticker}: {e}")
            continue

    if not performance_daten:
        return "FEHLER: Keine Performance-Daten verfügbar.", protokoll
        
    # Ranking erstellen
    ranking = pd.Series(performance_daten).sort_values(ascending=False)
    return ranking, protokoll


# --- 4. Der Cloud Run Endpunkt (wird vom Scheduler aufgerufen) ---
@app.route("/", methods=["GET"]) # MUSS "/" sein, um den Fehler zu beheben
def momentum_service():
    """Der HTTP-Endpunkt, der bei Aufruf die Logik ausführt."""
    ranking, protokoll = berechne_momentum_ranking(ETF_LISTE, PERFORMANCE_MONATE)
    
    ergebnis_message = ""
    ergebnis_message += "="*50 + "\n"
    ergebnis_message += "🤖 AUTOMATISIERTE KI-KAUFENTSCHEIDUNG 🤖\n"
    ergebnis_message += "="*50 + "\n"
    
    # Protokoll-Zeilen hinzufügen
    for zeile in protokoll:
        ergebnis_message += zeile + "\n"
        
    ergebnis_message += "\n"

    if isinstance(ranking, pd.Series):
        kauf_signale = ranking.head(TOP_N)
        ergebnis_message += f"✅ Kaufsignal (Top {TOP_N} ETFs mit dem höchsten {PERFORMANCE_MONATE}-Monats-Momentum):\n"
        
        for i, (ticker, rendite) in enumerate(kauf_signale.items()):
            ergebnis_message += f"{i+1}. Ticker: {ticker} | Momentum: {rendite:.2f}%\n"
            
        ergebnis_message += "\n=> AKTION ERFORDERLICH (MANUELL): Diese Ticker am Monatsanfang handeln."
    else:
        # Fehlerfall aus der Logik
        ergebnis_message += ranking

    # Das Ergebnis in die Cloud Run Logs schreiben
    print(ergebnis_message)
    
    # Rückgabe des Ergebnisses mit dem HTTP-Statuscode 200 (OK)
    return ergebnis_message, 200

# WICHTIG: Kein if __name__ == "__main__": Block hier, 
# da Gunicorn die App über main:app startet.

