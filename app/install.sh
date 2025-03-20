#!/bin/bash

# Installasjonsskript for Boliganalyseverktøy
# Dette skriptet installerer alle nødvendige avhengigheter og setter opp miljøet

echo "Installerer Boliganalyseverktøy..."
echo "=================================="

# Sjekk om Python er installert
if ! command -v python3 &> /dev/null; then
    echo "Python 3 er ikke installert. Installerer..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
else
    echo "Python 3 er allerede installert."
fi

# Opprett virtuelt miljø
echo "Oppretter virtuelt miljø..."
python3 -m venv boliganalyse_env
source boliganalyse_env/bin/activate

# Installer avhengigheter
echo "Installerer avhengigheter..."
pip install -r requirements.txt

echo ""
echo "Installasjon fullført!"
echo "For å starte applikasjonen, kjør:"
echo "source boliganalyse_env/bin/activate"
echo "streamlit run ui/app.py"
echo ""
echo "Åpne deretter nettleseren på http://localhost:8501"
