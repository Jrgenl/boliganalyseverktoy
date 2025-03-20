"""
Databehandlingsmodul for boliganalyse

Denne modulen inneholder funksjonalitet for å behandle og normalisere boligdata
hentet fra finn.no, samt definere datamodeller for boliginformasjon.
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime

# Konfigurer logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BoligData:
    """
    Datamodell for boliginformasjon.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialiserer BoligData med rådata fra scraperen.
        
        Args:
            data: Dictionary med boligdata fra scraperen
        """
        # Håndter tilfeller der data kan være None eller ikke en dictionary
        if data is None:
            data = {}
            
        # Lagre rådata
        self.raw_data = data
        
        # Adresseinformasjon
        if isinstance(data.get('adresse'), dict):
            adresse_data = data.get('adresse', {})
            self.adresse = adresse_data.get('full_adresse', '')
            self.postnummer = adresse_data.get('postnummer', '')
            self.poststed = adresse_data.get('poststed', '')
        else:
            self.adresse = data.get('adresse', '')
            self.postnummer = data.get('postnummer', '')
            self.poststed = data.get('poststed', '')
        
        self.finnkode = data.get('finnkode', '')
        self.url = data.get('url', '')
        self.tittel = data.get('tittel', '')
        
        # Prisinformasjon
        if isinstance(data.get('pris'), dict):
            pris_data = data.get('pris', {})
            self.prisantydning = self._parse_int(pris_data.get('prisantydning', '0'))
            self.totalpris = self._parse_int(pris_data.get('totalpris', '0'))
            self.omkostninger = self._parse_int(pris_data.get('omkostninger', '0'))
            self.fellesutgifter = self._parse_int(pris_data.get('fellesutgifter', '0'))
            self.formuesverdi = self._parse_int(pris_data.get('formuesverdi', '0'))
        else:
            self.prisantydning = self._parse_int(data.get('prisantydning', '0'))
            self.totalpris = self._parse_int(data.get('totalpris', '0'))
            self.omkostninger = self._parse_int(data.get('omkostninger', '0'))
            self.fellesutgifter = self._parse_int(data.get('fellesutgifter', '0'))
            self.formuesverdi = self._parse_int(data.get('formuesverdi', '0'))
        
        # Boliginformasjon
        if isinstance(data.get('boliginfo'), dict):
            bolig_data = data.get('boliginfo', {})
            self.boligtype = bolig_data.get('boligtype', '')
            self.eierform = bolig_data.get('eierform', '')
            self.soverom = self._parse_int(bolig_data.get('soverom', '0'))
            self.primærrom = self._parse_int(bolig_data.get('primærrom', '0'))
            self.bruksareal = self._parse_int(bolig_data.get('bruksareal', '0'))
            self.tomteareal = self._parse_int(bolig_data.get('tomteareal', '0'))
            self.byggeår = self._parse_int(bolig_data.get('byggeår', '0'))
            self.etasje = bolig_data.get('etasje', '')
        else:
            self.boligtype = data.get('boligtype', '')
            self.eierform = data.get('eierform', '')
            self.soverom = self._parse_int(data.get('soverom', '0'))
            self.primærrom = self._parse_int(data.get('primærrom', '0'))
            self.bruksareal = self._parse_int(data.get('bruksareal', '0'))
            self.tomteareal = self._parse_int(data.get('tomteareal', '0'))
            self.byggeår = self._parse_int(data.get('byggeår', '0'))
            self.etasje = data.get('etasje', '')
        
        # Annen informasjon
        self.fasiliteter = data.get('fasiliteter', [])
        self.beskrivelse = data.get('beskrivelse', '')
        self.bilder = data.get('bilder', [])
        
        # Meglerinformasjon
        if isinstance(data.get('megler'), dict):
            megler_data = data.get('megler', {})
            self.megler_navn = megler_data.get('navn', '')
            self.megler_firma = megler_data.get('firma', '')
            self.megler_telefon = megler_data.get('telefon', '')
        else:
            self.megler_navn = data.get('megler_navn', '')
            self.megler_firma = data.get('megler_firma', '')
            self.megler_telefon = data.get('megler_telefon', '')
        
        # Beregnede verdier
        if 'kvadratmeterpris' in data and data['kvadratmeterpris']:
            self.kvadratmeterpris = self._parse_int(data['kvadratmeterpris'])
        else:
            self.kvadratmeterpris = self._beregn_kvadratmeterpris()
            
        if 'alder' in data and data['alder']:
            self.alder = self._parse_int(data['alder'])
        else:
            self.alder = self._beregn_alder()
        
        # Analyserte data (fylles ut av analysemodulen)
        self.risikoer = data.get('risikoer', [])
        self.høydepunkter = data.get('høydepunkter', [])
    
    def _parse_int(self, value: Union[str, int]) -> int:
        """
        Konverterer en streng til heltall.
        
        Args:
            value: Verdi som skal konverteres
            
        Returns:
            Konvertert heltall, eller 0 hvis konvertering feiler
        """
        if isinstance(value, int):
            return value
        
        try:
            if isinstance(value, str) and value.strip():
                # Fjern ikke-numeriske tegn
                clean_value = ''.join(c for c in value if c.isdigit())
                return int(clean_value) if clean_value else 0
            return 0
        except (ValueError, TypeError):
            return 0
    
    def _beregn_kvadratmeterpris(self) -> int:
        """
        Beregner kvadratmeterpris basert på prisantydning og primærrom/bruksareal.
        
        Returns:
            Kvadratmeterpris som heltall
        """
        areal = self.primærrom if self.primærrom > 0 else self.bruksareal
        if areal > 0 and self.prisantydning > 0:
            return int(self.prisantydning / areal)
        return 0
    
    def _beregn_alder(self) -> int:
        """
        Beregner boligens alder basert på byggeår.
        
        Returns:
            Boligens alder i år, eller 0 hvis byggeår mangler
        """
        if self.byggeår > 0:
            current_year = datetime.now().year
            return max(0, current_year - self.byggeår)
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konverterer boligdata til et dictionary.
        
        Returns:
            Dictionary med boligdata
        """
        return {
            'finnkode': self.finnkode,
            'url': self.url,
            'tittel': self.tittel,
            'adresse': self.adresse,
            'postnummer': self.postnummer,
            'poststed': self.poststed,
            'prisantydning': self.prisantydning,
            'totalpris': self.totalpris,
            'omkostninger': self.omkostninger,
            'fellesutgifter': self.fellesutgifter,
            'formuesverdi': self.formuesverdi,
            'boligtype': self.boligtype,
            'eierform': self.eierform,
            'soverom': self.soverom,
            'primærrom': self.primærrom,
            'bruksareal': self.bruksareal,
            'tomteareal': self.tomteareal,
            'byggeår': self.byggeår,
            'etasje': self.etasje,
            'fasiliteter': self.fasiliteter,
            'beskrivelse': self.beskrivelse,
            'bilder': self.bilder,
            'megler_navn': self.megler_navn,
            'megler_firma': self.megler_firma,
            'megler_telefon': self.megler_telefon,
            'kvadratmeterpris': self.kvadratmeterpris,
            'alder': self.alder,
            'risikoer': self.risikoer,
            'høydepunkter': self.høydepunkter
        }


