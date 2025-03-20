"""
Konfigurasjonsmodul for web-applikasjonen

Denne modulen inneholder konfigurasjonsvariabler og innstillinger for web-applikasjonen.
"""

import os

# Applikasjonsnavn
APP_NAME = "Boliganalyseverktøy"

# Versjon
APP_VERSION = "1.0.0"

# Cache-innstillinger
CACHE_TTL = 3600  # Cache-levetid i sekunder (1 time)

# Finn.no API-begrensninger
MAX_REQUESTS_PER_MINUTE = 10  # Maksimalt antall forespørsler per minutt

# Logginnstillinger
LOG_LEVEL = "INFO"

# Filbaner
DATA_DIR = "data"
CACHE_DIR = os.path.join(DATA_DIR, "cache")

# Sikre at nødvendige mapper eksisterer
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Web-spesifikke innstillinger
ENABLE_ANALYTICS = False  # Deaktiver analytics som standard
ENABLE_SHARING = True  # Aktiver deling av analyseresultater
MAX_HISTORY_ITEMS = 5  # Maksimalt antall historikkelementer å vise

# Standardverdier for prisanalyse
DEFAULT_INTEREST_RATE = 0.04  # 4% rente
DEFAULT_LOAN_YEARS = 25  # 25 års nedbetalingstid
DEFAULT_EQUITY_PERCENT = 0.15  # 15% egenkapital
