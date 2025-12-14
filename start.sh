#!/bin/bash

# Attiva il virtual environment
source venv/bin/activate

# Imposta la chiave OpenAI (sostituisci con la tua)
export OPENAI_API_KEY="la_tua_chiave_openai"

# Avvia ngrok in background e salva log
nohup ngrok http 5000 > ngrok.log 2>&1 &

# Attendi 2 secondi e mostra l'URL pubblico
sleep 2
echo "URL pubblico ngrok (da usare in Twilio):"
grep -o "https://[a-z0-9]*\.ngrok-free\.app" ngrok.log

# Avvia Flask
python3 app.py