class DataProcessor:
    """
    Klasse for å behandle og normalisere boligdata.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialiserer DataProcessor.
        
        Args:
            data_dir: Mappe for lagring av data
        """
        if data_dir is None:
            # Bruk standardmappe hvis ingen er angitt
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        else:
            self.data_dir = data_dir
        
        # Opprett datamappen hvis den ikke eksisterer
        os.makedirs(self.data_dir, exist_ok=True)
    
    def process_bolig_data(self, raw_data: Dict[str, Any]) -> BoligData:
        """
        Behandler rådata fra scraperen og returnerer et BoligData-objekt.
        
        Args:
            raw_data: Dictionary med boligdata fra scraperen
            
        Returns:
            BoligData-objekt med behandlede data
        """
        try:
            # Opprett BoligData-objekt
            bolig_data = BoligData(raw_data)
            
            # Logg nøkkelinformasjon
            logger.info(f"Behandlet boligdata for {bolig_data.adresse} ({bolig_data.finnkode})")
            logger.info(f"Pris: {bolig_data.prisantydning} kr, Areal: {bolig_data.bruksareal} m², Kvadratmeterpris: {bolig_data.kvadratmeterpris} kr/m²")
            
            return bolig_data
        
        except Exception as e:
            logger.error(f"Feil ved behandling av boligdata: {str(e)}")
            # Returner et tomt BoligData-objekt ved feil
            return BoligData({})
    
    def save_to_json(self, bolig_data: BoligData, filename: str = None) -> str:
        """
        Lagrer boligdata til en JSON-fil.
        
        Args:
            bolig_data: BoligData-objekt som skal lagres
            filename: Filnavn for lagring (valgfritt)
            
        Returns:
            Filsti til den lagrede filen
        """
        try:
            # Generer filnavn basert på finnkode hvis ikke angitt
            if filename is None:
                filename = f"bolig_{bolig_data.finnkode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Fullt filsti
            filepath = os.path.join(self.data_dir, filename)
            
            # Konverter til dictionary og lagre som JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(bolig_data.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Boligdata lagret til {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Feil ved lagring av boligdata: {str(e)}")
            return ""
    
    def load_from_json(self, filepath: str) -> Optional[BoligData]:
        """
        Laster boligdata fra en JSON-fil.
        
        Args:
            filepath: Filsti til JSON-filen
            
        Returns:
            BoligData-objekt, eller None hvis lasting feiler
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Konverter data til dictionary hvis det ikke allerede er det
            if not isinstance(data, dict):
                data = json.loads(data) if isinstance(data, str) else {}
            
            logger.info(f"Boligdata lastet fra {filepath}")
            return BoligData(data)
        
        except Exception as e:
            logger.error(f"Feil ved lasting av boligdata fra {filepath}: {str(e)}")
            return None
    
    def create_dataframe(self, bolig_data_list: List[BoligData]) -> pd.DataFrame:
        """
        Oppretter en pandas DataFrame fra en liste med BoligData-objekter.
        
        Args:
            bolig_data_list: Liste med BoligData-objekter
            
        Returns:
            pandas DataFrame med boligdata
        """
        try:
            # Konverter hver BoligData til dictionary
            data_dicts = [bd.to_dict() for bd in bolig_data_list]
            
            # Opprett DataFrame
            df = pd.DataFrame(data_dicts)
            
            # Fjern kolonner med komplekse datatyper for enklere analyse
            for col in df.columns:
                if isinstance(df[col].iloc[0], (list, dict)) if len(df) > 0 else False:
                    df = df.drop(columns=[col])
            
            logger.info(f"DataFrame opprettet med {len(df)} rader og {len(df.columns)} kolonner")
            return df
        
        except Exception as e:
            logger.error(f"Feil ved opprettelse av DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def save_dataframe_to_csv(self, df: pd.DataFrame, filename: str = "boligdata.csv") -> str:
        """
        Lagrer en DataFrame til en CSV-fil.
        
        Args:
            df: pandas DataFrame som skal lagres
            filename: Filnavn for lagring
            
        Returns:
            Filsti til den lagrede filen
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"DataFrame lagret til {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Feil ved lagring av DataFrame: {str(e)}")
            return ""


# Eksempel på bruk
if __name__ == "__main__":
    # Last testdata
    test_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "data", "test_bolig_data.json")
    
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # Opprett DataProcessor
        processor = DataProcessor()
        
        # Behandle data
        bolig = processor.process_bolig_data(test_data)
        
        # Vis nøkkeldata
        print(f"Adresse: {bolig.adresse}")
        print(f"Pris: {bolig.prisantydning} kr")
        print(f"Areal: {bolig.bruksareal} m²")
        print(f"Kvadratmeterpris: {bolig.kvadratmeterpris} kr/m²")
        print(f"Byggeår: {bolig.byggeår} (Alder: {bolig.alder} år)")
        
        # Lagre behandlede data
        processor.save_to_json(bolig, "processed_bolig_data.json")
    else:
        print(f"Testfil ikke funnet: {test_file}")
