"""
Test script for FinnScraper

Dette scriptet tester funksjonaliteten til FinnScraper-klassen.
"""

import sys
import os
import json

# Legg til prosjektmappen i sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.finn_scraper import FinnScraper

def test_scraper():
    """
    Tester FinnScraper med en eksempel-URL.
    """
    print("Tester FinnScraper...")
    
    # Opprett en instans av FinnScraper
    scraper = FinnScraper()
    
    # Test URL
    test_url = "https://www.finn.no/realestate/homes/ad.html?finnkode=398290726"
    
    # Hent boligdata
    print(f"Henter data fra: {test_url}")
    data = scraper.get_bolig_data(test_url)
    
    # Lagre resultatet til en JSON-fil
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "data", "test_bolig_data.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Data lagret til: {output_file}")
    
    # Vis noen nøkkeldata
    print("\nNøkkeldata fra boligannonsen:")
    print(f"Tittel: {data.get('tittel', 'Ikke funnet')}")
    print(f"Adresse: {data.get('adresse', {}).get('full_adresse', 'Ikke funnet')}")
    print(f"Prisantydning: {data.get('pris', {}).get('prisantydning', 'Ikke funnet')} kr")
    print(f"Boligtype: {data.get('boliginfo', {}).get('boligtype', 'Ikke funnet')}")
    print(f"Antall soverom: {data.get('boliginfo', {}).get('soverom', 'Ikke funnet')}")
    
    return data

if __name__ == "__main__":
    test_scraper()
