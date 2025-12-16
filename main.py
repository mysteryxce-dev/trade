import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from flask import Flask, request 

# --- 1. Strategie-Parameter ---
# Extrem zuverlässige, US-Markt-ETFs, die mit yfinance stabil funktionieren.
ETF_LISTE = ['QQQ', 'SPY', 'IWM', 'AGG'] 
PERFORMANCE_MONATE = 3 
TOP_N = 3

# --- 2. Flask-Anwendung erstellen ---
app = Flask(__name__) 

# --- 3. Hauptlogik zur Berechnung des Momentums ---
def berechne_momentum_ranking(etf_liste, monate):
    """Führt die Momentum-Berechnung für eine Liste von Tickersymbolen durch."""
    
    # Setze das Enddatum auf gestern, um unvollständige Daten des aktuellen Tages zu vermeiden
    heute = datetime.now().date()
    end_datum = heute - timedelta(days=1)
    
    # Berechne das Startdatum (ungefähr 31 Tage pro Monat)
    start_datum = heute - timedelta(days=monate * 31)

    performance_daten = {}
    protokoll = []

    protokoll.append(f"Starte Momentum-Analyse ({monate} Monate) am {heute.strftime('%Y-%m-%d')}")

    for ticker in etf_liste:
        try:
            # Daten von Yahoo Finance abrufen
            # Beachte: Der Endpunkt ist jetzt 'end_datum' (gestern)
            daten = yf.download(ticker, start=start_datum, end=end_datum, progress=False)
            
            if daten.empty:
                protokoll.append(f"WARNUNG: Keine Daten für {ticker} gefunden (Zeitraum: {start_datum} bis {end_datum}).")
                continue

            # LOGIK ZUR BEHEBUNG DES 'Adj Close' FEHLERS:
            if 'Adj Close' in daten.columns:
                schlusskurse = daten['Adj Close']
            elif 'Close' in daten.columns:
                schlusskurse = daten['Close']
            else:
                protokoll.append(f"FEHLER: Ticker {ticker} enthält weder 'Adj Close' noch 'Close' Spalten.")
                continue

            # --- FINALE KORREKTUR: NaN-Werte entfernen und gültige Kurse extrahieren ---
            
            # 1. Entferne NaN-Werte aus der Serie (sehr wichtig für den ersten/letzten Tag!)
            schlusskurse_clean = schlusskurse.dropna()
            
            if len(schlusskurse_clean) < 2:
                protokoll.append(f"WARNUNG: Nicht genug gültige Datenpunkte für {ticker} ({len(schlusskurse_clean)}).")
                continue
            
            # 2. Extrahiere den ERSTEN gültigen und den LETZTEN gültigen Kurs
            start_kurs = schlusskurse_clean.iloc[0]
            end_kurs = schlusskurse_clean.iloc[-1]
            
            # Fehlerbehandlung, falls Kurse wider Erwarten immer noch nicht numerisch sind
            if not isinstance(start_kurs, (int, float)) or not isinstance(end_kurs, (int, float)):
                 protokoll.append(f"WARNUNG: Nach der Bereinigung ist Start- oder Endkurs für {ticker} kein gültiger Wert.")
                 continue

            rendite = (end_kurs / start_kurs - 1) * 100
            
            # Stellen Sie sicher, dass die Rendite nicht NaN ist, bevor Sie sie speichern
            if pd.notna(rendite):
                performance_daten[ticker] = rendite
                protokoll.append(f"[{ticker}]: Rendite: {rendite:.2f}%")
            else:
                protokoll.append(f"WARNUNG: Rendite für {ticker} ist ungültig (NaN).")
                
        except Exception as e:
            protokoll.append(f"KRITISCHER FEHLER beim Abrufen/Berechnen für {ticker}: {e}")
            continue

    if not performance_daten:
        return "FEHLER: Keine Performance-Daten verfügbar, da alle Ticker fehlgeschlagen sind.", protokoll
        
    # Ranking erstellen
    ranking = pd.Series(performance_daten).sort_values(ascending=False)
    return ranking, protokoll


# --- 4. Der Cloud Run Endpunkt (Web-Service) ---
@app.route("/", methods=["GET"]) 
def momentum_service():
    """Der HTTP-Endpunkt, der bei Aufruf die Logik ausführt."""
    
    # Stellen Sie sicher, dass der Bot nur einmal pro Aufruf die Daten abruft
    ranking, protokoll = berechne_momentum_ranking(ETF_LISTE, PERFORMANCE_MONATE)
    
    ergebnis_message = "="*50 + "\n"
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

    # Protokollierung an die Cloud Logging Konsole
    print(ergebnis_message) 
    
    # Rückgabe des Ergebnisses an den Cloud Run Aufrufer
    return ergebnis_message, 200

# Dies ist der Cloud Run / Gunicorn Startpunkt, muss nicht geändert werden
# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
