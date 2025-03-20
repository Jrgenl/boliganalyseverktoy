# Analyse av visning.ai funksjonalitet

## Hovedfunksjonalitet
1. **Input-metode**: Brukere kan lime inn en Finn-kode eller Finn-lenke for å analysere en bolig
2. **Risikoanalyse**: Identifiserer potensielle risikoer ved boligen basert på annonsetekst og tilstandsrapport
3. **Høydepunkter**: Fremhever positive aspekter ved boligen
4. **Detaljert informasjon**: Viser detaljert informasjon om boligen (pris, omkostninger, formuesverdi, etc.)
5. **Kategorisering**: Organiserer risikoer og høydepunkter i kategorier med ikoner

## Datakilder
- Henter data fra finn.no boligannonser
- Analyserer tekst og informasjon fra annonsen
- Bruker AI for å identifisere risikoer og høydepunkter

## Presentasjon av data
- Risikoer presenteres med ikoner og korte beskrivelser
- Høydepunkter presenteres med ikoner og korte beskrivelser
- Detaljert informasjon om boligen presenteres i en oversiktlig visning
- Mulighet for å se mer detaljert informasjon om hver risiko

## Finn.no API
- Finn.no tilbyr et API for å hente boligdata
- API-et er basert på REST-prinsipper
- Boligdata kan hentes via to hovedressurser:
  1. **Search API**: For å søke etter boligannonser
  2. **Ad API**: For å hente detaljert informasjon om en spesifikk annonse
- Data returneres i Atom-format med utvidelser
- Tilgang til API-et krever autentisering

## Implementasjonsstrategi
1. Bruke web scraping for å hente data fra finn.no siden API-et krever autentisering
2. Fokusere på å hente data fra spesifikke finn.no boligannonser via URL
3. Analysere tekst og data for å identifisere risikoer og høydepunkter
4. Presentere data i et brukergrensesnitt som ligner på visning.ai
5. Implementere AI-analyse for å identifisere risikoer og høydepunkter basert på annonsetekst
