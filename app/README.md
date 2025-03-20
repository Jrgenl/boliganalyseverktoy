# Boliganalyseverktøy - Web Deployment

Dette repositoriet inneholder koden for Boliganalyseverktøyet, en webapplikasjon som analyserer boligannonser fra Finn.no.

## Funksjonalitet

Boliganalyseverktøyet gir deg mulighet til å:

- Analysere boligannonser fra Finn.no ved å lime inn URL-en
- Identifisere potensielle risikoer ved boligen
- Fremheve positive aspekter ved boligen
- Utføre prisanalyse og estimere markedsverdi
- Beregne månedlige kostnader

## Teknisk Oversikt

Applikasjonen er bygget med følgende teknologier:

- **Python 3.10**: Programmeringsspråket
- **Streamlit**: Rammeverk for brukergrensesnitt
- **BeautifulSoup4**: For web scraping av Finn.no
- **Pandas & NumPy**: For databehandling og analyse
- **scikit-learn**: For maskinlæring og analyse
- **Docker**: For containerisering og enkel distribusjon

## Struktur

Prosjektet er organisert i følgende mapper:

- `scraper/`: Inneholder kode for å hente data fra Finn.no
- `analysis/`: Inneholder kode for databehandling og analyse
- `ui/`: Inneholder Streamlit-applikasjonen og brukergrensesnitt
- `data/`: Lagrer data og cache
- `utils/`: Hjelpefunksjoner
- `docs/`: Dokumentasjon
- `tests/`: Tester

## Installasjon og Kjøring

### Lokal Kjøring

1. Klone repositoriet:
   ```
   git clone https://github.com/username/boliganalyseverktoy.git
   cd boliganalyseverktoy
   ```

2. Installer avhengigheter:
   ```
   pip install -r requirements.txt
   ```

3. Start applikasjonen:
   ```
   streamlit run ui/web_app.py
   ```

### Docker

1. Bygg Docker-image:
   ```
   docker-compose build
   ```

2. Kjør containeren:
   ```
   docker-compose up
   ```

3. Åpne nettleseren på `http://localhost:8501`

## Distribusjon

For permanent distribusjon bruker vi Streamlit Cloud. Se `docs/streamlit_cloud_deployment.md` for detaljerte instruksjoner om hvordan du distribuerer applikasjonen.

## Utvikling

For å bidra til prosjektet:

1. Fork repositoriet
2. Opprett en ny branch for din funksjonalitet
3. Implementer endringene
4. Send en pull request

## Lisens

Dette prosjektet er lisensiert under MIT-lisensen - se LICENSE-filen for detaljer.

## Kontakt

For spørsmål eller tilbakemeldinger, vennligst opprett et issue i dette repositoriet.
