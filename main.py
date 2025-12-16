import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

# --- 1. Strategie-Parameter ---
# Ticker für globale ETFs (passen Sie diese bei Bedarf an)
# Stellen Sie sicher, dass diese Ticker auf Ihrer Handelsplattform verfügbar sind.
ETF_LISTE = ['VWCE.DE', 'ISIN.DE', 'SWRD.DE', 'EMIM.DE'] 
PERFORMANCE_MONATE = 3 # Momentum-Periode
TOP_N = 3 # Anzahl der besten ETFs, die gekauft werden sollen

def berechne_momentum_ranking(etf_liste, monate):
    """
    Berechnet die prozentuale Rendite der ETFs über N Monate.
    """
    heute = datetime.now()
    # Wir ziehen etwas mehr als N Monate ab, um sicher Daten zu erhalten
    start_datum = heute - timedelta(days=monate * 31)

    performance_daten = {}
    protokoll = []

    protokoll.append(f"Starte Momentum-Analyse ({monate} Monate) am {heute.strftime('%Y-%m-%d')}")

    for ticker in etf_liste:
        try:
            # Daten abrufen
            daten = yf.download(ticker, start=start_datum, end=heute, progress=False)

            if daten.empty:
                protokoll.append(f"WARNUNG: Keine Daten für {ticker} gefunden.")
                continue

            # Performance berechnen
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

# --- Hauptfunktion für Cloud Run ---
def momentum_service(request):
    """
    Cloud Run erwartet eine Hauptfunktion, die eine Anfrage entgegennimmt.
    """
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

    print(ergebnis_message) # Wichtig für die Cloud Run Logs

    # Cloud Run benötigt eine HTTP-Antwort
    return ergebnis_message, 200

if __name__ == "__main__":
    # Lokaler Test
    print(momentum_service(None)[0])