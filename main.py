import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from flask import Flask, request # NEU: Flask importiert

# --- 1. Strategie-Parameter ---
ETF_LISTE = ['VWCE.DE', 'ISIN.DE', 'SWRD.DE', 'EMIM.DE'] 
PERFORMANCE_MONATE = 3 
TOP_N = 3

# Die Hauptlogik bleibt unverändert
def berechne_momentum_ranking(etf_liste, monate):
    # ... (Ihr bisheriger Code zur Berechnung des Rankings hier unverändert einfügen) ...
    # Behalten Sie die return-Werte bei: return ranking, protokoll
    # ******************************************************************************
    heute = datetime.now()
    start_datum = heute - timedelta(days=monate * 31)

    performance_daten = {}
    protokoll = []

    protokoll.append(f"Starte Momentum-Analyse ({monate} Monate) am {heute.strftime('%Y-%m-%d')}")

    for ticker in etf_liste:
        try:
            daten = yf.download(ticker, start=start_datum, end=heute, progress=False)
            if daten.empty:
                protokoll.append(f"WARNUNG: Keine Daten für {ticker} gefunden.")
                continue

            schlusskurse = daten['Adj Close']
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
        
    ranking = pd.Series(performance_daten).sort_values(ascending=False)
    return ranking, protokoll
    # ******************************************************************************


# --- 2. Flask-Anwendung erstellen und Logik einbetten ---
app = Flask(__name__) # Flask-App-Instanz erstellen

@app.route("/", methods=["GET"]) # Definiere den Endpunkt, den Gunicorn aufrufen soll
def momentum_service():
    ranking, protokoll = berechne_momentum_ranking(ETF_LISTE, PERFORMANCE_MONATE)
    
    ergebnis_message = ""
    ergebnis_message += "="*50 + "\n"
    ergebnis_message += "🤖 AUTOMATISIERTE KI-KAUFENTSCHEIDUNG 🤖\n"
    ergebnis_message += "="*50 + "\n"
    
    for zeile in protokoll:
        ergebnis_message += zeile + "\n"
        
    ergebnis_message += "\n"

    if isinstance(ranking, pd.Series):
        kauf_signale = ranking.head(TOP_N)
        ergebnis_message += f"✅ Kaufsignal (Top {TOP_N} ETFs mit dem höchsten {PERFORMANCE_MONATE}-Monats-Momentum):\n"
        
        for i, (ticker, rendite) in enumerate(kauf_signale.items()):
            ergebnis_message += f"{i+1}. Ticker: {ticker} | Momentum: {rendite:.2f}%\n"
            
        ergebnis_message += "\n=> AKTION ERFORDERLICH (MANUELL): Diese Ticker am Monatsanfang auf eToro handeln."
    else:
        ergebnis_message += ranking

    print(ergebnis_message)
    
    # Rückgabe des Ergebnisses (im Header 200)
    return ergebnis_message, 200

# Entfernen Sie den if __name__ == "__main__": Block, da Gunicorn die App startet.
