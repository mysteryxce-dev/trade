# 1. Basis-Image festlegen
# Verwenden Sie ein schlankes Python-Basis-Image für geringere Größe
FROM python:3.11-slim

# 2. Arbeitsverzeichnis setzen
WORKDIR /usr/src/app

# 3. Abhängigkeiten kopieren und installieren
# Zuerst requirements.txt kopieren
COPY requirements.txt .

# Pakete installieren (Pandas, yfinance, gunicorn, Flask)
RUN pip install --no-cache-dir -r requirements.txt

# 4. Hauptcode kopieren
# main.py in das Arbeitsverzeichnis kopieren
COPY main.py .

# 5. Startbefehl (Der kritischste Teil)
# Cloud Run injiziert automatisch die Umgebungsvariable $PORT=8080.
# Wir verwenden das robuste Shell-Format (nicht das JSON-Array-Format).
# 'gunicorn -w 1': Eine Worker-Instanz starten.
# '-b 0.0.0.0:$PORT': An alle Adressen auf dem erwarteten Port binden (löst 404/Bindungsfehler).
# 'main:app': Startet die Flask-Instanz 'app' aus der Datei 'main.py'.
CMD gunicorn -w 1 -b 0.0.0.0:$PORT main:app
