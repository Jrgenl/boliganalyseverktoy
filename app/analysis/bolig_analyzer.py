"""
Analysemodul for boliganalyse

Denne modulen inneholder algoritmer for å analysere boligdata,
identifisere risikoer og høydepunkter, samt utføre prisanalyse.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
import re
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Last ned nødvendige NLTK-ressurser
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Konfigurer logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importer BoligData og DataProcessor fra data_processor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.data_processor import BoligData, DataProcessor

class BoligAnalyzer:
    """
    Klasse for å analysere boligdata og identifisere risikoer og høydepunkter.
    """
    
    def __init__(self):
        """
        Initialiserer BoligAnalyzer.
        """
        # Definer nøkkelord for risikoer
        self.risiko_nøkkelord = {
            'bad': ['gammelt bad', 'eldre bad', 'oppussingsbehov', 'fuktskade', 'mugg', 'råte', 'lekkasje', 'slitt bad'],
            'kjøkken': ['gammelt kjøkken', 'eldre kjøkken', 'slitt kjøkken', 'oppussingsbehov'],
            'tak': ['taklekkasje', 'gammelt tak', 'eldre tak', 'takstein', 'takplater', 'taktekking'],
            'fukt': ['fuktskade', 'fuktproblemer', 'mugg', 'råte', 'lekkasje', 'vanninntrengning', 'kondens'],
            'elektrisk': ['gammelt elektrisk anlegg', 'eldre elektrisk', 'sikringsskap', 'jordfeil', 'strømfeil'],
            'drenering': ['dårlig drenering', 'fukt i kjeller', 'vanninntrengning', 'fuktig kjeller'],
            'ventilasjon': ['dårlig ventilasjon', 'manglende ventilasjon', 'kondens', 'fuktproblemer'],
            'isolasjon': ['dårlig isolert', 'kald bolig', 'trekk', 'energilekkasje', 'høyt energiforbruk'],
            'skadedyr': ['skadedyr', 'mus', 'rotter', 'insekter', 'maur', 'skjeggkre'],
            'radon': ['radon', 'radonmåling', 'stråling'],
            'støy': ['støy', 'trafikkstøy', 'støyplager', 'lydproblemer'],
            'setningsskader': ['setningsskader', 'sprekker', 'skjevhet', 'setninger'],
            'asbest': ['asbest', 'eternitt', 'asbestplater'],
            'sopp': ['sopp', 'muggsopp', 'råtesopp', 'hussopp'],
            'pcb': ['pcb', 'miljøgifter', 'giftstoffer'],
            'pipe': ['pipe', 'skorstein', 'pipeløp', 'ildsted'],
            'fundamentering': ['fundamentering', 'grunnmur', 'setninger', 'sprekker'],
            'vinduer': ['gamle vinduer', 'eldre vinduer', 'trekkfulle vinduer', 'punkterte vinduer'],
            'parkering': ['parkering', 'garasje', 'parkeringsplass', 'biloppstilling'],
            'fellesgjeld': ['fellesgjeld', 'høy fellesgjeld', 'felleskostnader', 'borettslag']
        }
        
        # Definer nøkkelord for høydepunkter
        self.høydepunkt_nøkkelord = {
            'beliggenhet': ['sentral', 'sentralt', 'nærhet', 'utsikt', 'sjøutsikt', 'fjordutsikt', 'fjell', 'solrik', 'solrikt'],
            'standard': ['høy standard', 'god standard', 'moderne', 'nyoppusset', 'oppgradert', 'renovert'],
            'uteareal': ['hage', 'terrasse', 'balkong', 'uteplass', 'takterrasse', 'veranda', 'altan'],
            'parkering': ['garasje', 'carport', 'parkeringsplass', 'parkering', 'biloppstilling'],
            'kjøkken': ['nytt kjøkken', 'moderne kjøkken', 'integrerte hvitevarer', 'kjøkkenøy', 'flott kjøkken'],
            'bad': ['nytt bad', 'moderne bad', 'flislagt bad', 'varmekabler', 'gulvvarme', 'flott bad'],
            'energi': ['energieffektiv', 'varmepumpe', 'bergvarme', 'solceller', 'lavt energiforbruk'],
            'takhøyde': ['god takhøyde', 'høyt under taket', 'luftig', 'romfølelse'],
            'planløsning': ['god planløsning', 'åpen planløsning', 'funksjonell', 'praktisk', 'gjennomgående'],
            'oppvarming': ['peis', 'vedovn', 'ildsted', 'gulvvarme', 'varmekabler'],
            'fasiliteter': ['heis', 'treningsrom', 'fellesrom', 'gjesterom', 'takterrasse', 'felles takterrasse'],
            'boder': ['bod', 'lagringsplass', 'kjellerbod', 'loftsbod', 'sportsbod'],
            'turområder': ['turområde', 'turmuligheter', 'friluftsliv', 'marka', 'skog', 'sjø', 'strand'],
            'kollektiv': ['kollektivtransport', 'buss', 'trikk', 't-bane', 'tog', 'nærhet til kollektiv'],
            'skole': ['skole', 'barnehage', 'skolekrets', 'nærhet til skole', 'barneskole', 'ungdomsskole'],
            'shopping': ['butikker', 'shopping', 'kjøpesenter', 'nærhet til butikker', 'dagligvare'],
            'nybygg': ['nybygg', 'nyoppført', 'ny bolig', 'nyere bolig', 'byggeår'],
            'utleie': ['utleiedel', 'utleiemulighet', 'hybel', 'separat inngang', 'utleieleilighet'],
            'fiber': ['fiber', 'bredbånd', 'internett', 'høyhastighets internett'],
            'elbil': ['elbillader', 'lademulighet', 'ladestasjon', 'elbil']
        }
        
        # Norske stoppord
        self.norske_stoppord = set(stopwords.words('norwegian'))
    
    def analyze_bolig(self, bolig_data: BoligData) -> BoligData:
        """
        Analyserer boligdata og identifiserer risikoer og høydepunkter.
        
        Args:
            bolig_data: BoligData-objekt som skal analyseres
            
        Returns:
            BoligData-objekt med oppdaterte risikoer og høydepunkter
        """
        try:
            # Identifiser risikoer
            risikoer = self.identifiser_risikoer(bolig_data)
            bolig_data.risikoer = risikoer
            
            # Identifiser høydepunkter
            høydepunkter = self.identifiser_høydepunkter(bolig_data)
            bolig_data.høydepunkter = høydepunkter
            
            logger.info(f"Analyse fullført for {bolig_data.adresse} ({bolig_data.finnkode})")
            logger.info(f"Identifisert {len(risikoer)} risikoer og {len(høydepunkter)} høydepunkter")
            
            return bolig_data
        
        except Exception as e:
            logger.error(f"Feil ved analyse av boligdata: {str(e)}")
            return bolig_data
    
    def identifiser_risikoer(self, bolig_data: BoligData) -> List[Dict[str, str]]:
        """
        Identifiserer potensielle risikoer ved boligen.
        
        Args:
            bolig_data: BoligData-objekt som skal analyseres
            
        Returns:
            Liste med identifiserte risikoer
        """
        risikoer = []
        
        # Kombiner all tekstinformasjon for analyse
        all_text = f"{bolig_data.tittel} {bolig_data.beskrivelse}"
        
        # Sjekk for nøkkelord i teksten
        for kategori, nøkkelord in self.risiko_nøkkelord.items():
            for ord in nøkkelord:
                if ord.lower() in all_text.lower():
                    # Finn konteksten rundt nøkkelordet
                    kontekst = self._finn_kontekst(all_text.lower(), ord.lower())
                    risikoer.append({
                        'kategori': kategori,
                        'nøkkelord': ord,
                        'kontekst': kontekst,
                        'alvorlighetsgrad': self._beregn_alvorlighetsgrad(kategori, kontekst)
                    })
        
        # Sjekk boligens alder
        if bolig_data.alder > 30:
            risikoer.append({
                'kategori': 'alder',
                'nøkkelord': 'eldre bolig',
                'kontekst': f"Boligen er {bolig_data.alder} år gammel",
                'alvorlighetsgrad': 'medium'
            })
        
        # Sjekk for høy fellesgjeld
        if bolig_data.fellesutgifter > 5000:
            risikoer.append({
                'kategori': 'økonomi',
                'nøkkelord': 'høye felleskostnader',
                'kontekst': f"Felleskostnader er {bolig_data.fellesutgifter} kr/mnd",
                'alvorlighetsgrad': 'medium'
            })
        
        # Sjekk for lav etasje
        if bolig_data.etasje == '1' and bolig_data.boligtype == 'Leilighet':
            risikoer.append({
                'kategori': 'beliggenhet',
                'nøkkelord': 'første etasje',
                'kontekst': "Leilighet i første etasje",
                'alvorlighetsgrad': 'lav'
            })
        
        # Fjern duplikater
        unique_risikoer = []
        seen_categories = set()
        for risiko in risikoer:
            if risiko['kategori'] not in seen_categories:
                unique_risikoer.append(risiko)
                seen_categories.add(risiko['kategori'])
        
        return unique_risikoer
    
    def identifiser_høydepunkter(self, bolig_data: BoligData) -> List[Dict[str, str]]:
        """
        Identifiserer høydepunkter ved boligen.
        
        Args:
            bolig_data: BoligData-objekt som skal analyseres
            
        Returns:
            Liste med identifiserte høydepunkter
        """
        høydepunkter = []
        
        # Kombiner all tekstinformasjon for analyse
        all_text = f"{bolig_data.tittel} {bolig_data.beskrivelse}"
        
        # Sjekk for nøkkelord i teksten
        for kategori, nøkkelord in self.høydepunkt_nøkkelord.items():
            for ord in nøkkelord:
                if ord.lower() in all_text.lower():
                    # Finn konteksten rundt nøkkelordet
                    kontekst = self._finn_kontekst(all_text.lower(), ord.lower())
                    høydepunkter.append({
                        'kategori': kategori,
                        'nøkkelord': ord,
                        'kontekst': kontekst
                    })
        
        # Sjekk for nyere bolig
        if 0 < bolig_data.alder <= 5:
            høydepunkter.append({
                'kategori': 'alder',
                'nøkkelord': 'ny bolig',
                'kontekst': f"Boligen er kun {bolig_data.alder} år gammel"
            })
        
        # Sjekk for stort areal
        if bolig_data.boligtype == 'Leilighet' and bolig_data.bruksareal > 100:
            høydepunkter.append({
                'kategori': 'størrelse',
                'nøkkelord': 'stor leilighet',
                'kontekst': f"Leiligheten er på hele {bolig_data.bruksareal} m²"
            })
        
        # Sjekk for mange soverom
        if bolig_data.soverom >= 3:
            høydepunkter.append({
                'kategori': 'soverom',
                'nøkkelord': 'mange soverom',
                'kontekst': f"Boligen har {bolig_data.soverom} soverom"
            })
        
        # Sjekk for fasiliteter
        for fasilitet in bolig_data.fasiliteter:
            for kategori, nøkkelord in self.høydepunkt_nøkkelord.items():
                for ord in nøkkelord:
                    if ord.lower() in fasilitet.lower():
                        høydepunkter.append({
                            'kategori': kategori,
                            'nøkkelord': ord,
                            'kontekst': fasilitet
                        })
        
        # Fjern duplikater
        unique_høydepunkter = []
        seen_categories = set()
        for høydepunkt in høydepunkter:
            if høydepunkt['kategori'] not in seen_categories:
                unique_høydepunkter.append(høydepunkt)
                seen_categories.add(høydepunkt['kategori'])
        
        return unique_høydepunkter
    
    def _finn_kontekst(self, text: str, keyword: str, context_size: int = 100) -> str:
        """
        Finner konteksten rundt et nøkkelord i teksten.
        
        Args:
            text: Teksten som skal analyseres
            keyword: Nøkkelordet som skal finnes
            context_size: Antall tegn før og etter nøkkelordet
            
        Returns:
            Konteksten rundt nøkkelordet
        """
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - context_size)
        end = min(len(text), keyword_pos + len(keyword) + context_size)
        
        context = text[start:end]
        
        # Rens konteksten
        context = re.sub(r'\s+', ' ', context).strip()
        
        return context
    
    def _beregn_alvorlighetsgrad(self, kategori: str, kontekst: str) -> str:
        """
        Beregner alvorlighetsgraden til en risiko.
        
        Args:
            kategori: Risikokategori
            kontekst: Konteksten rundt risikoen
            
        Returns:
            Alvorlighetsgrad ('lav', 'medium', 'høy')
        """
        # Alvorlige kategorier
        høy_alvorlighet = ['fukt', 'sopp', 'asbest', 'pcb', 'radon', 'setningsskader', 'fundamentering']
        
        # Medium alvorlige kategorier
        medium_alvorlighet = ['bad', 'tak', 'elektrisk', 'drenering', 'pipe', 'ventilasjon']
        
        # Sjekk for alvorlige ord i konteksten
        alvorlige_ord = ['omfattende', 'alvorlig', 'store', 'betydelig', 'kritisk', 'umiddelbart', 'farlig']
        for ord in alvorlige_ord:
            if ord in kontekst.lower():
                return 'høy'
        
        # Bestem alvorlighetsgrad basert på kategori
        if kategori in høy_alvorlighet:
            return 'høy'
        elif kategori in medium_alvorlighet:
            return 'medium'
        else:
            return 'lav'
    
    def sammenlign_med_lignende_boliger(self, bolig_data: BoligData, andre_boliger: List[BoligData], 
                                        n_neighbors: int = 5) -> Dict[str, Any]:
        """
        Sammenligner boligen med lignende boliger.
        
        Args:
            bolig_data: BoligData-objekt som skal sammenlignes
            andre_boliger: Liste med andre BoligData-objekter for sammenligning
            n_neighbors: Antall naboer å sammenligne med
            
        Returns:
            Dictionary med sammenligningsresultater
        """
        try:
            if not andre_boliger:
                return {"error": "Ingen andre boliger å sammenligne med"}
            
            # Opprett DataFrame for sammenligning
            data = []
            for bolig in [bolig_data] + andre_boliger:
                data.append({
                    'finnkode': bolig.finnkode,
                    'adresse': bolig.adresse,
                    'prisantydning': bolig.prisantydning,
                    'bruksareal': bolig.bruksareal,
                    'soverom': bolig.soverom,
                    'byggeår': bolig.byggeår if bolig.byggeår > 0 else 2000,  # Default verdi hvis mangler
                    'kvadratmeterpris': bolig.kvadratmeterpris,
                    'boligtype': bolig.boligtype,
                    'postnummer': bolig.postnummer
                })
            
            df = pd.DataFrame(data)
            
            # Filtrer på samme boligtype og område (postnummer)
            if bolig_data.boligtype and bolig_data.postnummer:
                df_filtered = df[(df['boligtype'] == bolig_data.boligtype) & 
                                (df['postnummer'] == bolig_data.postnummer)]
                if len(df_filtered) < n_neighbors + 1:  # +1 for å inkludere boligen selv
                    # Hvis for få treff, filtrer bare på boligtype
                    df_filtered = df[df['boligtype'] == bolig_data.boligtype]
            else:
                df_filtered = df
            
            if len(df_filtered) < 2:
                return {"error": "For få lignende boliger for sammenligning"}
            
            # Velg numeriske kolonner for sammenligning
            numeric_cols = ['bruksareal', 'soverom', 'byggeår', 'prisantydning']
            X = df_filtered[numeric_cols].values
            
            # Normaliser data
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Finn nærmeste naboer
            nbrs = NearestNeighbors(n_neighbors=min(n_neighbors + 1, len(X_scaled)), 
                                   algorithm='auto').fit(X_scaled)
            distances, indices = nbrs.kneighbors(X_scaled[df_filtered['finnkode'] == bolig_data.finnkode].reshape(1, -1))
            
            # Fjern boligen selv fra resultatene
            similar_indices = [idx for idx in indices[0] if df_filtered.iloc[idx]['finnkode'] != bolig_data.finnkode]
            similar_distances = [distances[0][i] for i, idx in enumerate(indices[0]) 
                               if df_filtered.iloc[idx]['finnkode'] != bolig_data.finnkode]
            
            # Hent lignende boliger
            similar_boliger = []
            for i, idx in enumerate(similar_indices):
                similar_bolig = df_filtered.iloc[idx].to_dict()
                similar_bolig['likhet'] = 1 / (1 + similar_distances[i])  # Konverter avstand til likhetsscore
                similar_boliger.append(similar_bolig)
            
            # Beregn gjennomsnittsverdier
            avg_price = np.mean([b['prisantydning'] for b in similar_boliger])
            avg_sqm_price = np.mean([b['kvadratmeterpris'] for b in similar_boliger if b['kvadratmeterpris'] > 0])
            
            # Beregn prisavvik
            price_diff = bolig_data.prisantydning - avg_price
            price_diff_percent = (price_diff / avg_price) * 100 if avg_price > 0 else 0
            
            sqm_price_diff = bolig_data.kvadratmeterpris - avg_sqm_price
            sqm_price_diff_percent = (sqm_price_diff / avg_sqm_price) * 100 if avg_sqm_price > 0 else 0
            
            return {
                'lignende_boliger': similar_boliger,
                'gjennomsnittspris': int(avg_price),
                'gjennomsnitt_kvadratmeterpris': int(avg_sqm_price),
                'prisavvik': int(price_diff),
                'prisavvik_prosent': round(price_diff_percent, 1),
                'kvadratmeterpris_avvik': int(sqm_price_diff),
                'kvadratmeterpris_avvik_prosent': round(sqm_price_diff_percent, 1)
            }
        
        except Exception as e:
            logger.error(f"Feil ved sammenligning av boliger: {str(e)}")
            return {"error": f"Kunne ikke sammenligne boliger: {str(e)}"}
    
    def utfør_prisanalyse(self, bolig_data: BoligData) -> Dict[str, Any]:
        """
        Utfører prisanalyse av boligen.
        
        Args:
            bolig_data: BoligData-objekt som skal analyseres
            
        Returns:
            Dictionary med prisanalyseresultater
        """
        try:
            resultater = {
                'prisantydning': bolig_data.prisantydning,
                'totalpris': bolig_data.totalpris,
                'kvadratmeterpris': bolig_data.kvadratmeterpris,
                'fellesutgifter_årlig': bolig_data.fellesutgifter * 12 if bolig_data.fellesutgifter > 0 else 0
            }
            
            # Sjekk om vi har gyldig prisantydning
            if bolig_data.prisantydning <= 0:
                # Bruk totalpris hvis prisantydning mangler
                base_verdi = bolig_data.totalpris if bolig_data.totalpris > 0 else 3000000  # Standard verdi
            else:
                base_verdi = bolig_data.prisantydning
            
            # Juster for alder
            if bolig_data.alder > 0:
                if bolig_data.alder < 5:
                    # Nyere boliger har ofte høyere verdi
                    alder_faktor = 1.05
                elif bolig_data.alder < 15:
                    alder_faktor = 1.0
                elif bolig_data.alder < 30:
                    alder_faktor = 0.95
                else:
                    alder_faktor = 0.9
            else:
                alder_faktor = 1.0
            
            # Juster for boligtype
            if bolig_data.boligtype == 'Leilighet':
                type_faktor = 1.0
            elif bolig_data.boligtype == 'Enebolig':
                type_faktor = 1.05
            elif bolig_data.boligtype == 'Rekkehus':
                type_faktor = 0.98
            else:
                type_faktor = 1.0
            
            # Juster for antall soverom
            if bolig_data.soverom >= 4:
                soverom_faktor = 1.05
            elif bolig_data.soverom == 3:
                soverom_faktor = 1.02
            elif bolig_data.soverom == 2:
                soverom_faktor = 1.0
            else:
                soverom_faktor = 0.98
            
            # Beregn estimert markedsverdi
            estimert_verdi = base_verdi * alder_faktor * type_faktor * soverom_faktor
            
            resultater['estimert_markedsverdi'] = int(estimert_verdi)
            resultater['verdi_avvik'] = int(estimert_verdi - base_verdi)
            resultater['verdi_avvik_prosent'] = round(((estimert_verdi - base_verdi) / base_verdi) * 100, 1)
            
            # Beregn månedlige kostnader
            rente = 0.04  # 4% rente
            nedbetalingstid = 25  # 25 år
            egenkapital_prosent = 0.15  # 15% egenkapital
            
            lån = bolig_data.totalpris * (1 - egenkapital_prosent) if bolig_data.totalpris > 0 else estimert_verdi * (1 - egenkapital_prosent)
            månedlig_lån = (lån * (rente / 12)) / (1 - (1 + (rente / 12)) ** (-nedbetalingstid * 12))
            
            resultater['månedlig_lånekostnad'] = int(månedlig_lån)
            resultater['månedlig_totalkostnad'] = int(månedlig_lån + bolig_data.fellesutgifter)
            
            return resultater
        
        except Exception as e:
            logger.error(f"Feil ved prisanalyse: {str(e)}")
            return {"error": f"Kunne ikke utføre prisanalyse: {str(e)}"}


# Eksempel på bruk
if __name__ == "__main__":
    import sys
    
    # Last testdata
    test_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "data", "processed_bolig_data.json")
    
    if os.path.exists(test_file):
        # Opprett DataProcessor
        processor = DataProcessor()
        
        # Last boligdata
        bolig = processor.load_from_json(test_file)
        
        if bolig:
            # Opprett BoligAnalyzer
            analyzer = BoligAnalyzer()
            
            # Analyser boligen
            analysert_bolig = analyzer.analyze_bolig(bolig)
            
            # Vis resultater
            print(f"\nAnalyseresultater for {bolig.adresse}:")
            
            print("\nIdentifiserte risikoer:")
            for risiko in analysert_bolig.risikoer:
                print(f"- {risiko['kategori']} ({risiko['alvorlighetsgrad']}): {risiko['nøkkelord']}")
            
            print("\nIdentifiserte høydepunkter:")
            for høydepunkt in analysert_bolig.høydepunkter:
                print(f"- {høydepunkt['kategori']}: {høydepunkt['nøkkelord']}")
            
            # Utfør prisanalyse
            prisanalyse = analyzer.utfør_prisanalyse(bolig)
            
            print("\nPrisanalyse:")
            print(f"Prisantydning: {prisanalyse['prisantydning']} kr")
            print(f"Estimert markedsverdi: {prisanalyse['estimert_markedsverdi']} kr")
            print(f"Avvik: {prisanalyse['verdi_avvik']} kr ({prisanalyse['verdi_avvik_prosent']}%)")
            print(f"Månedlig lånekostnad: {prisanalyse['månedlig_lånekostnad']} kr")
            print(f"Månedlig totalkostnad: {prisanalyse['månedlig_totalkostnad']} kr")
            
            # Lagre analyserte data
            processor.save_to_json(analysert_bolig, "analysert_bolig_data.json")
    else:
        print(f"Testfil ikke funnet: {test_file}")
