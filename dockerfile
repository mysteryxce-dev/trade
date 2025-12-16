# Basis-Image
FROM python:3.11-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /usr/src/app

# Kopiere die Abhängigkeitsdatei und installiere sie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Hauptcode
COPY main.py .

# Standardmäßige Umgebungsvariable
ENV PORT 8080

# Starte den Webserver mit Gunicorn, der die Funktion 'momentum_service' aus main.py aufruft
CMD exec gunicorn --bind :$PORT --workers 1 main:momentum_service