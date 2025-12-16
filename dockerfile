# Basis-Image
FROM python:3.11-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /usr/src/app

# Kopiere die Abhängigkeitsdatei und installiere sie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Hauptcode
COPY main.py .

# Wir definieren den PORT, den Cloud Run erwartet
ENV PORT 8080

# WICHTIG: Korrigierter Startbefehl
# main:app weist Gunicorn an, die Instanz 'app' in main.py zu finden
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app

