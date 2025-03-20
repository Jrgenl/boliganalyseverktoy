"""
Test script for BoligAnalyzer

Dette scriptet tester funksjonaliteten til BoligAnalyzer-klassen.
"""

import sys
import os
import json

# Legg til prosjektmappen i sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.data_processor import DataProcessor
from analysis.bolig_analyzer import BoligAnalyzer

def test_analyzer():
    """
    Tester BoligAnalyzer med testdata.
    """
    print("Tester BoligAnalyzer...")
    
    # Last testdata
    test_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "data", "processed_bolig_data.json")
    
    if not os.path.exists(test_file):
        print(f"Testfil ikke funnet: {test_file}")
        return
    
    # Opprett DataProcessor
    processor = DataProcessor()
    
    # Last boligdata
    bolig = processor.load_from_json(test_file)
    
    if not bolig:
        print("Kunne ikke laste boligdata")
        return
    
    # Opprett BoligAnalyzer
    analyzer = BoligAnalyzer()
    
    # Analyser boligen
    print("\nAnalyserer boligdata...")
    analysert_bolig = analyzer.analyze_bolig(bolig)
    
    # Vis resultater
    print(f"\nAnalyseresultater for {bolig.adresse if bolig.adresse else bolig.finnkode}:")
    
    print("\nIdentifiserte risikoer:")
    if analysert_bolig.risikoer:
        for risiko in analysert_bolig.risikoer:
            print(f"- {risiko['kategori']} ({risiko['alvorlighetsgrad']}): {risiko['nøkkelord']}")
    else:
        print("Ingen risikoer identifisert")
    
    print("\nIdentifiserte høydepunkter:")
    if analysert_bolig.høydepunkter:
        for høydepunkt in analysert_bolig.høydepunkter:
            print(f"- {høydepunkt['kategori']}: {høydepunkt['nøkkelord']}")
    else:
        print("Ingen høydepunkter identifisert")
    
    # Utfør prisanalyse
    print("\nUtfører prisanalyse...")
    prisanalyse = analyzer.utfør_prisanalyse(bolig)
    
    print("\nPrisanalyse:")
    print(f"Prisantydning: {prisanalyse.get('prisantydning', 'Ikke tilgjengelig')} kr")
    print(f"Estimert markedsverdi: {prisanalyse.get('estimert_markedsverdi', 'Ikke tilgjengelig')} kr")
    print(f"Avvik: {prisanalyse.get('verdi_avvik', 'Ikke tilgjengelig')} kr ({prisanalyse.get('verdi_avvik_prosent', 'Ikke tilgjengelig')}%)")
    print(f"Månedlig lånekostnad: {prisanalyse.get('månedlig_lånekostnad', 'Ikke tilgjengelig')} kr")
    print(f"Månedlig totalkostnad: {prisanalyse.get('månedlig_totalkostnad', 'Ikke tilgjengelig')} kr")
    
    # Lagre analyserte data
    output_file = processor.save_to_json(analysert_bolig, "analysert_bolig_data.json")
    print(f"\nAnalyserte data lagret til: {output_file}")
    
    return analysert_bolig

if __name__ == "__main__":
    test_analyzer()
