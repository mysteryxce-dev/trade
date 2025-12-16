# Verwenden Sie ein schlankes Python-Basis-Image
FROM python:3.11-slim

# Setzen Sie das Arbeitsverzeichnis
WORKDIR /usr/src/app

# Kopieren und Installieren der Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren Sie den Hauptcode
COPY main.py .

# WICHTIG: Kein explizites ENV PORT 8080 mehr, da Cloud Run es injiziert.
# Wir setzen nur den Gunicorn-Befehl:
# CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app

# Letzter Versuch: Hardcodierte Bindung, um die Umgebungsvariable auszuschließen, 
# falls es ein Problem mit der Cloud Run Injektion gibt.
ENV PORT 8080
# ÄNDERUNG: Bindung direkt an den erforderlichen Port 8080
CMD gunicorn -w 1 -b 0.0.0.0:$PORT main:app

