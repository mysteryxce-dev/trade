# Verwenden Sie ein schlankes Python-Basis-Image
FROM python:3.11-slim

# Setzen Sie das Arbeitsverzeichnis im Container
WORKDIR /usr/src/app

# Kopieren Sie die Datei mit den Abhängigkeiten
COPY requirements.txt .

# Installieren Sie die Python-Abhängigkeiten
# --no-cache-dir reduziert die Image-Größe
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren Sie den Hauptcode (main.py)
COPY main.py .

# Exponieren Sie den Port (Dies ist hauptsächlich dokumentarisch, aber gängige Praxis)
# Cloud Run injiziert die Umgebungsvariable PORT=8080 automatisch
ENV PORT 8080

# Der finale Startbefehl für Gunicorn
# 'exec' stellt sicher, dass das Signal korrekt an Gunicorn weitergeleitet wird
# '--bind 0.0.0.0:$PORT' sorgt dafür, dass Gunicorn auf alle eingehenden Verbindungen auf dem Cloud Run Port lauscht (behebt oft 404/Bindungsfehler)
# 'main:app' weist Gunicorn an, die Flask-Instanz 'app' in der Datei 'main.py' zu starten
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app
