"""
Finn.no Bolig Scraper

Dette modulen inneholder funksjonalitet for å hente boligdata fra finn.no boligannonser.
"""

import re
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Any, Optional, List, Tuple
import json

# Konfigurer logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinnScraper:
    """
    En klasse for å hente boligdata fra finn.no boligannonser.
    """
    
    def __init__(self):
        """
        Initialiserer FinnScraper med standard headers for HTTP-forespørsler.
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'nb-NO,nb;q=0.9,no;q=0.8,en-US;q=0.7,en;q=0.6',
        }
    
    def extract_finn_code(self, url: str) -> Optional[str]:
        """
        Ekstraherer finn-koden fra en finn.no URL.
        
        Args:
            url: URL til finn.no boligannonse
            
        Returns:
            Finn-koden hvis funnet, ellers None
        """
        # Prøv å finne finnkode i URL-parametere
        if 'finnkode=' in url:
            match = re.search(r'finnkode=(\d+)', url)
            if match:
                return match.group(1)
        
        # Prøv å finne finnkode i URL-stien
        match = re.search(r'/(\d+)(?:\?|$)', url)
        if match:
            return match.group(1)
        
        logger.warning(f"Kunne ikke finne finn-kode i URL: {url}")
        return None
    
    def get_bolig_data(self, url: str) -> Dict[str, Any]:
        """
        Henter boligdata fra en finn.no boligannonse.
        
        Args:
            url: URL til finn.no boligannonse
            
        Returns:
            Et dictionary med boligdata
        """
        finn_code = self.extract_finn_code(url)
        if not finn_code:
            logger.error(f"Ugyldig finn.no URL: {url}")
            return {"error": "Ugyldig finn.no URL"}
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Grunnleggende boligdata
            bolig_data = {
                "finnkode": finn_code,
                "url": url,
                "tittel": self._get_title(soup),
                "adresse": self._get_address(soup),
                "pris": self._get_price_info(soup),
                "boliginfo": self._get_property_info(soup),
                "fasiliteter": self._get_facilities(soup),
                "beskrivelse": self._get_description(soup),
                "bilder": self._get_images(soup),
                "megler": self._get_broker_info(soup)
            }
            
            return bolig_data
            
        except requests.RequestException as e:
            logger.error(f"Feil ved henting av data fra {url}: {str(e)}")
            return {"error": f"Kunne ikke hente data: {str(e)}"}
        except Exception as e:
            logger.error(f"Uventet feil ved parsing av {url}: {str(e)}")
            return {"error": f"Feil ved parsing av data: {str(e)}"}
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Henter tittelen på boligannonsen."""
        try:
            title_elem = soup.select_one('h1')
            if title_elem:
                return title_elem.text.strip()
        except Exception as e:
            logger.warning(f"Kunne ikke hente tittel: {str(e)}")
        return ""
    
    def _get_address(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Henter adresseinformasjon."""
        address_info = {"full_adresse": "", "postnummer": "", "poststed": ""}
        try:
            address_elem = soup.select_one('a[href*="maps"]')
            if address_elem:
                full_address = address_elem.text.strip()
                address_info["full_adresse"] = full_address
                
                # Prøv å ekstrahere postnummer og poststed
                match = re.search(r'(\d{4})\s+(\w+)', full_address)
                if match:
                    address_info["postnummer"] = match.group(1)
                    address_info["poststed"] = match.group(2)
        except Exception as e:
            logger.warning(f"Kunne ikke hente adresse: {str(e)}")
        return address_info
    
    def _get_price_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Henter prisinformasjon."""
        price_info = {
            "prisantydning": "",
            "totalpris": "",
            "omkostninger": "",
            "fellesutgifter": "",
            "formuesverdi": ""
        }
        
        try:
            # Prisantydning
            price_elem = soup.select_one('h2.text-28')
            if price_elem:
                price_info["prisantydning"] = self._clean_price(price_elem.text)
            
            # Totalpris
            totalpris_elem = soup.find(string=re.compile('Totalpris'))
            if totalpris_elem and totalpris_elem.find_next():
                price_info["totalpris"] = self._clean_price(totalpris_elem.find_next().text)
            
            # Omkostninger
            omkostninger_elem = soup.find(string=re.compile('Omkostninger'))
            if omkostninger_elem and omkostninger_elem.find_next():
                price_info["omkostninger"] = self._clean_price(omkostninger_elem.find_next().text)
            
            # Fellesutgifter
            fellesutg_elem = soup.find(string=re.compile('Felleskost'))
            if fellesutg_elem and fellesutg_elem.find_next():
                price_info["fellesutgifter"] = self._clean_price(fellesutg_elem.find_next().text)
            
            # Formuesverdi
            formue_elem = soup.find(string=re.compile('Formuesverdi'))
            if formue_elem and formue_elem.find_next():
                price_info["formuesverdi"] = self._clean_price(formue_elem.find_next().text)
        
        except Exception as e:
            logger.warning(f"Kunne ikke hente prisinformasjon: {str(e)}")
        
        return price_info
    
    def _clean_price(self, price_text: str) -> str:
        """Renser prisstreng for ikke-numeriske tegn."""
        if not price_text:
            return ""
        return re.sub(r'[^\d]', '', price_text)
    
    def _get_property_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Henter boliginformasjon."""
        property_info = {
            "boligtype": "",
            "eierform": "",
            "soverom": "",
            "primærrom": "",
            "bruksareal": "",
            "tomteareal": "",
            "byggeår": "",
            "etasje": ""
        }
        
        try:
            # Boligtype
            boligtype_elem = soup.find(string=re.compile('Boligtype'))
            if boligtype_elem and boligtype_elem.find_next():
                property_info["boligtype"] = boligtype_elem.find_next().text.strip()
            
            # Eierform
            eierform_elem = soup.find(string=re.compile('Eieform'))
            if eierform_elem and eierform_elem.find_next():
                property_info["eierform"] = eierform_elem.find_next().text.strip()
            
            # Soverom
            soverom_elem = soup.find(string=re.compile('Soverom'))
            if soverom_elem and soverom_elem.find_next():
                property_info["soverom"] = soverom_elem.find_next().text.strip()
            
            # Primærrom
            prom_elem = soup.find(string=re.compile('Primærrom'))
            if prom_elem and prom_elem.find_next():
                property_info["primærrom"] = self._extract_number(prom_elem.find_next().text)
            
            # Bruksareal
            bra_elem = soup.find(string=re.compile('Bruksareal'))
            if bra_elem and bra_elem.find_next():
                property_info["bruksareal"] = self._extract_number(bra_elem.find_next().text)
            
            # Tomteareal
            tomt_elem = soup.find(string=re.compile('Tomteareal'))
            if tomt_elem and tomt_elem.find_next():
                property_info["tomteareal"] = self._extract_number(tomt_elem.find_next().text)
            
            # Byggeår
            byggeår_elem = soup.find(string=re.compile('Byggeår'))
            if byggeår_elem and byggeår_elem.find_next():
                property_info["byggeår"] = byggeår_elem.find_next().text.strip()
            
            # Etasje
            etasje_elem = soup.find(string=re.compile('Etasje'))
            if etasje_elem and etasje_elem.find_next():
                property_info["etasje"] = etasje_elem.find_next().text.strip()
            
        except Exception as e:
            logger.warning(f"Kunne ikke hente boliginformasjon: {str(e)}")
        
        return property_info
    
    def _extract_number(self, text: str) -> str:
        """Ekstraherer tall fra tekst."""
        if not text:
            return ""
        match = re.search(r'(\d+)', text)
        return match.group(1) if match else ""
    
    def _get_facilities(self, soup: BeautifulSoup) -> List[str]:
        """Henter fasiliteter."""
        facilities = []
        try:
            facility_section = soup.find(string=re.compile('Fasiliteter'))
            if facility_section and facility_section.find_parent():
                facility_items = facility_section.find_parent().find_next_siblings('div')
                for item in facility_items:
                    if item.text.strip():
                        facilities.append(item.text.strip())
        except Exception as e:
            logger.warning(f"Kunne ikke hente fasiliteter: {str(e)}")
        return facilities
    
    def _get_description(self, soup: BeautifulSoup) -> str:
        """Henter boligbeskrivelse."""
        try:
            description_section = soup.find(string=re.compile('Om boligen'))
            if description_section and description_section.find_parent():
                description_div = description_section.find_parent().find_next_sibling('div')
                if description_div:
                    return description_div.text.strip()
        except Exception as e:
            logger.warning(f"Kunne ikke hente beskrivelse: {str(e)}")
        return ""
    
    def _get_images(self, soup: BeautifulSoup) -> List[str]:
        """Henter bildelenker."""
        images = []
        try:
            # Finn bildelenker i JSON-data
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'images' in data:
                        for img in data['images']:
                            if 'url' in img:
                                images.append(img['url'])
                except (json.JSONDecodeError, AttributeError):
                    continue
            
            # Alternativ metode: finn img-tagger
            if not images:
                img_tags = soup.select('img[src*="bilde"]')
                for img in img_tags:
                    if 'src' in img.attrs:
                        images.append(img['src'])
        except Exception as e:
            logger.warning(f"Kunne ikke hente bilder: {str(e)}")
        return images
    
    def _get_broker_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Henter meglerinformasjon."""
        broker_info = {"navn": "", "firma": "", "telefon": ""}
        try:
            # Meglernavn
            broker_name = soup.select_one('div.broker-name')
            if broker_name:
                broker_info["navn"] = broker_name.text.strip()
            
            # Meglerfirma
            broker_firm = soup.select_one('div.broker-company')
            if broker_firm:
                broker_info["firma"] = broker_firm.text.strip()
            
            # Telefonnummer
            phone_elem = soup.select_one('a[href^="tel:"]')
            if phone_elem:
                broker_info["telefon"] = phone_elem.text.strip()
        except Exception as e:
            logger.warning(f"Kunne ikke hente meglerinformasjon: {str(e)}")
        return broker_info


# Eksempel på bruk
if __name__ == "__main__":
    scraper = FinnScraper()
    # Test med en eksempel-URL
    test_url = "https://www.finn.no/realestate/homes/ad.html?finnkode=398290726"
    data = scraper.get_bolig_data(test_url)
    print(json.dumps(data, indent=2, ensure_ascii=False))
